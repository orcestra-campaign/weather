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
    logger("Generating briefing figures", "INFO")
    variables_dict = _load_variables_yaml(date, logger)
    # external
    external_time = pd.Timestamp.now(TIME_ZONE_STR)
    logger(f"External figure time set to {external_time}", "INFO")
    external_figures = generate_external_figures(external_time, logger)
    for name, image in external_figures.items():
        fig_path = variables_dict["plots"]["external"][name]
        _save_image(image, fig_path)
        logger(f"Saved external figure '{name}' in '{fig_path}'.", "INFO")
    # internal
    internal_time = pd.Timestamp(date, tz=TIME_ZONE_STR)
    logger(f"Internal figure time set to {internal_time}", "INFO")
    internal_figures = generate_internal_figures(internal_time, logger)
    for name, images in internal_figures.items():
        fig_paths = variables_dict["plots"]["internal"][name]
        for lead_time, fig_path in fig_paths.items():
            image = images[lead_time]
            _save_image(image, fig_path)
            logger(f"Saved internal figure '{name}' for '{internal_time}' "
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
    make_briefing_images("20240731")  # for testing


