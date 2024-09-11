"""Generate and save the report figures."""

from typing import Callable
from PIL.Image import Image
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import pandas as pd

from wblib.api._utils import TIME_ZONE_STR, _load_variables_yaml
from wblib.services.get_figures import generate_external_inst_figures
from wblib.services.get_figures import generate_external_lead_figures
from wblib.services.get_figures import generate_internal_figures
from wblib.services.get_paths import get_briefing_path
from wblib.api._logger import logger

from orcestra.meteor import get_meteor_track

def make_briefing_figures(date: str, logger: Callable = logger) -> None:
    logger("Generating briefing figures", "INFO")
    variables_dict = _load_variables_yaml(date, logger)
    external_location = variables_dict["location"]
    current_time = pd.Timestamp.now(TIME_ZONE_STR)
    briefing_time = pd.Timestamp(date, tz=TIME_ZONE_STR)
    sattracks_fc_date = variables_dict["sattracks_fc_date"]
    sattracks_fc_time = pd.Timestamp(sattracks_fc_date, tz=TIME_ZONE_STR)
    meteor_track = get_meteor_track(deduplicate_latlon=True)

    _internal_plots(
        date,
        logger,
        variables_dict,
        current_time,
        briefing_time,
        sattracks_fc_time,
        meteor_track,
    )
    _external_lead_time_plots(
        date,
        logger,
        variables_dict,
        current_time,
        briefing_time,
        sattracks_fc_time,
    )
    _external_instantaneous_plots(
        date,
        logger,
        variables_dict,
        external_location,
        current_time,
        briefing_time,
        sattracks_fc_time,
        meteor_track,
    )


def _internal_plots(
    date,
    logger,
    variables_dict,
    current_time,
    briefing_time,
    sattracks_fc_time,
    meteor_track,
):
    logger(f"Internal figure time set to {briefing_time}", "INFO")
    for product, lead_time, image in generate_internal_figures(
        briefing_time,
        current_time,
        sattracks_fc_time,
        meteor_track,
        logger,
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


def _external_lead_time_plots(
    date,
    logger,
    variables_dict,
    current_time,
    briefing_time,
    sattracks_fc_time,
):
    logger(f"External lead time figure time set to {briefing_time}", "INFO")
    for product, lead_time, image in generate_external_lead_figures(
        briefing_time,
        current_time,
        sattracks_fc_time,
        logger,
    ):
        fig_path = variables_dict["plots"]["external_lead"][product][lead_time]
        fig_path = get_briefing_path(date) + "/" + fig_path
        _save_image(image, fig_path)
        _close_image(image)
        logger(
            f"Saved external lead time figure '{product}' for "
            f"'{briefing_time}' and '{lead_time}' in '{fig_path}'.",
            "INFO",
        )
        _close_image(image)


def _external_instantaneous_plots(
    date,
    logger,
    variables_dict,
    external_location,
    current_time,
    briefing_time,
    sattracks_fc_time,
    meteor_track,
):
    logger(f"External instantaneous figure time set to {current_time}", "INFO")
    for product, image in generate_external_inst_figures(
        external_location,
        current_time,
        briefing_time,
        sattracks_fc_time,
        meteor_track,
        logger,
    ):
        fig_path = variables_dict["plots"]["external_inst"][product]
        fig_path = get_briefing_path(date) + "/" + fig_path
        _save_image(image, fig_path)
        _close_image(image)
        logger(
            f"Saved external instantaneous figure '{product}' in "
            + f"'{fig_path}'.",
            "INFO",
        )


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
    make_briefing_figures("20240906")  # for testing
