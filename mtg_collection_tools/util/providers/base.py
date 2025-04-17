from abc import ABC, abstractmethod
from pathlib import Path


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