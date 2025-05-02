from pydantic import BaseModel, Field
from pydantic.v1.errors import NoneIsAllowedError

from mtg_collection_tools.util.models.config import CollectionProvider


class Card(BaseModel):
    """A single Magic: The Gathering card with game-relevant metadata."""

    id: str = Field(
        ...,
        description="Scryfall UUID for this card (e.g., '0001f1ef-b957-4a55-b47f-14839cdbab6f').",
    )
    name: str = Field(..., description="Card’s printed English name.")
    mana_cost: str = Field(
        ...,
        description="Mana cost in MTG notation (e.g., '{2}{G}{G}'). "
                    "Use an empty string for cards with no cost.",
    )
    cmc: float = Field(
        ...,
        description="Converted mana cost / mana value. Numeric so split cards, X-spells, etc. work."
    )
    type_line: str = Field(
        ...,
        description="Exact type line (e.g., 'Creature — Human Knight').",
    )
    oracle_text: str = Field(
        ...,
        description="Current Oracle rules text with newline literals (\\n) between paragraphs."
    )
    power: str | None = Field(
        None,
        description="Power as printed. Keep as string so '*' and '∞' are valid; None for non-creatures.",
    )
    toughness: str | None = Field(
        None,
        description="Toughness as printed; same rules as power.",
    )
    loyalty: str | None = Field(
        None,
        description="Starting loyalty for planeswalkers; None otherwise.",
    )
    colors: list[str] = Field(
        ...,
        description="List of single-letter color abbreviations this card is printed with "
                    "(e.g., ['G', 'U']). Empty list for colorless.",
    )
    color_identity: list[str] = Field(
        ...,
        description="Color identity for Commander (rules 903.4); may include colors not in `colors`."
    )
    commander_legality: str = Field(
        ...,
        description="Legality status in Commander format (e.g., 'legal', 'banned', 'restricted').",
    )
    game_changer: bool = Field(
        ...,
        description="True if the card dramatically shifts board state by itself (custom flag).",
    )
    edhrec_rank: int | None = Field(
        ...,
        description="Current EDHREC popularity rank; higher means less played. None if unavailable.",
    )
    price: str = Field(
        ...,
        description="Latest market price in USD as string to preserve formatting (e.g., '0.08').",
    )

    model_config = {
        "extra": "forbid",   # disallow unknown keys
    }

class Deck(BaseModel):
    """A full Commander deck with game-relevant metadata."""
    id: str = Field(
        ...,
        description="Scryfall UUID for this deck (e.g., '0001f1ef-b957-4a55-b47f-14839cdbab6f').",
    )
    provider: CollectionProvider = Field(
        ...,
        description="The collection provider this deck is associated with (e.g., 'moxfield', 'archidekt').",
    )
    name: str = Field(..., description="Deck’s printed English name.")
    cards: list[Card] = Field(
        ...,
        description="List of cards in the deck. Order preserved so the front-end can show the list exactly as built.",
    )
    commander: Card = Field(
        ...,
        description="The card designated as the deck’s commander. Must also appear in `cards`.",
    )

    model_config = {
        "extra": "forbid",   # disallow unknown keys
    }
