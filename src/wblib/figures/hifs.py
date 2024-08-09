"""Functions to work with IFS forecasts in healpix format."""

import copy
from typing import Iterable
import numpy as np
import pandas as pd
import xarray as xr
import intake
import easygems.healpix as egh

from wblib.figures.briefing_info import get_valid_time


FORECAST_PUBLISH_LAG = "8h"
FORECAST_PUBLISH_FREQ = "12h"
FORECAST_QUERY_MAX_ATTEMPS = 6  # last 6 initializations


class HifsForecasts:
    def __init__(self, catalog: intake.Catalog):
        self.catalog = catalog

    def get_forecast(
        self,
        variable: str,
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        differentiate: bool = False,
        differentiate_unit: str = "s",
    ) -> tuple[pd.Timestamp, xr.DataArray]:
        issue_time, forecast = self._get_forecast(
            variable,
            briefing_time,
            current_time,
            differentiate,
            differentiate_unit,
        )
        valid_time = get_valid_time(briefing_time, lead_hours)
        valid_time = valid_time.tz_localize(None)
        forecast = forecast.sel(time=valid_time)
        return issue_time, forecast

    def get_previous_forecasts(
        self,
        variable: str,
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        number: int = 5,
        differentiate: bool = False,
        differentiate_unit: str = "s",
    ) -> Iterable[tuple[pd.Timestamp, xr.DataArray]]:
        valid_time = get_valid_time(briefing_time, lead_hours)
        valid_time = valid_time.tz_localize(None)
        briefing_times = _get_dates_of_previous_briefings(
            briefing_time, number
        )
        for briefing_time in briefing_times:
            issue_time, forecast = self._get_forecast(
                variable,
                briefing_time,
                current_time,
                differentiate,
                differentiate_unit,
            )
            forecast = forecast.sel(time=valid_time)
            yield issue_time, forecast

    def _get_forecast(
        self,
        variable,
        briefing_time,
        current_time,
        differentiate,
        differentiate_unit,
    ) -> tuple[pd.Timestamp, xr.DataArray]:
        issue_time, forecast_dataset = _load_forecast_dataset(
            briefing_time, current_time, self.catalog
        )
        forecast = forecast_dataset[variable]
        if differentiate:
            forecast = _accumulated_to_instantaneous(
                issue_time, forecast, differentiate_unit
            )
        return issue_time, forecast


def _load_forecast_dataset(
    briefing_time: pd.Timestamp,
    current_time: pd.Timestamp,
    catalog: intake.Catalog,
) -> tuple[pd.Timestamp, xr.Dataset]:
    publish_freq = pd.Timedelta(FORECAST_PUBLISH_FREQ)
    query_forecast_attempts = FORECAST_QUERY_MAX_ATTEMPS
    issue_time = expected_issue_time(briefing_time, current_time)
    while query_forecast_attempts:
        try:
            forecast = (
                catalog.HIFS(
                    refdate=issue_time.strftime("%Y-%m-%d"),
                    reftime=issue_time.strftime("%H"),
                )
                .to_dask()
                .pipe(egh.attach_coords)
            )
            return issue_time, forecast
        except KeyError:
            query_forecast_attempts -= 1
            issue_time = issue_time - publish_freq
    msg = f"No forecasts available for brifieng_time '{briefing_time}'."
    raise KeyError(msg)


def expected_issue_time(
    briefing_time: pd.Timestamp, current_time: pd.Timestamp
) -> pd.Timestamp:
    if current_time >= briefing_time:
        return copy.deepcopy(briefing_time)
    else:
        return current_time.floor(FORECAST_PUBLISH_FREQ)


def _get_dates_of_previous_briefings(
    briefing_time: pd.Timestamp,
    number: int = 5,
) -> list[pd.Timestamp]:
    day = pd.Timedelta("1D")
    dates = [(briefing_time.floor("1D") - i * day) for i in range(0, number)]
    dates.reverse()
    return dates


def _accumulated_to_instantaneous(
    issue_time: pd.Timestamp,
    accumulated: xr.DataArray,
    differentiate_unit: str = "s",
) -> xr.DataArray:
    # first time step
    time_0 = issue_time.tz_localize(None).to_numpy()
    time_1 = accumulated.time.isel(time=0)
    dtime_1 = (time_1 - time_0) / np.timedelta64(1, differentiate_unit)
    dacc_1 = accumulated.isel(time=0)
    instantaneous_1 = dacc_1 / dtime_1
    # other time steps
    dtime = accumulated.time.diff("time") / np.timedelta64(1, differentiate_unit)
    dacc = accumulated.diff("time")
    instantaneous_other = dacc / dtime
    instantaneous = xr.concat([instantaneous_1, instantaneous_other], "time")
    return instantaneous


if __name__ == "__main__":
    import intake

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 8, 7).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 15).tz_localize("UTC")

    issue_time, dttr = hifs.get_forecast(
        "ttr", briefing_time1, "108H", current_time1, differentiate=True
    )
