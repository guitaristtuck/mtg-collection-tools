import typer
from pydantic import ValidationError

from mtg_collection_tools.commands.collection import app as collection_app
from mtg_collection_tools.commands.init import app as init_app
from mtg_collection_tools.commands.scryfall import app as scryfall_app
from mtg_collection_tools.util.common import logging
from mtg_collection_tools.util.common.constants import get_config_path
from mtg_collection_tools.util.models.config import MTGConfig

app = typer.Typer(name="MTG Collection Tools CLI", no_args_is_help=True)

app.add_typer(init_app)
app.add_typer(scryfall_app, name="scryfall")
app.add_typer(collection_app, name="collection")


@app.callback(invoke_without_command=True)
def load_config(ctx: typer.Context):
    if not get_config_path().exists():
        logging.error(message=f"No config file found at '{get_config_path()}'. Try running 'mtg init' for initial setup", fail=True)

    try:  
        _ = ctx.ensure_object(object_type=dict)
        ctx.obj["config"] = MTGConfig()
    except ValidationError as e:
        logging.error(message=f"Config file '{get_config_path()}' has validation errors. Please try manually correcting these errors, or run 'mtg init -f' to reinitialize. Errors: \n{e}", fail=True)


if __name__ == "__main__":
    app()