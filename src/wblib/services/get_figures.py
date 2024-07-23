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
        try:
            figures[product] = function(current_time)
        except Exception as error:
            msg = (f"Can not generate {product} with '{current_time}'. "
                   "Please provide it manually or debug the code.")
            logger(msg, "ERROR")
            print(error)
    return figures


def generate_internal_figures(current_time: pd.Timestamp,
                              logger: Callable) -> dict[str, dict[str, Image]]:
    figures = dict()
    for product, function in INTERNAL_PLOTS.items():
        if function is None:
            _warn_function_is_not_defined(product, logger)
            continue
        figures[product] = dict()
        for lead_hours in INTERNAL_PLOTS_LEADTIMES:
            try:
                figure = function(current_time, lead_hours)
                figures[product][lead_hours] = figure
            except Exception as error:
                msg = (f"Can not generate {product} with '{current_time}' "
                       f"and '{lead_hours}'. Please provide it manually or "
                       "debug the code.")
                logger(msg, "ERROR")
                print(error)
    return figures


def _warn_function_is_not_defined(product, logger):
    msg = f"Undefined function for '{product}' product."
    logger(msg, "ERROR")


def catch_ignore_warn(function, logger):
    def wrap(*args, **kwargs):
        try:
            figure = function(*args, **kwargs)
            logger(f"Ran figure function '{function.__name__}'", "INFO")
            return figure
        except:
            logger(f"Ran figure function '{function.__name__}'", "INFO")
