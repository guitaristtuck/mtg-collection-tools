from typing import Any

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from mtg_collection_tools.util.applets.collection_sorter.app import (
    run_collection_sorter_app,
)
from mtg_collection_tools.util.common.constants import get_data_path
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.providers import get_provider
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider
from mtg_collection_tools.util.providers.base import BaseProvider

app = typer.Typer()


@app.command(
    help="Run a collection sorter app to help organize cards by placing them in alphabetical order for given sets"
)
def sorter(
    ctx: typer.Context, 
    set_codes: Annotated[list[str], typer.Option("--set-code", "-s", help="Set codes to sort (can specify multiple)")],
):
    print("Initializing")
    config: MTGConfig = ctx.obj["config"]

    provider: BaseProvider = get_provider(config=config)

    run_collection_sorter_app(provider=provider, set_codes=set_codes) 
