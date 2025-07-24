import pytest

from mtg_collection_tools.util.agent.tools import save_card_suggestions
from mtg_collection_tools.util.models.agent import DeckBuilderState
from mtg_collection_tools.util.models.mtg import CardSuggestion


def test_save_card_suggestions():
    """
    Test that the save card suggestions tool works as expected.

    This test will use the same config path as the cli for loading configuration,
    and will actually reach out to any external APIs to test the tool.
    """
    suggestions = [
        CardSuggestion(
            name="Black Lotus", quantity=1, reason="Best in-class mana card"
        ),
        CardSuggestion(name="Sol Ring", quantity=1, reason="Staple ramp card"),
        CardSuggestion(name="Rhystic Study", quantity=1, reason="Card draw engine"),
        CardSuggestion(name="Cyclonic Rift", quantity=1, reason="Powerful board wipe"),
        CardSuggestion(
            name="Fierce Guardianship",
            quantity=1,
            reason="Free counterspell for protection",
        ),
        CardSuggestion(
            name="Dockside Extortionist", quantity=1, reason="Generates massive mana"
        ),
        CardSuggestion(name="Smothering Tithe", quantity=1, reason="Mana advantage"),
        CardSuggestion(name="Mana Crypt", quantity=1, reason="Fast mana source"),
        CardSuggestion(
            name="Teferi's Protection", quantity=1, reason="Protects board state"
        ),
        CardSuggestion(name="Forest", quantity=3, reason="Increase green mana base"),
        CardSuggestion(
            name="Counterspell",
            quantity=-1,
            reason="Too generic, making room for better options",
        ),
        CardSuggestion(
            name="Cultivate", quantity=-1, reason="Replacing with more efficient ramp"
        ),
        CardSuggestion(
            name="Lightning Bolt", quantity=-1, reason="Not impactful enough in EDH"
        ),
        CardSuggestion(name="Divination", quantity=-1, reason="Low value draw spell"),
        CardSuggestion(
            name="Cancel", quantity=-1, reason="Too expensive for its effect"
        ),
        CardSuggestion(
            name="Serra Angel", quantity=-1, reason="Outclassed by other creatures"
        ),
        CardSuggestion(
            name="Giant Growth", quantity=-1, reason="Not impactful in multiplayer"
        ),
        CardSuggestion(
            name="Disenchant", quantity=-1, reason="Redundant with other removal"
        ),
        CardSuggestion(
            name="Negate",
            quantity=-1,
            reason="Making room for more versatile counterspells",
        ),
        CardSuggestion(name="Swamp", quantity=-3, reason="Reducing black mana base"),
    ]

    # Call the function manually with all required parameters
    result = save_card_suggestions.invoke(
        {
            "suggestions": suggestions,
            "must_be_in_collection": False,
            "state": DeckBuilderState(),
            "tool_call_id": "fake_tool_call_id",
        }
    )

    # Verify the result
    assert len(result.update.get("card_suggestions")) == len(suggestions)


def test_save_card_suggestions_not_in_scryfall():
    """
    Test that the save card suggestions tool works as expected when one or more cards are not in scryfall.
    """
    suggestions = [
        CardSuggestion(
            name="Totally Not a Real Card",
            quantity=1,
            reason="Making room for more versatile counterspells",
        ),
        CardSuggestion(
            name="Hallucinations of a bad LLM",
            quantity=-3,
            reason="Reducing black mana base",
        ),
        CardSuggestion(
            name="Counterspell",
            quantity=-1,
            reason="Making room for more versatile counterspells",
        ),
        CardSuggestion(
            name="Dawn's Truce",
            quantity=+1,
            reason="Adding more protection",
        ),
    ]

    with pytest.raises(ValueError) as e:
        _ = save_card_suggestions.invoke(
            {
                "suggestions": suggestions,
                "must_be_in_collection": False,
                "state": DeckBuilderState(),
                "tool_call_id": "fake_tool_call_id",
            }
        )

    assert (
        "The following cards were not found in scryfall: Totally Not a Real Card, Hallucinations of a bad LLM. This suggests that these card names are hallucinated."
        in str(e.value)
    )
