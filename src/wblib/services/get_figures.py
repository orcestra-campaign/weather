"""Generate figures with the weather briefing library."""


from typing import Callable, Union
from PIL import Image as img
from matplotlib.figure import Figure
import pandas as pd

from wblib.services._define_figures import EXTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS_LEADTIMES


Image = Union[img.Image, Figure]


def generate_external_figures(current_time: pd.Timestamp,
                              logger: Callable)-> dict[str, Image]:
    figures = dict()
    for product, function in EXTERNAL_PLOTS.items():
        if function is None:
            _warn_function_is_not_defined(product, logger)
            continue
        figures[product] = function(current_time)
    return figures


def generate_internal_figures(current_time: pd.Timestamp,
                              logger: Callable) -> dict[str, Image]:
    figures = dict()
    for product, function in INTERNAL_PLOTS.items():
        if function is None:
            _warn_function_is_not_defined(product, logger)
            continue
        figures[product] = dict()
        for lead_time in INTERNAL_PLOTS_LEADTIMES:
            figures[product][lead_time] = function(current_time, lead_time)
    return figures


def _warn_function_is_not_defined(product, logger):
    msg = f"Undefined function for '{product}' product."
    logger(msg, "ERROR")

