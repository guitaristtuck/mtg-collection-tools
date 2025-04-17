from pathlib import Path
from typing import Any, override
from urllib.parse import urljoin

import requests
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from urllib3.connection import _get_default_user_agent

from mtg_collection_tools.util.common.constants import get_data_path
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
            _ = progress.add_task(description="Grabbing collection metadata...", total=None)

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

            task = progress.add_task("Records Downloaded:",total=card_count)

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
                    progress.advance(task_id=task,advance=chunk_data.count("\n"))


        print(f"{card_count} records successfully downloaded to '{target_path}'")    