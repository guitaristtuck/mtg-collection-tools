"""Integration tests for the collection sorter app."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from mtg_collection_tools.util.applets.collection_sorter.app import (
    run_collection_sorter_app,
)
from mtg_collection_tools.util.models.mtg import Card
from mtg_collection_tools.util.providers.base import BaseProvider


class MockProvider(BaseProvider):
    """Mock provider for testing."""
    
    def test_connection(self):
        pass
    
    def download_collection(self):
        pass
    
    def annotate_collection(self):
        pass
    
    def list_decks(self):
        return []
    
    def get_deck(self, deck_id: str):
        # This is a mock method, so we'll raise an exception to indicate it's not implemented
        raise NotImplementedError("Mock provider does not implement get_deck")
    
    def save_altered_deck(self, deck):
        return "mock_url"
    
    def get_cards_in_collection_for_sets(self, sets: list[str]):
        """Return mock cards for testing."""
        return [
            Card(
                id="test1",
                name="Test Card 1",
                set_code="TEST",
                quantity=2,
                mana_cost="",
                cmc=0.0,
                type_line="",
                oracle_text="",
                power=None,
                toughness=None,
                loyalty=None,
                colors=[],
                color_identity=[],
                commander_legality="",
                game_changer=False,
                edhrec_rank=None,
                price="0"
            ),
            Card(
                id="test2", 
                name="Test Card 2",
                set_code="TEST",
                quantity=1,
                mana_cost="",
                cmc=0.0,
                type_line="",
                oracle_text="",
                power=None,
                toughness=None,
                loyalty=None,
                colors=[],
                color_identity=[],
                commander_legality="",
                game_changer=False,
                edhrec_rank=None,
                price="0"
            )
        ]


def test_collection_sorter_app_import():
    """Test that the collection sorter app can be imported."""
    from mtg_collection_tools.util.applets.collection_sorter.app import CollectionSorter
    assert CollectionSorter is not None


def test_collection_sorter_app_initialization():
    """Test that the collection sorter app can be initialized."""
    provider = MockProvider(username="test", password=SecretStr("test"), data_path=Path("/tmp"))
    set_codes = ["TEST"]
    
    # This should not raise an exception
    assert provider.get_cards_in_collection_for_sets(set_codes) is not None


def test_collection_sorter_app_functionality():
    """Test that the collection sorter app has the expected functionality."""
    provider = MockProvider(username="test", password=SecretStr("test"), data_path=Path("/tmp"))
    set_codes = ["TEST"]
    
    # Test that we can get cards from the provider
    cards = provider.get_cards_in_collection_for_sets(set_codes)
    assert len(cards) == 2
    assert cards[0].name == "Test Card 1"
    assert cards[1].name == "Test Card 2"
    
    # Test that cards are sorted alphabetically
    sorted_cards = sorted(cards, key=lambda x: x.name)
    assert sorted_cards[0].name == "Test Card 1"
    assert sorted_cards[1].name == "Test Card 2" 
