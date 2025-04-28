import typer

from mtg_collection_tools.commands.agent.run import (
    app as run_app,
)

app = typer.Typer(help="Interact with the LLM agent", no_args_is_help=True)

app.add_typer(run_app)
