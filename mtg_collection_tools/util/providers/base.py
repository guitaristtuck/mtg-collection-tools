from abc import ABC, abstractmethod
from pathlib import Path

from langchain.tools import tool
from pydantic import SecretStr

from mtg_collection_tools.util.models.mtg import Deck


class BaseProvider(ABC):
    provider_name = "base"

    def __init__(self, username: str, password: SecretStr, data_path: Path):
        self.username = username
        self.password = password
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
    def list_decks(self) -> list[tuple[str,str]]:
        """
        List all decks by name and id associated with the logged-in user in the provider.

        Returns:
            list[tuple[str,str]]: A list of tuples of (id, name) pairs representing decks associated with the user
        """
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

    @abstractmethod
    def save_altered_deck(self,deck: Deck) -> str:
        """
        Save the deck object to the Provider and return the url for the saved deck.

        Args:
            deck (Deck): Full deck object

        Returns:
            str: url of the new deck
        """
        pass
