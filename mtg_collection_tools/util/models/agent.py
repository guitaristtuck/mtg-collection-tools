from enum import StrEnum, auto

from pydantic import BaseModel, Field

from mtg_collection_tools.util.models.mtg import Card, Deck


class BuilderMode(StrEnum):
    WORK_WITH_EXISTING_DECK = auto()
    BUILD_NEW_DECK = auto()
    GET_CARD_SUGGESTIONS = auto()
    INVALID_MODE = auto()

class DeckBuilderState(BaseModel):
    """
    In-memory snapshot of a deck-builder session.
    """
    messages: list[str] = Field(
        ...,
        description="List of messages exchanged between the user and the assistant. "    
    )
    builder_mode: BuilderMode = Field(
        ...,
        description="Current interaction mode of the builder engine (e.g., ADD_CARDS, "
                    "UPGRADE_DECK, SUGGEST_COMMANDER).",
    )
    deck: Deck = Field(
        ...,
        description="Deck that we are working with",
    )
    target_bracket: int = Field(
        ...,
        description="Desired power / budget bracket using the offical WOTC bracket system (1–5 scale) "
                    "that guides upgrade suggestions.",
    )

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",          # reject unexpected keys
    }
