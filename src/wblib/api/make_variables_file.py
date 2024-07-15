"""Generate variables yaml in briefings folder."""

import pathlib
from typing import Callable

import yaml

from wblib.api._logger import logger
from wblib.services import get_briefing_path
from wblib.services import get_expected_figures


def create_variables_yaml(date: str, flight_id: str, location: str,
                          logger: Callable = logger) -> None:
    variables_nml = get_expected_figures(date, location, flight_id)
    variables_file_name = f"_variables_{date}.yml"
    output_path = pathlib.Path(get_briefing_path(date))
    logger(f"Creating variables file in '{output_path}'", "INFO")
    outfile_yml = output_path / variables_file_name
    softlink_yml = "_variables.yml"
    with open(outfile_yml, "w") as outfile:
        yaml.dump(variables_nml, outfile, default_flow_style=False)
    logger(f"Variables file created in '{output_path}'", "INFO")
    _create_softlink(outfile_yml, softlink_yml)
    logger(f"Variables file linked to '{softlink_yml}'", "INFO")


def _create_softlink(file, link) -> None:
    file_a_path = pathlib.Path(file)
    link_path = pathlib.Path(link)
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    link_path.symlink_to(file_a_path)


if __name__ == "__main__":
    from wblib.api._logger import logger
    create_variables_yaml("20240101", "FX2", "Barbados", logger)
