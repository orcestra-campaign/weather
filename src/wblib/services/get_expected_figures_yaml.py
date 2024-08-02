"""Get the figures expected by the Quarto report."""

from datetime import datetime

from wblib.services.get_paths import get_figure_path

from wblib.services._define_figures import EXTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS_LEADTIMES


MSS_PLOTS_SIDE_VIEW = ["relative_humidity", "cloud_cover"]
ALLOWED_LOCATIONS = ["Barbados", "Sal"]


def get_expected_figures(
    date: str, location: str, flight_id: str, sattracks_date: str
) -> dict:
    """Returns a dictionary with the expected figures for the briefing."""
    _validate_date(date)
    _validate_date(sattracks_date)
    _validate_location(location)
    init = _find_latest_available_init(date)
    output_path = get_figure_path(date)
    date2 = _change_date_format(date)
    variables_nml = {
        "flight_id": flight_id,
        "location": location,
        "date": {"yyyymmdd": date, "yyyy-mm-dd": date2},
        "sattracks_date": sattracks_date,
        "plots": {
            "external": get_expected_external_figures(output_path),
            "internal": get_expected_internal_figures(output_path, init),
            "mss_side_view": get_expected_mss_side_view_figures(
                output_path, init, flight_id
            ),
        },
    }
    return variables_nml


def get_expected_external_figures(figures_output_path) -> dict:
    figures = {
        product: f"{figures_output_path}/external/{product}.png"
        for product in EXTERNAL_PLOTS.keys()
    }
    return figures


def get_expected_internal_figures(figures_output_path, init) -> dict:
    figures = dict()
    for product in INTERNAL_PLOTS.keys():
        figures[product] = dict()
        for lead_time in INTERNAL_PLOTS_LEADTIMES:
            figures[product][
                lead_time
            ] = f"{figures_output_path}/internal/IFS_{init}+{lead_time}_{product}.png"
    return figures


def get_expected_mss_side_view_figures(
    figures_output_path, init, flight_id
) -> dict:
    figures = {
        "IFS": {
            product: f"{figures_output_path}/mss/MSS_{flight_id}_sideview_IFS_{init}_{product}.png"
            for product in MSS_PLOTS_SIDE_VIEW
        },
        "ICON": {
            product: f"{figures_output_path}/mss/MSS_{flight_id}_sideview_ICON_{init}_{product}.png"
            for product in MSS_PLOTS_SIDE_VIEW
        },
    }
    return figures


def _validate_location(location: str) -> None:
    """Check that a correct location was provided."""
    msg = f"Incorrect location, should be {ALLOWED_LOCATIONS}!"
    if location not in ALLOWED_LOCATIONS:
        raise ValueError(msg)


def _validate_date(date_str: str) -> None:
    """Validate the date of the weather briefing provided by the user."""
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYYMMDD")


def _change_date_format(date_str: str) -> str:
    new_date_str = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8]
    return new_date_str


def _find_latest_available_init(date_str: str) -> str:
    expected_latest_init = date_str + "T0000Z"
    return expected_latest_init
