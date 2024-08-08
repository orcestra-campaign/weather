"""Generate figures with the weather briefing library."""

from typing import Callable, Iterator, Union
from PIL import Image as img
from matplotlib.figure import Figure
import pandas as pd

import intake

from wblib.figures.hifs import HifsForecasts
from wblib.services._define_figures import EXTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS_LEADTIMES


Image = Union[img.Image, Figure]

INTAKE_CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"


def generate_external_figures(
    current_location: str, current_time: pd.Timestamp, logger: Callable
) -> Iterator[tuple[str, Image]]:
    for product, function in EXTERNAL_PLOTS.items():
        if function is None:
            _warn_function_is_not_defined(product, logger)
            continue
        try:
            figure = function(current_time, current_location)
            yield (product, figure)
        except Exception as error:
            msg = (
                f"Can not generate {product} with '{current_time}'. "
                "Please provide it manually or debug the code."
            )
            logger(msg, "ERROR")
            print(error)
            continue


def generate_internal_figures(
    briefing_time: pd.Timestamp, current_time: pd.Timestamp, logger: Callable
) -> Iterator[tuple[str, str, Image]]:
    catalog = intake.open_catalog(INTAKE_CATALOG_URL)
    hifs = HifsForecasts(catalog)
    for product, function in INTERNAL_PLOTS.items():
        if function is None:
            _warn_function_is_not_defined(product, logger)
            continue
        for lead_hours in INTERNAL_PLOTS_LEADTIMES:
            try:
                figure = function(
                    briefing_time, lead_hours, current_time, hifs
                )
                yield (product, lead_hours, figure)
            except Exception as error:
                msg = (
                    f"Can not generate {product} with '{current_time}' "
                    f"and '{lead_hours}'. Please provide it manually or "
                    "debug the code."
                )
                logger(msg, "ERROR")
                print(error)
                continue


def _warn_function_is_not_defined(product, logger):
    msg = f"Undefined function for '{product}' product."
    logger(msg, "ERROR")
