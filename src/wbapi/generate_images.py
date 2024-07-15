"""Generate and save the report figures."""

from pathlib import Path

import yaml
from wblib.services.get_figures import generate_external_figures
from wblib.services.get_figures import generate_internal_figures
from wblib.services.get_paths import get_briefing_path


def generate_images(date: str):
    variables_dict = _load_variables_yaml(date)
    # external
    external_figures = generate_external_figures()
    for name, image in external_figures.items():
        fig_name = variables_dict["plots"]["external"][name]
        print(fig_name)
        image.save(fig_name)
    # internal
    internal_figures = generate_internal_figures()
    for name, image in internal_figures.items():
        fig_name = variables_dict["plots"]["internal"][name]
        image.save(fig_name)

def _load_variables_yaml(date: str) -> dict:
    variables_path = Path(get_briefing_path(date)) / f"_variables_{date}.yml"
    with open(variables_path, "r") as stream:
        variables_dict = yaml.safe_load(stream)
    return variables_dict

if __name__ == "__main__":
    # create_variables_yaml()
    generate_images("20240101")  # for testing

