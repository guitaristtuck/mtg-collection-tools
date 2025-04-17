
from pathlib import Path

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
        case CollectionProvider.archidekt:
            return ArchidektProvider(collection_id=config.collection_id, data_path=Path(config.data_path))
        case CollectionProvider.moxfield:
            raise NotImplementedError("Moxfield provider not yet set up")
