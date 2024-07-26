"""Utility function for the api."""

from pathlib import Path
from typing import Callable

import yaml

from wblib.services.get_paths import get_variables_path

TIME_ZONE_STR = "UTC"

def _load_variables_yaml(date: str, logger: Callable) -> dict:
    variables_path = get_variables_path(date)
    logger(f"Loading variables file '{variables_path}'.", "INFO")
    with open(variables_path, "r") as stream:
        variables_dict = yaml.safe_load(stream)
    return variables_dict