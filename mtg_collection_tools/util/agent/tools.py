from pathlib import Path
from typing import Annotated

from langchain_core.tools import BaseTool, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, interrupt

from mtg_collection_tools.util.models.agent import DeckBuilderState
from mtg_collection_tools.util.models.config import CollectionProvider
from mtg_collection_tools.util.models.mtg import Deck
from mtg_collection_tools.util.providers import get_provider_from_values
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider

# def load_deck_from_provider(
#     collection_provider: Annotated[CollectionProvider, "Provider of the user's deck, such as archidekt or moxfield"],
#     collection_id: Annotated[str, "Identifier of the user's collection in the provider"], 
#     deck_id: Annotated[str, "Identifier of the user's deck to load from provider"]
# )-> Deck:
#     """
#     Return a Deck object from the provider based on the input deck_id.

#     This deck will be a pydandic model and will return 100 cards
#     """
#     provider = get_provider_from_values(
#         provider=collection_provider,
#         collection_id=collection_id,
#         data_path=Path("/dev/null")
#     )

#     return provider.get_deck(deck_id=deck_id)

# def save_deck_to_provider(
#     collection_provider: Annotated[CollectionProvider, "Provider of the user's deck, such as archidekt or moxfield"],
#     collection_id: Annotated[str, "Identifier of the user's collection in the provider"], 
#     deck_id: Annotated[str, "Identifier of the user's deck to load from provider"]
# )-> Deck:
#     """
#     Return a Deck object from the provider based on the input deck_id.

#     This deck will be a pydandic model and will return 100 cards
#     """
#     provider = get_provider_from_values(
#         provider=collection_provider,
#         collection_id=collection_id,
#         data_path=Path("/dev/null")
#     )

#     return provider.get_deck(deck_id=deck_id)


def get_deck_builder_tools() -> list[BaseTool]:
    
    @tool
    def load_original_deck(state: Annotated[DeckBuilderState, InjectedState]) -> Deck:
        """
        Return a Deck object that the user already provided prior to llm execution.

        This is a pydandic model that represents a full commander deck
        """
        return state.original_deck

    @tool
    def load_deck_builder_parameters(state: Annotated[DeckBuilderState, InjectedState]) -> dict[str,str]:
        """
        Return a dictionary of deck builder parameters.
        
        This is a dictionary of key-value pair value that represent deck building parameters 
        provided by the user prior to llm execution
        """
        return state.builder_params

    @tool
    def set_altered_deck(deck: Deck) -> Command:
        """
        Set the modified_deck property of the graph state.

        This is done by returning a langgraph Command with the update
        """
        return Command(update={"altered_deck": Deck})


    return [load_original_deck, load_deck_builder_parameters, set_altered_deck]
