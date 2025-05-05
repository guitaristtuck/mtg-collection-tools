from pathlib import Path
from typing import Annotated

from langchain_core.tools import BaseTool, tool

from mtg_collection_tools.util.models.mtg import Deck
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider


@tool
def load_deck_from_archidekt(
    collection_id: Annotated[str, "Identifier of the user's collection in archidekt"], 
    deck_id: Annotated[str, "Identifier of the user's deck to load from archidekt"]
)-> Deck:
    """
    Return a Deck object from archidekt based on the input deck_id.

    This deck will be a pydandic model and will return 100 cards
    """
    provider = ArchidektProvider(collection_id=collection_id,data_path=Path("/dev/null"))

    return provider.get_deck(deck_id=deck_id)

def get_deck_builder_tools() -> list[BaseTool]:
    return [load_deck_from_archidekt]
