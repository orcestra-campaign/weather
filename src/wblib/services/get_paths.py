"""Get paths of the weather briefing library."""

from datetime import datetime
from importlib import resources

import wblib


TEMPLATE_FILE = "template.qmd"


def get_briefing_path(date) -> str:
    _validate_date(date)
    return f"briefings/{date}"


def get_figure_path(date) -> str:
    figures_output_path = "fig"
    return figures_output_path


def get_briefing_paths(date: str) -> list[str]:
    figures_output_path = get_briefing_path(date) + "/" + get_figure_path(date)
    briefing_paths = [
        f"{figures_output_path}",
        f"{figures_output_path}/internal",
        f"{figures_output_path}/external",
        f"{figures_output_path}/mss",
    ]
    return briefing_paths


def get_variables_path(date: str) -> str:
    variables_path = get_briefing_path(date) + "/_metadata.yml"
    return variables_path


def get_briefing_template_path() -> str:
    briefing_template_path = str(resources.files(wblib) / TEMPLATE_FILE)
    return briefing_template_path


def _validate_date(date_str: str) -> None:
    """Validate the date of the weather briefing provided by the user."""
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYYMMDD")
