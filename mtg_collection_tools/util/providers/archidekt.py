import csv
from pathlib import Path
from typing import Any, override
from urllib.parse import urljoin

import ijson
import requests
from langchain.tools import tool
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from urllib3.connection import _get_default_user_agent

from mtg_collection_tools.util import scryfall
from mtg_collection_tools.util.common import logging
from mtg_collection_tools.util.common.constants import get_data_path
from mtg_collection_tools.util.models.config import CollectionProvider
from mtg_collection_tools.util.models.mtg import Card, Deck
from mtg_collection_tools.util.providers.base import BaseProvider


class ArchidektProvider(BaseProvider):
    base_url = "https://archidekt.com/api"
    provider_name = "archidekt"

    @override
    def test_connection(self):
        response = requests.get(f"{self.base_url}/users/{self.collection_id}/")

        response.raise_for_status()

    @override
    def download_collection(self):
        target_path = self.data_path / "collection.csv"

        # Make sure the data directory is set up
        if not self.data_path.exists():
            self.data_path.mkdir(parents=True, exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            _ = progress.add_task(
                description="Grabbing collection metadata...", total=None
            )

            # Get the card count of the collection for iteration purposes
            resp = requests.get(url=f"{self.base_url}/collection/{self.collection_id}/")
            resp.raise_for_status()
            card_count = int(resp.json().get("count"))

        print(f"Downloading collection of '{card_count}' cards to '{target_path}'")

        with Progress(
            TextColumn(text_format="{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        ) as progress:
            # Iterate through entire collection in chunks of PAGE_SIZE and build a csv from it
            PAGE_SIZE = 2500
            GAME = 1

            page = 1
            is_more_content = True

            task = progress.add_task("Records Downloaded:", total=card_count)

            with open(target_path, "w") as f:
                while is_more_content:
                    resp = requests.post(
                        url=f"{self.base_url}/collection/export/v2/{self.collection_id}/",
                        json={
                            "fields": [
                                "card__oracleCard__name",
                                "card__edition__editioncode",
                                "card__uid",
                                "card__collectorNumber",
                            ],
                            "page": page,
                            "game": 1,
                            "pageSize": PAGE_SIZE,
                        },
                    )
                    resp.raise_for_status()

                    # write the content field to file, and check if there is more content
                    chunk_json = resp.json()
                    chunk_data = str(chunk_json.get("content"))
                    f.write(chunk_data)
                    is_more_content = chunk_json.get("moreContent", False)

                    page += 1
                    progress.advance(task_id=task, advance=chunk_data.count("\n"))

        print(f"{card_count} records successfully downloaded to '{target_path}'")

    @staticmethod
    def map_card_json_to_model(card_json: dict[str, Any]) -> Card:
        """Maps the JSON response from Archidekt to the Card model."""
        def build_type_line(oracle_card: dict[str, Any]) -> str:
            """Builds the type line from the card JSON."""
            types = oracle_card.get("types",[])
            subtypes = oracle_card.get("subTypes", [])
            supertypes = oracle_card.get("superTypes", [])

            type_part    = " ".join(supertypes + types)          # super & main types
            subtype_part = " ".join(subtypes)                    # sub-types

            if subtype_part:
                #  both parts → “Types - Subtypes”
                return f"{type_part} - {subtype_part}" if type_part else subtype_part
            else:
                #  no subtypes → just the type section
                return type_part

        oracle_card: dict[str, Any] = card_json.get("card").get("oracleCard")

        # Extract the relevant fields from the JSON response
        card_data = {
            "id": oracle_card.get("uid"),
            "name": oracle_card.get("name"),
            "mana_cost": oracle_card.get("manaCost"),
            "cmc": oracle_card.get("cmc"),
            "type_line": build_type_line(oracle_card),
            "oracle_text": oracle_card.get("text"),
            "power": oracle_card.get("power"),
            "toughness": oracle_card.get("toughness"),
            "loyalty": oracle_card.get("loyalty"),
            "colors": oracle_card.get("colors"),
            "color_identity": oracle_card.get("colorIdentity"),
            "commander_legality": oracle_card.get("legalities").get("commander"),
            "game_changer": oracle_card.get("gameChanger"),
            "edhrec_rank": oracle_card.get("edhrecRank"),
            "price": str(card_json.get("card").get("prices").get("tcg")),
        }

        # Create a Card instance using the extracted data
        return Card.model_validate(card_data)

    @override
    def annotate_collection(self):
        collection_path = self.data_path / "collection.csv"
        scryfall_path = get_data_path() / "scryfall" / "oracle_cards.json"
        output_path = Path.cwd() / "annotated_collection.csv"

        fields_to_extract = [
            "id",
            "name",
            "mana_cost",
            "cmc",
            "type_line",
            "oracle_text",
            "power",
            "toughness",
            "loyalty",
            "colors",
            "color_identity",
            "commander_legality",
            "game_changer",
            "edhrec_rank",
            "price",
        ]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            _ = progress.add_task(
                description=f"Loading collection data from {collection_path}...",
                total=None,
            )

            # Get the card count of the collection for iteration purposes
            with open(file=collection_path, newline="\r\n", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                scryfall_ids = set()
                row_count = 0
                for row in reader:
                    scryfall_ids.add(row["Scryfall ID"])
                    row_count += 1

        print(
            f"Loaded {len(scryfall_ids)} distinct scryfall IDs out of {row_count} total rows"
        )

        print(f"Pulling {len(scryfall_ids)} distinct scryfall IDs out of '{scryfall_path}' and writing results to '{output_path}'")

        with Progress(
            TextColumn(text_format="{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        ) as progress:
            # Iterate through entire collection as a stream
            task = progress.add_task("Records Matched:", total=len(scryfall_ids))
            matches = 0
            missing_ids = scryfall_ids.copy()

            with open(file=scryfall_path, mode="rb") as f_in:
                with open(file=output_path, mode="w", encoding="utf-8") as f_out:
                    writer = csv.DictWriter(f_out, fieldnames=fields_to_extract)
                    writer.writeheader()
                    for card in ijson.items(f_in, "item"):
                        if card.get("id") in scryfall_ids:
                            row = {
                                "id": card.get("id"),
                                "name": card.get("name"),
                                "mana_cost": card.get("mana_cost"),
                                "cmc": card.get("cmc"),
                                "type_line": card.get("type_line"),
                                "oracle_text": card.get("oracle_text"),
                                "power": card.get("power"),
                                "toughness": card.get("toughness"),
                                "loyalty": card.get("loyalty"),
                                "colors": card.get("colors"),
                                "color_identity": card.get("color_identity"),
                                "commander_legality": card.get("legalities").get("commander"),
                                "game_changer": card.get("game_changer"),
                                "edhrec_rank": card.get("edhrec_rank"),
                                "price": card.get("prices").get("usd"),
                            }
                            writer.writerow(rowdict=row)
                            progress.advance(task_id=task)
                            missing_ids.remove(card.get("id"))
                            matches += 1

        print(f"Successfully annotated {matches} / {len(scryfall_ids)} target records")

        if matches != len(scryfall_ids):
            logging.error(message=f"Could not find scryfall card entries for {len(missing_ids)} scryfall IDs: {missing_ids}",fail=True)

    
    @override
    def get_deck(self, deck_id: str) -> Deck:
        """
        Fetch a deck from Archidekt using the provided deck ID.

        Args:
            deck_id (str): The ID of the deck to fetch.
        Returns:
            Deck: A Deck object containing the deck information.
        """
        response = requests.get(f"{self.base_url}/decks/{deck_id}/")

        response.raise_for_status()
        raw = response.json()

        # commander is identified by 'commander': true in the export payload
        commander_json = next(c for c in raw["cards"] if "Commander" in c.get("categories"))
        commander = self.map_card_json_to_model(commander_json)
        cards = [self.map_card_json_to_model(c) for c in raw["cards"]]

        return Deck(
            id=str(raw["id"]),
            provider=CollectionProvider.archidekt,
            name=raw["name"],
            cards=cards,
            commander=commander,
        )
