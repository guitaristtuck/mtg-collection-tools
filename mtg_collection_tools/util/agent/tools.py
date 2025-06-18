from typing import Annotated, Any, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolArg, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, interrupt
from pydantic import BaseModel

from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.mtg import (
    CardSuggestion,
    Deck,
    ValidatedCardSuggestion,
)
from mtg_collection_tools.util.providers.base import BaseProvider
from mtg_collection_tools.util.scryfall.api import ScryfallApi


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
    scryfall = ScryfallApi()
    validated_suggestions = []

    scryfall_cards, not_found = scryfall.search_for_exact_cards_by_name(
        [suggestion.name for suggestion in suggestions]
    )

    if len(not_found) > 0:
        raise ValueError(
            f"The following cards were not found in scryfall: {', '.join(not_found)}. This suggests that these card names are hallucinated."
        )

    if len(scryfall_cards) != len(suggestions):
        raise ValueError(
            f"The number of scryfall cards found ({len(scryfall_cards)}) does not match the number of suggestions ({len(suggestions)}). This suggests a programming error in the tool."
        )

    for scryfall_card, suggestion in zip(scryfall_cards, suggestions):
        validated_card = scryfall_card
        validated_card.quantity = suggestion.quantity
        validated_suggestions.append(
            ValidatedCardSuggestion(
                name=validated_card.name,
                quantity=suggestion.quantity,
                reason=suggestion.reason,
                card=validated_card,
            )
        )

    return Command(
        update={
            "card_suggestions": validated_suggestions,
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
