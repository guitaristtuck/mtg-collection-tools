from abc import ABC, abstractmethod
from pathlib import Path

from langchain.tools import tool

from mtg_collection_tools.util.models.mtg import Deck


class BaseProvider(ABC):
    provider_name = "base"

    def __init__(self, collection_id: str, data_path: Path):
        self.collection_id = collection_id
        self.data_path = data_path / self.provider_name

    @abstractmethod
    def test_connection(self):
        pass

    @abstractmethod
    def download_collection(self):
        pass

    @abstractmethod
    def annotate_collection(self):
        pass

    @abstractmethod
    def get_deck(self, deck_id: str) -> Deck:
        """
        Fetch a deck from a Provider using the provided deck ID.

        Args:
            deck_id (str): The ID of the deck to fetch.
        Returns:
            Deck: A Deck object containing the deck information.
        """
        pass
