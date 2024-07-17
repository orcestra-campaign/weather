"""Generate and save the report figures."""

from pathlib import Path
from typing import Callable
import yaml

from wblib.api._utils import _load_variables_yaml
from wblib.services.get_figures import generate_external_figures
from wblib.services.get_figures import generate_internal_figures
from wblib.services.get_paths import get_variables_path

from wblib.api._logger import logger


def make_briefing_images(date: str, logger: Callable = logger) -> None:
    logger(f"Generating figures for {date}", "INFO")
    variables_dict = _load_variables_yaml(date, logger)
    # external
    external_figures = generate_external_figures(logger)
    for name, image in external_figures.items():
        fig_path = variables_dict["plots"]["external"][name]
        logger(f"Saved figure '{name}' in '{fig_path}'.", "INFO")
        image.save(fig_path)
    # internal
    internal_figures = generate_internal_figures(logger)
    for name, image in internal_figures.items():
        fig_path = variables_dict["plots"]["internal"][name]
        image.save(fig_path)


if __name__ == "__main__":
    make_briefing_images("20240101")  # for testing


