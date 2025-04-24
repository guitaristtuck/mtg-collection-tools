import typer

from mtg_collection_tools.commands.scryfall.refresh_cards import (
    app as refresh_cards_app,
)

app = typer.Typer(help="Interact with Scryfall", no_args_is_help=True)

app.add_typer(refresh_cards_app)