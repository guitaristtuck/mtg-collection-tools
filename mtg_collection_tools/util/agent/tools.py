from typing import Annotated, Any, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolArg, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, interrupt
from pydantic import BaseModel

from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.mtg import CardSuggestion, Deck
from mtg_collection_tools.util.providers.base import BaseProvider


@tool
def save_card_suggestions(
    suggestions: Annotated[
        list[CardSuggestion], "List of card suggestions to save to the graph state"
    ],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command[Literal["altered_deck"]]:
    """
    Save a list of card suggestions to the graph state.

    This will completely overwrite the previous suggestions. Each suggestion should be a single card, but can
    be a positive or negative quantity to indicate if the card is being added or removed. Quantity should respect
    the singleton rules of a commander deck where applicable (For example, cards such as basic lands and Tempest Hawk
    may have multiple copies in the deck).
    """
    # TODO: This should also look up scryfall IDs for the cards and add them to the suggestions. This should also
    # be able to check if the card is in the user's collection and give back an error if it is not.
    return Command(
        update={
            "card_suggestions": suggestions,
            "messages": [
                ToolMessage(
                    content="Saved new card suggestions to graph state",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def get_deck_builder_tools(
    builder_mode: BuilderMode, provider: BaseProvider
) -> list[BaseTool]:
    match builder_mode:
        case BuilderMode.WORK_WITH_EXISTING_DECK:
            return [
                save_card_suggestions,
            ]
        case BuilderMode.BUILD_NEW_DECK:
            raise NotImplementedError("Building a new deck is not implemented yet")
        case BuilderMode.GET_CARD_SUGGESTIONS:
            raise NotImplementedError("Getting card suggestions is not implemented yet")
