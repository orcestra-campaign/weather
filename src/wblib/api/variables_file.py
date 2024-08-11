"""Generate variables yaml in briefings folder."""

import pathlib
from typing import Callable

import yaml

from wblib.api._logger import logger
from wblib.services import get_briefing_path
from wblib.services import get_expected_figures


def make_briefing_variables(
    date: str,
    flight_id: str,
    location: str,
    sattracks_fc_date: str,
    logger: Callable = logger,
) -> None:
    variables_nml = get_expected_figures(
        date, location, flight_id, sattracks_fc_date
    )
    variables_file_name = f"_metadata.yml"
    output_path = pathlib.Path(get_briefing_path(date))
    outfile_yml = output_path / variables_file_name
    with open(outfile_yml, "w") as outfile:
        yaml.dump(
            variables_nml, outfile, default_flow_style=False, sort_keys=False
        )
    logger(f"Variables file created in '{output_path}'", "INFO")


if __name__ == "__main__":
    from wblib.api._logger import logger

    make_briefing_variables("20240101", "FX2", "Barbados", logger)
