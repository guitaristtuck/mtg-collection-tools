import json
from pathlib import Path

import pytest

from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.models.mtg import Card
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider

# Skip entire test file if collection provider is not archidekt
try:
    config = MTGConfig()
    if config.collection_provider != "archidekt":
        pytestmark = pytest.mark.skip(reason="Collection provider is not archidekt")
except Exception:
    pytestmark = pytest.mark.skip(reason="Could not load config or collection provider is not archidekt")

@pytest.fixture
def provider():
    config = MTGConfig()
    if not config.collection_provider == "archidekt":
        pytest.skip("Skipping test because collection provider is not archidekt")
    
    provider = ArchidektProvider(
        username=config.username,
        password=config.password,
        data_path=Path(config.data_path),
    )
    return provider

def test_get_collection_index(provider):
    """
    Test that the save card suggestions tool works as expected.

    This test will use the same config path as the cli for loading configuration,
    and will actually reach out to any external APIs to test the tool.
    """
    # TODO: this is just returning all cards in the collection. Might need to revisit filtering logic
    deck = provider.get_deck(deck_id="9785697")
    result = provider.get_matches_in_collection(cards=deck.cards)

    assert len(result.keys()) == len(deck.cards)
    print(result)

def test_get_cards_in_collection_for_sets(provider):
    """
    Test that the get cards in collection for sets tool works as expected.
    """
    cards = provider.get_cards_in_collection_for_sets(sets=["eoe","eos","eoc"])

    assert len(cards) > 0
    print([f"{card.name}: {card.set_code}" for card in cards])
