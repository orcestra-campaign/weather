"""Generate and save the report figures."""

from typing import Callable
from PIL.Image import Image
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import pandas as pd

from wblib.api._utils import TIME_ZONE_STR, _load_variables_yaml
from wblib.services.get_figures import generate_external_figures
from wblib.services.get_figures import generate_internal_figures
from wblib.services.get_paths import get_briefing_path

from wblib.api._logger import logger


def make_briefing_images(date: str, logger: Callable = logger) -> None:
    logger("Generating briefing figures", "INFO")
    variables_dict = _load_variables_yaml(date, logger)
    # external
    external_time = pd.Timestamp.now(TIME_ZONE_STR)
    logger(f"External figure time set to {external_time}", "INFO")
    external_figures = generate_external_figures(external_time, logger)
    for name, image in external_figures.items():
        fig_path = get_briefing_path(date) + "/" + variables_dict["plots"]["external"][name]
        _save_image(image, fig_path)
        logger(f"Saved external figure '{name}' in '{fig_path}'.", "INFO")
    # internal
    internal_time = pd.Timestamp(date, tz=TIME_ZONE_STR)
    logger(f"Internal figure time set to {internal_time}", "INFO")
    for product, lead_time, image in generate_internal_figures(internal_time, logger):
        fig_rel_path = variables_dict["plots"]["internal"][product][lead_time]
        fig_path = get_briefing_path(date) + "/" + fig_rel_path
        _save_image(image, fig_path)
        logger(f"Saved internal figure '{product}' for '{internal_time}' "
                f"and '{lead_time}' in '{fig_path}'.", "INFO")
        plt.close(image)


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


