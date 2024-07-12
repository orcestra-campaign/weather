"""General services of the weather briefing library."""

from datetime import datetime

from wblib.services.config import ALLOWED_LOCATIONS
from wblib.services.config import get_briefing_relative_path
from wblib.services.config import get_figures_relative_path
from wblib.services.config import get_expected_external_figures
from wblib.services.config import get_expected_internal_figures
from wblib.services.config import get_expected_mss_side_view_figures


def get_briefing_path(date) -> str:
    """Get the output folder of the weather briefing."""
    _validate_date(date)
    output_path = get_briefing_relative_path(date)
    return output_path


def get_briefing_paths(date) -> list[str]:
    _validate_date(date)
    figures_output_path = get_figures_relative_path(date)
    briefing_paths = [
        f"{figures_output_path}",
        f"{figures_output_path}/internal",
        f"{figures_output_path}/external",
        f"{figures_output_path}/mss",
    ]
    return briefing_paths


def get_expected_figures(date, location, flight_id) -> dict:
    """Returns a dictionary with the expected figures for the briefing."""
    _validate_date(date)
    _validate_location(location)
    init = _find_latest_available_init(date)
    output_path = get_figures_relative_path(date)
    variables_nml = {
        "flight_id": flight_id,
        "location": location,
        "date": {
            "yyyymmdd": date,
        },
        "plots": {
            "external": get_expected_external_figures(output_path),
            "internal": get_expected_internal_figures(output_path, init),
            "mss_side_view": get_expected_mss_side_view_figures(
                output_path, init, flight_id
            ),
        },
    }
    return variables_nml


def _validate_location(location):
    """Check that a correct location was provided."""
    msg = f"Incorrect location, should be {ALLOWED_LOCATIONS}!"
    if location not in ALLOWED_LOCATIONS:
        raise ValueError(msg)


def _validate_date(date_str):
    """Validate the date of the weather briefing provided by the user."""
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYYMMDD")


def _find_latest_available_init(date_str):
    expected_latest_init = date_str + "T0000Z"
    return expected_latest_init