import typer

from mtg_collection_tools.commands.collection.refresh_collection import (
    app as refresh_collection_app,
)

app = typer.Typer(help="Interact with MTG Collection", no_args_is_help=True)

app.add_typer(refresh_collection_app)