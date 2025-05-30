from typing import Annotated, Any, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolArg, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, interrupt

from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.mtg import Deck
from mtg_collection_tools.util.providers.base import BaseProvider


def make_load_original_deck_to_state_tool(provider: BaseProvider) -> BaseTool:
    @tool
    def load_original_deck_to_state(
            state: Annotated[DeckBuilderState, InjectedState],
            tool_call_id: Annotated[str, InjectedToolCallId]
        ) -> Annotated[Command[Literal["original_deck"]], "Command to update the original_deck in the graph state"]:
        """
        Load the original deck from the provider and store it in the graph state.

        This tool will prompt the user for a deck_id if one is not provided in the graph state, and
        then use that deck_id to load the deck from the provider. This will return a Command to update
        the original_deck property of the graph state.
        """
        # check if the user provided a deck_id already
        if state.original_deck and state.original_deck.id:
            deck_id= str(state.original_deck.id)
        else:
            # prompt the user what deck they want to load
            prompt = f"Which deck would you like to load from {provider.provider_name}?"
            deck_info = provider.list_decks()
            for i in range(len(deck_info)):
                prompt += (f"\n\t{i + 1}. {deck_info[i][1]}")

            prompt += "\nEnter deck number from above:"

            while True:
                user_input = interrupt(prompt + "\n> ")
                user_input_int = 0

                try:
                    user_input_int = int(user_input) - 1
                    if user_input_int not in range(len(deck_info)):
                        raise ValueError()
                    break
                except ValueError:
                    prompt = f"Invalid option. Please enter [{1} - {len(deck_info)}]"

            deck_id= deck_info[user_input_int][0]

        original_deck = provider.get_deck(deck_id=deck_id)

        return Command(update={
            "original_deck": original_deck,
            "messages": [
                ToolMessage(
                    content=f"Loaded {sum(card.quantity for card in original_deck.cards)} cards ({len(original_deck.cards)} unique) from deck '{original_deck.name}'",
                    tool_call_id=tool_call_id
                )
            ]
        })

    return load_original_deck_to_state

@tool
def get_original_deck_from_state(state: Annotated[DeckBuilderState, InjectedState]) -> Deck:
    """
    Get the original deck from the graph state
    """
    if not state.original_deck:
        raise ValueError("No original deck found in state")
    return state.original_deck

@tool
def set_altered_deck_in_state(
    deck: Annotated[Deck, "Deck to set in the graph state. This is in the exact same format as the original deck"],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command[Literal["altered_deck"]]:
    """
    Set the altered deck in the graph state.

    This should be in the same format as the original deck, but with the suggested cuts and adds.
    When calling this tool, the deck.name property should be set to a new descriptive name for the deck
    based on the original deck name and the suggested cuts and adds.
    """
    return Command(update={
            "altered_deck": deck,
            "messages": [
                ToolMessage(
                    content="Saved altered deck to state",
                    tool_call_id=tool_call_id
                )
            ]
        })

def make_save_altered_deck_from_state_to_provider_tool(provider: BaseProvider) -> BaseTool:
    @tool
    def save_altered_deck_from_state_to_provider(
        state: Annotated[DeckBuilderState, InjectedState]
    ) -> Annotated[str, "URL of the saved deck"]:
        """
        Save the altered deck from the state to the provider
        """
        if not state.altered_deck:
            raise ValueError("No altered deck found in state")
        return provider.save_altered_deck(deck=state.altered_deck)

    return save_altered_deck_from_state_to_provider

@tool
def prompt_user(
    prompt: Annotated[str, "Prompt to ask the user for input"]
) -> Annotated[str, "User input in response to the prompt"]:
    """
    Prompt the user for input and return the user's response
    """
    return interrupt("❓: " +prompt + "\n> ")

def get_deck_builder_tools(builder_mode: BuilderMode, provider: BaseProvider) -> list[BaseTool]:
    match builder_mode:
        case BuilderMode.WORK_WITH_EXISTING_DECK:
            return [
                make_load_original_deck_to_state_tool(provider=provider), 
                get_original_deck_from_state, 
                set_altered_deck_in_state, 
                make_save_altered_deck_from_state_to_provider_tool(provider=provider), 
                prompt_user
            ]
        case BuilderMode.BUILD_NEW_DECK:
            raise NotImplementedError("Building a new deck is not implemented yet")
        case BuilderMode.GET_CARD_SUGGESTIONS:
            raise NotImplementedError("Getting card suggestions is not implemented yet")
