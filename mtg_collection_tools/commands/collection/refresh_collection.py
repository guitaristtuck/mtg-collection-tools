from typing import Any

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from mtg_collection_tools.util.common.constants import get_data_path
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.providers import get_provider
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider
from mtg_collection_tools.util.providers.base import BaseProvider

app = typer.Typer()


@app.command(help="Refresh collection card data")
def refresh(ctx: typer.Context):
    print("Initializing")
    config: MTGConfig = ctx.obj["config"]

    provider: BaseProvider = get_provider(config=config)

    provider.download_collection()


@app.command(help="Annotate collection card data with scryfall data")
def annotate(ctx: typer.Context):
    print("Initializing")
    config: MTGConfig = ctx.obj["config"]

    provider: BaseProvider = get_provider(config=config)

    provider.annotate_collection()
