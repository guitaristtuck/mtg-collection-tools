from pathlib import Path

import typer

TYPER_APP_NAME = "mtg"

def get_app_dir() -> Path:
    return Path(typer.get_app_dir(TYPER_APP_NAME))

def get_data_path() -> Path:
    return get_app_dir().joinpath("data")

def get_config_path() -> Path:
    return get_app_dir().joinpath("config")