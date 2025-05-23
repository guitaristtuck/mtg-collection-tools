from typing import Any

import typer
from pydantic import Field
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from mtg_collection_tools.util.agent.deckbuilder import run_deckbuilder_agent
from mtg_collection_tools.util.common.constants import get_data_path
from mtg_collection_tools.util.models.agent import BuilderMode
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.providers import get_provider
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider
from mtg_collection_tools.util.providers.base import BaseProvider

app = typer.Typer()

@app.command(help="Run the MTG collection agent")
def run(
    ctx: typer.Context,
    builder_mode: Annotated[BuilderMode, typer.Option("--builder-mode", "-m", help="Builder mode to use when running the agent")],
    deck_id: Annotated[str | None, typer.Option("--deck-id", "-d", help=f"Idendifier of your deck. Only used when builder_mode = {BuilderMode.WORK_WITH_EXISTING_DECK}")] = None,
) -> None:  
    print("Initializing")
    run_deckbuilder_agent(config=ctx.obj["config"],builder_mode=builder_mode,deck_id=deck_id)
