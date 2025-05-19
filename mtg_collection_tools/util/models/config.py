from enum import StrEnum, auto
from pathlib import Path

import typer
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from mtg_collection_tools.util.common.constants import get_config_path, get_data_path


class CollectionProvider(StrEnum):
    MOXFIELD = auto()
    ARCHIDEKT = auto()

class MTGConfig(BaseSettings):
    collection_provider: CollectionProvider = Field(
        ..., description="Which Magic collection provider is being used: 'moxfield' or 'archidekt'."
    )
    username: str = Field(
        ..., description="Username for the provider"
    )
    password: SecretStr = Field(
        ..., description="Password for the provider"
    )
    data_path: str = Field(
        default=str(get_data_path()), description="Local path to use for cached data"
    )
    anthropic_api_key: str | None = Field(
        description="Anthropic API key for Claude AI."
    )

    model_config = SettingsConfigDict(env_file=str(get_config_path()),env_file_encoding="utf-8")
