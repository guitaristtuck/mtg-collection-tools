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


class ScryfallApi():
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
                task = progress.add_task("Progress:",total=size)

                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(self.download_chunk_size):
                        if chunk:
                            progress.update(task, advance=len(chunk))
                            _ = f.write(chunk)
                            
    def get_bulk_data(self) -> dict[str,any]:
        r = requests.get(url=posixpath.join(self.base_uri,"bulk-data"))
        return r.json()