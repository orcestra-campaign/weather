"""Generate and save the report figures."""

from typing import Callable
from PIL import Image
from matplotlib.figure import Figure
import pandas as pd

from wblib.api._utils import _load_variables_yaml
from wblib.services.get_figures import generate_external_figures
from wblib.services.get_figures import generate_internal_figures
from wblib.services.get_paths import get_variables_path

from wblib.api._logger import logger


def make_briefing_images(date: str, logger: Callable = logger) -> None:
    current_time = pd.Timestamp.now("UTC")
    logger(f"Generating figures for {date} at {current_time}", "INFO")
    variables_dict = _load_variables_yaml(date, logger)
    # external
    external_figures = generate_external_figures(current_time, logger)
    for name, image in external_figures.items():
        fig_path = variables_dict["plots"]["external"][name]
        logger(f"Saved external figure '{name}' in '{fig_path}'.", "INFO")
        _save_image(image, fig_path)

    # internal

    internal_figures = generate_internal_figures(current_time, logger)
    for name, image in internal_figures.items():
        fig_path = variables_dict["plots"]["internal"][name]
        logger(f"Saved internal figure '{name}' in '{fig_path}'.", "INFO")
        _save_image(image, fig_path)


def _save_image(image, fig_path) -> None:
    if isinstance(image, Image):
        image.save(fig_path)
    if isinstance(image, Figure):
        image.savefig(fig_path)
    raise ValueError("Unrecognized figure type")


if __name__ == "__main__":
    make_briefing_images("20240101")  # for testing


