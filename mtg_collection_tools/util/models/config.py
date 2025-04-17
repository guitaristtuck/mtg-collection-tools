from enum import Enum
from pathlib import Path

import typer
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mtg_collection_tools.util.common.constants import get_config_path, get_data_path


class CollectionProvider(str, Enum):
    moxfield = "moxfield"
    archidekt = "archidekt"

class MTGConfig(BaseSettings):
    collection_provider: CollectionProvider = Field(
        ..., description="Which Magic collection provider is being used: 'moxfield' or 'archidekt'."
    )
    collection_id: str = Field(
        ..., description="Identifier of the collection to pull."
    )
    data_path: str = Field(
        default=str(get_data_path()), description="Local path to use for cached data"
    )

    model_config = SettingsConfigDict(env_file=str(get_config_path()),env_file_encoding="utf-8")