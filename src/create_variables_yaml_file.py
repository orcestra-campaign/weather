"""Generate variables yaml in briefings folder."""

import os
import sys
import pathlib

import yaml

from wblib.services import get_briefing_path
from wblib.services import get_expected_figures


def create_variables_yaml(date=None, flight_id=None, location=None) -> None:
    if not date:
        date = sys.argv[1]
    if not flight_id:
        flight_id = sys.argv[2]
    if not location:
        location = sys.argv[3]
    variables_nml = get_expected_figures(date, location, flight_id)
    variables_file_name = f"_variables_{date}.yml"
    output_path = pathlib.Path(get_briefing_path(date))
    outfile_yml = output_path / variables_file_name
    softlink_yml = "_variables.yml"
    with open(outfile_yml, "w") as outfile:
        yaml.dump(variables_nml, outfile, default_flow_style=False)
    _create_softlink(outfile_yml, softlink_yml)


def _create_softlink(file, link):
    file_a_path = pathlib.Path(file)
    link_path = pathlib.Path(link)
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    link_path.symlink_to(file_a_path)


if __name__ == "__main__":
    # create_variables_yaml()
    create_variables_yaml(
        "20240101", "FX2", "Barbados"
    )  # for testing

