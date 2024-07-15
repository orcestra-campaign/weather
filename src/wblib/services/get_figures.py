"""Generate figures with the weather briefing library."""


from typing import Callable
from PIL import Image as img

from wblib.services._define_figures import EXTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS_LEADTIMES


def generate_external_figures()-> dict[str, img.Image]:
    figures = dict()
    for product, function in EXTERNAL_PLOTS.items():
        if function is None:
            _warn_function_is_not_defined(product)
            continue
        figures[product] = function()
    return figures


def generate_internal_figures() -> dict[str, img.Image]:
    figures = dict()
    for product, function in INTERNAL_PLOTS.items():
        if function is None:
            _warn_function_is_not_defined(product)
            continue
        figures[product] = dict()
        for lead_time in INTERNAL_PLOTS_LEADTIMES:
            figures[product][lead_time] = function(lead_time)
    return figures


def _warn_function_is_not_defined(product):
    msg = f"Undefined function for '{product}' product."
    print(msg)

