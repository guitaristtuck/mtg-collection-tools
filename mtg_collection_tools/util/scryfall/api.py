import posixpath
from pathlib import Path, PosixPath

import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from mtg_collection_tools.util.models.mtg import Card


class ScryfallApi:
    base_uri = "https://api.scryfall.com"
    download_chunk_size = 8192

    def __init__(self):
        pass

    def download_bulk(self, uri: str, dest_path: Path, size: int):
        with requests.get(url=uri, stream=True) as r:
            r.raise_for_status()

            print(f"Downloading {uri} to {dest_path}:")

            with Progress(
                TextColumn(text_format="{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Progress:", total=size)

                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(self.download_chunk_size):
                        if chunk:
                            progress.update(task, advance=len(chunk))
                            _ = f.write(chunk)

    def get_bulk_data(self) -> dict[str, any]:
        r = requests.get(url=posixpath.join(self.base_uri, "bulk-data"))
        return r.json()

    def search_for_exact_card_by_name(self, name: str) -> Card:
        """
        Search for an exact card by name.

        Args:
            name (str): The name of the card to search for.

        Returns:
            Card: The card object if found. Raises an exception if the card is not found.
        """
        response = requests.get(
            url=posixpath.join(self.base_uri, "cards/named"),
            params={"exact": f"{name}"},
        )
        response.raise_for_status()
        return self.map_card_json_to_model(response.json())

    def search_for_exact_cards_by_name(
        self, names: list[str]
    ) -> tuple[list[Card], list[str]]:
        """
        Search for multiple cards by name.

        This uses scryfall's collection search endpoint to make lookups more efficient for multiple cards.
        The API only allows 75 identifiers at a time, so requests are batched accordingly.

        Args:
            names (list[str]): The names of the cards to search for.

        Returns:
            tuple[list[Card], list[str]]: A tuple containing the list of cards found and the list of names that were not found.
        """
        MAX_IDENTIFIERS = 75
        all_cards = []
        all_not_found = []

        # Process names in batches of MAX_IDENTIFIERS
        for i in range(0, len(names), MAX_IDENTIFIERS):
            batch_names = names[i : i + MAX_IDENTIFIERS]

            response = requests.post(
                url=posixpath.join(self.base_uri, "cards/collection"),
                json={"identifiers": [{"name": name} for name in batch_names]},
            )
            response.raise_for_status()

            response_data = response.json()

            # Add found cards to results
            all_cards.extend(
                [
                    self.map_card_json_to_model(card)
                    for card in response_data.get("data", [])
                ]
            )

            # Add not found names to results
            not_found_batch = response_data.get("not_found", [])
            all_not_found.extend(
                [identifier.get("name") for identifier in not_found_batch]
            )

        return all_cards, all_not_found

    @staticmethod
    def map_card_json_to_model(card_json: dict[str, Any]) -> Card:
        """Maps the JSON response from scryfall to the Card model."""

        # Extract the relevant fields from the JSON response
        card_data = {
            "id": card_json.get("id"),
            "name": card_json.get("name"),
            "mana_cost": card_json.get("mana_cost"),
            "cmc": card_json.get("cmc"),
            "type_line": card_json.get("type_line"),
            "oracle_text": card_json.get("oracle_text"),
            "power": card_json.get("power"),
            "toughness": card_json.get("toughness"),
            "loyalty": card_json.get("loyalty"),
            "colors": card_json.get("colors"),
            "color_identity": card_json.get("color_identity"),
            "commander_legality": card_json.get("legalities").get("commander"),
            "game_changer": card_json.get("game_changer"),
            "edhrec_rank": card_json.get("edhrec_rank"),
            "price": str(card_json.get("prices").get("usd")),
        }

        # Create a Card instance using the extracted data
        return Card.model_validate(card_data)
