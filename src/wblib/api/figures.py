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
from wblib.flights.flighttrack import get_python_flightdata
from wblib.api._logger import logger


def make_briefing_figures(date: str, logger: Callable = logger) -> None:
    logger("Generating briefing figures", "INFO")
    variables_dict = _load_variables_yaml(date, logger)
    # external
    external_location = variables_dict["location"]
    logger(f"External figure location set to {external_location}", "INFO")
    current_time = pd.Timestamp.now(TIME_ZONE_STR)
    logger(f"External figure time set to {current_time}", "INFO")
    for product, image in generate_external_figures(
        external_location, current_time, logger
    ):
        fig_path = variables_dict["plots"]["external"][product]
        fig_path = get_briefing_path(date) + "/" + fig_path
        _save_image(image, fig_path)
        _close_image(image)
        logger(f"Saved external figure '{product}' in '{fig_path}'.", "INFO")
    # internal
    briefing_time = pd.Timestamp(date, tz=TIME_ZONE_STR)
    sattracks_fc_date = variables_dict["sattracks_fc_date"]
    sattracks_fc_time = pd.Timestamp(sattracks_fc_date, tz=TIME_ZONE_STR)
    flight_id = variables_dict["flight_id"]
    flight = get_python_flightdata(flight_id)
    logger(f"Internal figure time set to {briefing_time}", "INFO")
    for product, lead_time, image in generate_internal_figures(
        briefing_time, current_time, sattracks_fc_time, flight, logger
    ):
        fig_path = variables_dict["plots"]["internal"][product][lead_time]
        fig_path = get_briefing_path(date) + "/" + fig_path
        _save_image(image, fig_path)
        _close_image(image)
        logger(
            f"Saved internal figure '{product}' for '{briefing_time}' "
            f"and '{lead_time}' in '{fig_path}'.",
            "INFO",
        )
        _close_image(image)


def _save_image(image, fig_path) -> None:
    if isinstance(image, Figure):
        image.savefig(fig_path)
        return
    if isinstance(image, Image):
        image.save(fig_path)
        return
    raise ValueError("Unrecognized figure type")


def _close_image(image) -> None:
    if isinstance(image, Figure):
        plt.close(image)
        return
    if isinstance(image, Image):
        image.close()
        return
    raise ValueError("Unrecognized figure type")


if __name__ == "__main__":
    make_briefing_figures("20240731")  # for testing
