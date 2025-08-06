import typer

from mtg_collection_tools.commands.collection.card_picklist import (
    app as card_picklist_app,
)
from mtg_collection_tools.commands.collection.collection_sorter import (
    app as collection_sorter_app,
)
from mtg_collection_tools.commands.collection.refresh_collection import (
    app as refresh_collection_app,
)

app = typer.Typer(help="Interact with MTG Collection", no_args_is_help=True)

app.add_typer(refresh_collection_app)
app.add_typer(card_picklist_app)
app.add_typer(collection_sorter_app)
