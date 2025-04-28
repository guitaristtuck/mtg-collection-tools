from typing import Any

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from mtg_collection_tools.util.agent.deckbuilder import run_deckbuilder_agent
from mtg_collection_tools.util.common.constants import get_data_path
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.providers import get_provider
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider
from mtg_collection_tools.util.providers.base import BaseProvider

app = typer.Typer()

@app.command(help="Run the MTG collection agent")
def run(
    ctx: typer.Context
) -> None:  
    print("Initializing")
    run_deckbuilder_agent(ctx.obj["config"])
