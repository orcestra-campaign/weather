"""Get the figures expected by the Quarto report."""

from datetime import datetime
import pandas as pd
from wblib.services.get_paths import get_figure_path

from wblib.services._define_figures import EXTERNAL_INST_PLOTS
from wblib.services._define_figures import EXTERNAL_LEAD_PLOTS
from wblib.services._define_figures import INTERNAL_PLOTS
from wblib.services._define_figures import PLOTS_LEADTIMES

MSS_PLOTS_SIDE_VIEW = ["relative_humidity", "cloud_cover"]
ALLOWED_LOCATIONS = ["Barbados", "Sal"]


def get_expected_figures(
    date: str, location: str, flight_id: str, sattracks_fc_date: str
) -> dict:
    """Returns a dictionary with the expected figures for the briefing."""
    _validate_date(date)
    _validate_date(sattracks_fc_date)
    _validate_location(location)
    output_path = get_figure_path()
    variables_nml = {
        "flight_id": flight_id,
        "location": location,
        "date": date,
        "sattracks_fc_date": sattracks_fc_date,
        "valid_dates": _get_valid_dates(date, PLOTS_LEADTIMES),
        "plots": {
            "external_inst": get_expected_external_inst_figures(output_path),
            "external_lead": get_expected_external_lead_figures(output_path,
                                                                date),
            "internal": get_expected_internal_figures(output_path, date),
            "mss_side_view": get_expected_mss_side_view_figures(
                output_path, date, flight_id
            ),
        },
    }
    return variables_nml

def _get_valid_dates(date, lead_times) -> dict:
    valid_dates = dict()
    for lead in PLOTS_LEADTIMES:
        temp_time = (pd.Timestamp(date, tz='UTC') 
                     + pd.Timedelta(hours=int(lead[:-1]))).strftime('%Y-%m-%d %H:%M') 
        valid_dates[lead] = str(temp_time) + ' UTC'
    return valid_dates

def get_expected_external_inst_figures(figures_output_path) -> dict:
    figures = {
        product: f"{figures_output_path}/external_inst/{product}.png"
        for product in EXTERNAL_INST_PLOTS.keys()
    }
    return figures


def get_expected_external_lead_figures(figures_output_path, date) -> dict:
    figures = dict()
    for product in EXTERNAL_LEAD_PLOTS.keys():
        figures[product] = dict()
        for lead_time in PLOTS_LEADTIMES:
            figures[product][
                lead_time
            ] = (f"{figures_output_path}/external_lead/IFS_{date}+{lead_time}" +
                 f"_{product}.png")
    return figures


def get_expected_internal_figures(figures_output_path, date) -> dict:
    figures = dict()
    for product in INTERNAL_PLOTS.keys():
        figures[product] = dict()
        for lead_time in PLOTS_LEADTIMES:
            figures[product][
                lead_time
            ] = (f"{figures_output_path}/internal/IFS_{date}+{lead_time}_" +
                 f"{product}.png")
    return figures


def get_expected_mss_side_view_figures(
    figures_output_path, date, flight_id
) -> dict:
    figures = {
        "IFS": {
            product: f"{figures_output_path}/mss/MSS_{flight_id}_sideview_IFS_{date}_{product}.png"
            for product in MSS_PLOTS_SIDE_VIEW
        },
        "ICON": {
            product: f"{figures_output_path}/mss/MSS_{flight_id}_sideview_ICON_{date}_{product}.png"
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
    except ValueError as exc:
        raise ValueError("Incorrect data format, should be YYYYMMDD") from exc
