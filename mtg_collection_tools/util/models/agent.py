from enum import StrEnum, auto
from typing import Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.managed import RemainingSteps
from pydantic import BaseModel, Field

from mtg_collection_tools.util.models.mtg import Card, Deck
from mtg_collection_tools.util.providers.base import BaseProvider


class BuilderMode(StrEnum):
    WORK_WITH_EXISTING_DECK = auto()
    BUILD_NEW_DECK = auto()
    GET_CARD_SUGGESTIONS = auto()

class DeckBuilderState(BaseModel):
    """
    In-memory snapshot of a deck-builder session.
    """
    messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="List of messages exchanged between the user and the assistant. "    
    )
    remaining_steps: RemainingSteps = Field(
        default=25,
        description="Number of steps left"
    )
    is_last_step: bool = Field(
        default=False,
        description="Whether this is the last step in the graph execution"
    )
    builder_mode: BuilderMode | None = Field(
        default=None,
        description="Current interaction mode of the builder engine (e.g., ADD_CARDS, "
                    "UPGRADE_DECK, SUGGEST_COMMANDER).",
    )
    builder_params: dict[str, str] = Field(
        default_factory=dict,
        description="List of key-value pairs provided by the user to direct the deck builder agent"
    )
    original_deck: Deck | None = Field(
        default=None,
        description="Original loaded Deck that we loaded from the user's deck provider",
    )
    altered_deck: Deck | None = Field(
        default=None,
        description="Altered Deck that we are actively working with. Any changes here are suggested by the LLM and not yet saved",
    )
    target_bracket: int | None = Field(
        default=None,
        description="Desired power / budget bracket using the offical WOTC bracket system (1–5 scale) "
                    "that guides upgrade suggestions.",
    )
    builder_step: str | None = Field(
        default=None,
        description="Current builder step in the graph"
    )

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",          # reject unexpected keys
    }
