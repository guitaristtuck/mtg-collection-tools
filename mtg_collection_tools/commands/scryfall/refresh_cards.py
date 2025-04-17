import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from mtg_collection_tools.util.common.constants import get_data_path
from mtg_collection_tools.util.scryfall.api import ScryfallApi

app = typer.Typer()

@app.command(help="Download the bulk list of oracle card data from scryfall")
def refresh_cards(
    force: Annotated[bool, typer.Option("--force", "-f",help="Force re-download of bulk data")] = False
):
    print("Initializing")

    api = ScryfallApi()

    print("Fetching Bulk Metadata")
    oracle_cards_metadata = next((item for item in api.get_bulk_data().get("data") if item.get("type") == "oracle_cards"), None)

    if not oracle_cards_metadata:
        print("Couldn't find a bulk data entry for type 'oracle_cards' from scryfall")
        raise typer.Exit(1)

    print("Checking for existing exports locally")

    data_dir = get_data_path().joinpath("scryfall")
    timestamp_file =data_dir.joinpath("updated_at")
    data_file =data_dir.joinpath("oracle_cards.json")

    download_data = True

    if timestamp_file.exists():
        existing_timestamp = timestamp_file.read_text("utf-8").strip()

        if existing_timestamp != oracle_cards_metadata.get("updated_at"):
            print(f"Scryfall has a timestamp of {oracle_cards_metadata.get('updated_at')}, while local timestamp is {existing_timestamp}. Re-downloading bulk data.")
            download_data = True
        else:
            print(f"scryfall timestamp of {existing_timestamp} matches local data file. Using existing local bulk data.")
            download_data = False
    else:
        print("No local download of bulk data. This will be pulled from scryfall")

    if download_data or force:
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)

        if data_file.exists():
            data_file.unlink()

        timestamp_file.write_text(data=oracle_cards_metadata.get("updated_at"))
        api.download_bulk(uri=oracle_cards_metadata.get("download_uri"),dest_path=data_file,size=oracle_cards_metadata.get("size"))


