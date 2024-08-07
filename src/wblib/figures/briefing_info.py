"""Functions to work with IFS forecasts in healpix format."""
import pandas as pd


FORECAST_PUBLISH_LAG = "8h"
FORECAST_PUBLISH_FREQ = "12h"


def get_valid_time(
    briefing_time: pd.Timestamp, briefing_lead_hours: str
) -> pd.Timestamp:
    """Valid time for when the briefing info applies."""
    briefing_delta = pd.Timedelta(hours=int(briefing_lead_hours[:-1]))
    valid_time = briefing_time + briefing_delta
    return valid_time


def get_latest_forecast_issue_time(briefing_time: pd.Timestamp):
    current_time = pd.Timestamp.now("UTC")
    publish_lag = pd.Timedelta(FORECAST_PUBLISH_LAG)
    publish_freq = pd.Timedelta(FORECAST_PUBLISH_FREQ)
    if current_time >= briefing_time + publish_lag:
        issued_time = briefing_time
    if current_time < briefing_time + publish_lag:
        issued_time = current_time.floor(FORECAST_PUBLISH_FREQ) - publish_freq
    return issued_time


def get_dates_of_previous_initializations(
    issue_time: pd.Timestamp,
    number: int=5,
) -> list[pd.Timestamp]:
    day = pd.Timedelta("1D")
    dates = [(issue_time.floor("1D") - i * day) for i in
             range(0, number)]
    dates.reverse()
    return dates