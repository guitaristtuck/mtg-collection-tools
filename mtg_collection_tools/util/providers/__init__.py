from pathlib import Path

from pydantic import SecretStr

from mtg_collection_tools.util.models.config import CollectionProvider, MTGConfig
from mtg_collection_tools.util.providers.archidekt import ArchidektProvider
from mtg_collection_tools.util.providers.base import BaseProvider


def get_provider(config: MTGConfig) -> BaseProvider:
    """
    Get a provider based on the supplied config.

    Args:
        config (MTGConfig): configuration object used to get a provider

    Raises:
        NotImplementedError: For provider types that aren't yet implemented

    Returns:
        BaseProvider: A provider object
        
    """
    match config.collection_provider:
        case CollectionProvider.ARCHIDEKT:
            return ArchidektProvider(username=config.username, password=config.password, data_path=Path(config.data_path))
        case CollectionProvider.MOXFIELD:
            raise NotImplementedError("Moxfield provider not yet set up")

def get_provider_from_values(provider: CollectionProvider, username: str, password: SecretStr, data_path: Path) -> BaseProvider:
    """
    Get a provider based on the supplied values.

    Args:
        provider (CollectionProvider): provider type of the collection
        collection_id (str): id of the user's collection
        data_path (Path): base data path to use on local system

    Raises:
        NotImplementedError: For provider types that aren't yet implemented

    Returns:
        BaseProvider: A provider object
        
    """
    match provider:
        case CollectionProvider.ARCHIDEKT:
            return ArchidektProvider(username=username, password=password, data_path=data_path)
        case CollectionProvider.MOXFIELD:
            raise NotImplementedError("Moxfield provider not yet set up")
