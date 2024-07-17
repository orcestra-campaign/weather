"""Create the briefing folder and subfolder."""

import pathlib
import sys
from typing import Callable

from wblib.services import get_briefing_path
from wblib.services import get_briefing_paths

from wblib.api._logger import logger


def make_briefing_directory(date: str, logger: Callable = logger) -> None:
    logger(f"Creating briefing folders for '{date}'.", "INFO")
    briefing_parent_path = pathlib.Path(get_briefing_path(date))
    briefing_paths = get_briefing_paths(date)
    if briefing_parent_path.exists():
        logger(f"Path for date '{date}' already existed.", "WARNING")
    briefing_parent_path.mkdir(parents=True, exist_ok=True)
    for briefing_path_str in briefing_paths:
        briefing_path = pathlib.Path(briefing_path_str)
        briefing_path.mkdir(parents=False, exist_ok=True)
    logger(
        f"Subfolders for '{date}' briefing ready on '{briefing_parent_path}'",
        "INFO"
    )

if __name__ == "__main__":
    make_briefing_directory("20240101")

