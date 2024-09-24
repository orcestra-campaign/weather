"""Plot ITCZ edges based on the IWV from ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import xarray as xr

import matplotlib
from matplotlib.figure import Figure
import seaborn as sns

from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.hifs import HifsForecasts
from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS
from wblib.figures.meteor_pos import plot_meteor_latest_position_in_ifs_forecast

ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_MAX = 70  # mm
ICWV_MIN = 45  # mm
ICWV_COLORMAP = "Blues"
ICWV_CATALOG_VARIABLE = "tcwv"
REFDATE_COLORBAR = [
    "#ff0000",
    "#bf0000",
    "#800000",
    "#400000",
    "#000000"
] # the ordering of the colors indicate the latest available refdate
REFDATE_LINEWIDTH = [1, 1.1, 1.2, 1.3, 1.5]


def iwv_itcz_edges(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
    meteor_track: xr.Dataset,
    hifs: HifsForecasts,
) -> Figure:
    issue_time, forecast = hifs.get_forecast(
        ICWV_CATALOG_VARIABLE, briefing_time, lead_hours, current_time,
    )
    forecasts = hifs.get_previous_forecasts(
        ICWV_CATALOG_VARIABLE, briefing_time, lead_hours, current_time,
        issue_time,
    )
    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time,
                                sattracks_fc_time, "iwv_itcz_edges", ax)
    _draw_icwv_contours_for_previous_forecasts(forecasts, ax)
    im = _draw_icwv_current_forecast(forecast, ax)
    fig.colorbar(im, label="IWV / kg m$^{-2}$", shrink=0.8)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, lead_hours, ax,
                                color="C1")
    plot_meteor_latest_position_in_ifs_forecast(
        briefing_time, lead_hours, ax, meteor=meteor_track)
    matplotlib.rc_file_defaults()
    return fig


def _draw_icwv_contours_for_previous_forecasts(forecasts, ax):
    for i, (_, forecast) in enumerate(forecasts):
        color = REFDATE_COLORBAR[i]
        linewidth = REFDATE_LINEWIDTH[i]
        egh.healpix_contour(
            forecast,
            ax=ax,
            levels=[ICWV_ITCZ_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )


def _draw_icwv_current_forecast(forecast, ax):
    im = egh.healpix_show(
        forecast,
        ax=ax,
        method="linear",
        alpha=0.75,
        cmap=ICWV_COLORMAP,
        vmin=ICWV_MIN,
        vmax=ICWV_MAX,
    )
    return im


if __name__ == "__main__":
    import intake
    from orcestra.meteor import get_meteor_track
    
    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 9, 24).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 9, 24, 12).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 9, 24).tz_localize("UTC")
    meteor_track = get_meteor_track(deduplicate_latlon=True)
    fig = iwv_itcz_edges(briefing_time1, "12H", current_time1,
                         sattracks_fc_time1, meteor_track, hifs)
    fig.savefig("test_icwv_156H.png")
