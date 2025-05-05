from enum import StrEnum, auto
from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from mtg_collection_tools.util.models.mtg import Card, Deck


class BuilderMode(StrEnum):
    WORK_WITH_EXISTING_DECK = auto()
    BUILD_NEW_DECK = auto()
    GET_CARD_SUGGESTIONS = auto()

class DeckBuilderState(BaseModel):
    """
    In-memory snapshot of a deck-builder session.
    """
    messages: Annotated[list, add_messages] = Field(
        ...,
        description="List of messages exchanged between the user and the assistant. "    
    )
    builder_mode: BuilderMode | None = Field(
        default=None,
        description="Current interaction mode of the builder engine (e.g., ADD_CARDS, "
                    "UPGRADE_DECK, SUGGEST_COMMANDER).",
    )
    deck: Deck | None = Field(
        default=None,
        description="Deck that we are working with",
    )
    target_bracket: int | None = Field(
        default=None,
        description="Desired power / budget bracket using the offical WOTC bracket system (1–5 scale) "
                    "that guides upgrade suggestions.",
    )
    collection_id: str = Field(
        ...,
        description="Collection ID of your collection"
    )

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",          # reject unexpected keys
    }
