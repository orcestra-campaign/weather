"""Functions to work with IFS forecasts in healpix format."""
import pandas as pd


FORECAST_PUBLISH_LAG = "8h"
FORECAST_PUBLISH_FREQ = "12h"


def get_latest_forecast_issue_time(briefing_time: pd.Timestamp):
    current_time = pd.Timestamp.now("UTC")
    publish_lag = pd.Timedelta(FORECAST_PUBLISH_LAG)
    publish_freq = pd.Timedelta(FORECAST_PUBLISH_FREQ)
    if current_time >= briefing_time + publish_lag:
        issued_time = briefing_time
    if current_time < briefing_time + publish_lag:
        issued_time = current_time.floor(FORECAST_PUBLISH_FREQ) - publish_freq
    return issued_time


def get_dates_of_N_previous_initializations(
    issue_time: pd.Timestamp,
    N_previous_forecasts: int=5,
) -> list[pd.Timestamp]:
    day = pd.Timedelta("1D")
    dates = [(issue_time.floor("1D") - i * day) for i in
             range(0, N_previous_forecasts)]
    dates.reverse()
    return dates