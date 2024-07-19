"""Get paths of the weather briefing library."""

from datetime import datetime


def get_briefing_path(date) -> str:
    _validate_date(date)
    return f"briefings/{date}"


def get_figure_path(date) -> str:
    briefing_path = get_briefing_path(date)
    figures_output_path = f"{briefing_path}/fig"
    return figures_output_path


def get_briefing_paths(date: str) -> list[str]:
    figures_output_path = get_figure_path(date)
    briefing_paths = [
        f"{figures_output_path}",
        f"{figures_output_path}/internal",
        f"{figures_output_path}/external",
        f"{figures_output_path}/mss",
    ]
    return briefing_paths


def get_variables_path(date: str) -> str:
    variables_path = get_briefing_path(date) + f"/_variables_{date}.yml"
    return variables_path


def _validate_date(date_str: str) -> None:
    """Validate the date of the weather briefing provided by the user."""
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYYMMDD")