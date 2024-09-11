"""Plot ITCZ edges based on the IWV from ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import xarray as xr
import warnings

import matplotlib
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import seaborn as sns

from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE, get_climatology_path
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.hifs import HifsForecasts, get_valid_time
from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS
from wblib.figures.meteor_pos import plot_meteor_latest_position_in_ifs_forecast

ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_CATALOG_VARIABLE = "tcwv"

def iwv_itcz_edges_enfo(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
    meteor_track: xr.Dataset,
    hifs: HifsForecasts,
) -> Figure:
    issue_time_oper, forecast_oper = hifs.get_forecast(
        ICWV_CATALOG_VARIABLE, briefing_time, lead_hours, current_time,
        forecast_type="oper"
    )
    issue_time_enfo, forecast_enfo = hifs.get_forecast(
        ICWV_CATALOG_VARIABLE, briefing_time, lead_hours, current_time,
        forecast_type="enfo"
    )
    _validate_issue_times(issue_time_oper, issue_time_enfo)
    climatology = _get_rolling_daily_climatology(
        ICWV_CATALOG_VARIABLE, briefing_time, lead_hours
        )
    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time_oper,
                                sattracks_fc_time, "iwv_itcz_edges_enfo", ax)
    plot1 = _draw_icwv_enfo_contours(forecast_enfo, ax)
    plot2 = _draw_icwv_enfo_mean_contour(forecast_enfo, ax)
    plot3 = _draw_icwv_oper_contour(forecast_oper, ax)
    plot4 = _draw_icwv_ERA5_contour(climatology, ax)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, lead_hours, ax,
                                color="C1", show_waypoints=False)
    plot_meteor_latest_position_in_ifs_forecast(
        briefing_time, lead_hours, ax, meteor=meteor_track)
    
    handles = [plot1, plot2, plot3, plot4]
    plt.legend(handles=handles, fontsize=8, loc="lower left", frameon=False)
    matplotlib.rc_file_defaults()
    return fig


def _validate_issue_times(
        issue_time_oper: pd.Timestamp, issue_time_enfo: pd.Timestamp):
    """Give a warning if issue times of operational forecast and ensemble
    forecast disagree."""
    msg = (f"WARNING: Issue times of operational forecast and ensemble " +
           f"forecast disagree! Issue time of operational forecast is " +
           f"{issue_time_oper.strftime('%Y-%m-%dT%HUTC')}, issue time of " +
           f"ensemble forecast is {issue_time_enfo.strftime('%Y-%m-%dT%HUTC')}!"
           )
    if issue_time_oper != issue_time_enfo:
        warnings.warn(msg)


def _draw_icwv_oper_contour(forecast, ax):
    color = "#000000"
    linewidth = 2.0
    egh.healpix_contour(
        forecast,
        ax=ax,
        levels=[ICWV_ITCZ_THRESHOLD],
        colors=color,
        linewidths=linewidth,
    )
    line = Line2D([0], [0], label="Operational forecast", color=color,
                  linewidth=linewidth)
    return line

def _draw_icwv_enfo_contours(forecasts, ax):
    color = "#bf0000"
    linewidth = 0.8
    alpha = 0.15
    for member in forecasts["member"]:
        egh.healpix_contour(
            forecasts.sel(member=member),
            ax=ax,
            levels=[ICWV_ITCZ_THRESHOLD],
            colors=color,
            linewidths=linewidth,
            alpha=alpha,
        )
    line = Line2D([0], [0], label="Individual ensemble members", color=color,
                  linewidth=linewidth, alpha=alpha)
    return line


def _draw_icwv_enfo_mean_contour(forecasts, ax):
    color = "#800000"
    linewidth = 2.0
    enfo_mean = forecasts.mean(dim="member")
    egh.healpix_contour(
        enfo_mean,
        ax=ax,
        levels=[ICWV_ITCZ_THRESHOLD],
        colors=color,
        linewidths=linewidth,
    )
    line = Line2D([0], [0], label="Ensemble mean", color=color,
                  linewidth=linewidth)
    return line


def _draw_icwv_ERA5_contour(climatology, ax):
    color = "gray"
    linewidth = 2.0
    ls = '--'
    egh.healpix_contour(
        climatology,
        ax=ax,
        levels=[ICWV_ITCZ_THRESHOLD],
        colors=color,
        linewidths=linewidth,
        linestyles=ls,
    )
    line = Line2D([0], [0], label="ERA5 2010-2022 7-day running mean",
                  color=color, linewidth=linewidth)
    return line

def _get_rolling_daily_climatology(
        var: str,
        briefing_time: pd.Timestamp,
        lead_hours: str):
    valid_time = get_valid_time(briefing_time, lead_hours)
    valid_time_doy = valid_time.day_of_year
    climatology = _load_rolling_daily_climatology(var)
    return climatology.sel(dayofyear=valid_time_doy)

def _load_rolling_daily_climatology(var: str = "tcwv"):
    climatology_path = get_climatology_path()
    climatology = xr.open_dataset(climatology_path)
    return climatology[var]


if __name__ == "__main__":
    
    import intake
    from orcestra.meteor import get_meteor_track
    
    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 9, 7).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 9, 7, 10).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 9, 6).tz_localize("UTC")
    meteor_track = get_meteor_track(deduplicate_latlon=True)
    for lead_time in ["012h"]:#, "036h", "060h", "084h", "108h"]:
        fig = iwv_itcz_edges_enfo(briefing_time1, "12H", current_time1,
                                sattracks_fc_time1, meteor_track, hifs)
        fig.savefig(f"test_{lead_time}.png")        
