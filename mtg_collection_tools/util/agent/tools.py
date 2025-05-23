from typing import Annotated, Any, Literal

from langchain_core.tools import BaseTool, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from mtg_collection_tools.util.models.agent import DeckBuilderState
from mtg_collection_tools.util.models.mtg import Deck


def get_deck_builder_tools() -> list[BaseTool]:
    
    @tool
    def load_original_deck(state: Annotated[DeckBuilderState, InjectedState]) -> dict[str, Any]:
        """
        Return a Deck object that the user already provided prior to llm execution.

        This is a pydandic model that represents a full commander deck. The output will be a dictionary
        with the following structure:
        {
            "id": str | None,
            "provider": str,
            "name": str | None,
            "cards": list[dict],  # Each card is a dictionary with card properties
            "commander": dict | None  # Commander card as a dictionary
        }
        """
        if not state.original_deck:
            return {}
        return state.original_deck.model_dump()

    @tool
    def load_deck_builder_parameters(state: Annotated[DeckBuilderState, InjectedState]) -> dict[str,str]:
        """
        Return a dictionary of deck builder parameters.
        
        This is a dictionary of key-value pair value that represent deck building parameters 
        provided by the user prior to llm execution
        """
        return state.builder_params

    @tool
    def set_altered_deck(deck_dict: dict[str, Any]) -> Command[Literal["altered_deck"]]:
        """
        Set the modified_deck property of the graph state.

        Args:
            deck_dict: A dictionary representing a deck with the following structure:
            {
                "id": str | None,
                "provider": str,
                "name": str | None,
                "cards": list[dict],  # Each card is a dictionary with card properties
                "commander": dict | None  # Commander card as a dictionary
            }

        This is done by returning a langgraph Command with the update
        """
        # Convert the dictionary back to a Deck object
        deck = Deck.model_validate(deck_dict)
        return Command(update={"altered_deck": deck})

    return [load_original_deck, load_deck_builder_parameters, set_altered_deck]
