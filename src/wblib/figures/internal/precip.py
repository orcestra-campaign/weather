"""Plot the cloud forecast from ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import xarray as xr

import matplotlib
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.colors import BoundaryNorm

import seaborn as sns
import cmocean as cmo

from wblib.figures.hifs import HifsForecasts
from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS
from wblib.figures.meteor_pos import plot_meteor_latest_position_in_ifs_forecast

TP_THRESHOLD = 50  # mm
TCWV_THRESHOLD = 48  # mm
TP_STEPS = [0, 5, 25, 50, 75, 100]
TP_COLORMAP = cmo.cm.rain
DATA_CATALOG_VARIABLE = ["tp", "tcwv"]
REFDATE_COLORBAR_TCWV = [
    "#ff0000",
    "#bf0000",
    "#800000",
    "#400000",
    "#000000"
] # the ordering of the colors indicate the latest available refdate
REFDATE_LINEWIDTH = [1, 1.1, 1.2, 1.3, 1.5]

def precip(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
    meteor_track: xr.Dataset,
    hifs: HifsForecasts,
) -> Figure:
    # retrieve the forecast data
    issue_time, precip = hifs.get_forecast(
        DATA_CATALOG_VARIABLE[0],
        briefing_time,
        lead_hours,
        current_time,
        differentiate=True,
        differentiate_unit="D",
    )
    precip = 1000 * precip
    tcwv_forecasts = hifs.get_previous_forecasts(
        DATA_CATALOG_VARIABLE[1],
        briefing_time,
        lead_hours,
        current_time,
        issue_time,
        number=5,
    )
    # plotting
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time,
                                sattracks_fc_time, "precip", ax)
    _draw_tcwv_contours_for_previous_forecasts(tcwv_forecasts, ax)
    _draw_current_forecast(precip, fig, ax)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, lead_hours, ax,
                                color="C1", show_waypoints=False)
    plot_meteor_latest_position_in_ifs_forecast(
        briefing_time, lead_hours, ax, meteor=meteor_track)
    matplotlib.rc_file_defaults()
    return fig


def _draw_tcwv_contours_for_previous_forecasts(tcwv_forecasts, ax):
    issued_times = []
    for i, (issued_time_, tcwv_forecasts) in enumerate(tcwv_forecasts):
        color = REFDATE_COLORBAR_TCWV[i]
        linewidth = REFDATE_LINEWIDTH[i]
        im = egh.healpix_contour(
            tcwv_forecasts,
            ax=ax,
            levels=[TCWV_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )
        issued_times.append(issued_time_)


def _draw_current_forecast(precip, fig, ax):
    im = egh.healpix_show(
        precip,
        ax=ax,
        method="linear",
        norm=BoundaryNorm(TP_STEPS, ncolors=TP_COLORMAP.N, clip=True),
        cmap=TP_COLORMAP,
    )
    fig.colorbar(im, label="mean precip. rate / mm day$^{-1}$", shrink=0.8)


if __name__ == "__main__":
    import intake
    from orcestra.meteor import get_meteor_track

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 8, 23).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 23, 8).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 8, 21).tz_localize("UTC")
    meteor_track = get_meteor_track(deduplicate_latlon=True)
    fig = precip(briefing_time1, "12H", current_time1,
                 sattracks_fc_time1, meteor_track, hifs)
    fig.savefig("test_precip.png")
