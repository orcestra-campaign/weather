"""Generate variables yaml in briefings folder."""

import os
import sys
import pathlib

import yaml

from wblib.services import get_briefing_path
from wblib.services import get_expected_figures


def main(date = None, flight_id = None, location = None) -> None:
    if not date:
        date = sys.argv[1]
    if not flight_id:
        flight_id = sys.argv[2]
    if not location:
        location = sys.argv[3]

    outpath = pathlib.Path(get_briefing_path(date))
    variables_nml = get_expected_figures(date, location, flight_id)
    variables_file_name = f"_variables_{date}.yml"
    outfile_yml = outpath / variables_file_name
    softlink_yml = "_variables.yml"
    print(os.getcwd())
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
    # main()
    main("20240101", "PERCUSION_CV_FL00", "Barbados") # for testing





