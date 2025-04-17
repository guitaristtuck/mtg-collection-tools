import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from typing_extensions import Annotated

from mtg_collection_tools.util.common import logging
from mtg_collection_tools.util.common.constants import (
    get_app_dir,
    get_config_path,
    get_data_path,
)
from mtg_collection_tools.util.models.config import CollectionProvider, MTGConfig
from mtg_collection_tools.util.providers import get_provider
from mtg_collection_tools.util.scryfall.api import ScryfallApi

app = typer.Typer()

COLLECTION_ID_HELP = {
    CollectionProvider.archidekt.value: "For Archidekt, this can be found by logging in, navigating to 'Collection', and grabbing the numerical value from the end of the url",
    CollectionProvider.moxfield.value: "For Moxfield, this can be found by logging in, navigating to 'Collection', selecting 'share', and grabbing the hash value from the end of the url",
}

@app.command(help="Initialize the cli tool")
def init(
    force: Annotated[bool, typer.Option("--force", "-f",help="Force re-initialization")] = False
):
    print("Initializing")

    config_file = get_config_path()

    if config_file.exists() and not force:
        print(f"Config file already exists at '{config_file}'. Re-run this command with '--force' to override existing config")
        raise typer.Exit(1)


    provider_name = Prompt.ask("What provider do you use for your MTG collection?", choices=[member.value for member in CollectionProvider])

    
    collection_id = Prompt.ask(f"What is your collection id? {COLLECTION_ID_HELP[provider_name]}")

    data_path = Prompt.ask("Where do you want the cli to store cached data? Enter nothing to use the default",default=str(get_data_path()),show_default=True)

    config = MTGConfig(
        collection_provider=CollectionProvider(provider_name),
        collection_id=collection_id,
        data_path=data_path,
    )

    print("This is the resulting configuration object: ")

    print(config.model_dump_json(indent=4))

    if Confirm.ask("Is this correct?"):
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            _ = progress.add_task(description="Testing Connection...", total=None)
            try:
                get_provider(config=config).test_connection()
            except Exception as e:
                logging.error(message=f"Unable to access API connection successfully with collection_id '{config.collection_id}'. Please check your collection_id value and try again. Error: \n{e}",fail=True)

            _ = progress.add_task(description=f"Writing Config to '{config_file}'...", total=None)

            if not get_app_dir().exists():
                get_app_dir().mkdir(parents=True,exist_ok=True)

            if config_file.exists() and force:
                config_file.unlink()

            with config_file.open("w", encoding="utf-8") as f:
                _ = f.write(f"COLLECTION_PROVIDER={config.collection_provider.value}\n")
                _ = f.write(f"COLLECTION_ID={config.collection_id}\n")
    else:
        print("Aborting!")
        raise typer.Abort()

    print("Initialization successful")