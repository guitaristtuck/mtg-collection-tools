from typing import Any

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from mtg_collection_tools.util.applets.picklist.app import run_picklist_app
from mtg_collection_tools.util.common.constants import get_data_path
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.providers import get_provider
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider
from mtg_collection_tools.util.providers.base import BaseProvider

app = typer.Typer()


@app.command(
    help="Run a picklist app to assist with grabbing cards from a collection to build a deck"
)
def picklist(
    ctx: typer.Context, 
    deck_id: Annotated[str, typer.Option("--deck-id", "-d", help="Identifier of your deck")],
):
    print("Initializing")
    config: MTGConfig = ctx.obj["config"]

    provider: BaseProvider = get_provider(config=config)

    run_picklist_app(provider=provider, deck_id=deck_id)
