"""Generate and save the report figures."""

from typing import Callable
from PIL.Image import Image
from matplotlib.figure import Figure
import pandas as pd

from wblib.api._utils import TIME_ZONE_STR, _load_variables_yaml
from wblib.services.get_figures import generate_external_figures
from wblib.services.get_figures import generate_internal_figures

from wblib.api._logger import logger


def make_briefing_images(date: str, logger: Callable = logger) -> None:
    current_time = pd.Timestamp.now(TIME_ZONE_STR)
    logger(f"Generating figures for {date} at {current_time}", "INFO")
    variables_dict = _load_variables_yaml(date, logger)
    # external
    external_figures = generate_external_figures(current_time, logger)
    for name, image in external_figures.items():
        fig_path = variables_dict["plots"]["external"][name]
        _save_image(image, fig_path)
        logger(f"Saved external figure '{name}' in '{fig_path}'.", "INFO")
    # internal
    internal_figures = generate_internal_figures(current_time, logger)
    for name, images in internal_figures.items():
        fig_paths = variables_dict["plots"]["internal"][name]
        for lead_time, fig_path in fig_paths.items():
            image = images[lead_time]
            _save_image(image, fig_path)
            logger(f"Saved internal figure '{name}' for '{current_time}' "
                   f"and '{lead_time}' in '{fig_path}'.", "INFO")


def _save_image(image, fig_path) -> None:
    if isinstance(image, Figure):
        image.tight_layout()
        image.savefig(fig_path)
        return
    if isinstance(image, Image):
        image.save(fig_path)
        return
    raise ValueError("Unrecognized figure type")


if __name__ == "__main__":
    make_briefing_images("20240101")  # for testing


