"""Generate figures with the weather briefing library."""


from matplotlib.figure import Figure

from wblib.figures.external.goes import

FIGURE_FUNCTIONS_DICT = {
        "external": {
            "":,
            "":
        }
    }


def generate_figures(figures: dict) -> list[Figure]:
    ...

def generate_external_figures()-> list[Figure]:
    ...


def generate_external_figure() -> Figure:
    ...
