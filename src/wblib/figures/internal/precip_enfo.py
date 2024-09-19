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
from matplotlib.colors import BoundaryNorm
import cmocean as cmo
import seaborn as sns

from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.hifs import HifsForecasts
from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS
from wblib.figures.meteor_pos import plot_meteor_latest_position_in_ifs_forecast

CONTOUR_THRESHOLD = 30  # mm
CATALOG_VARIABLE = "tp"

def precip_enfo(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
    meteor_track: xr.Dataset,
    hifs: HifsForecasts,
) -> Figure:
    issue_time_oper, forecast_oper = hifs.get_forecast(
        CATALOG_VARIABLE, briefing_time, lead_hours, current_time,
        forecast_type="oper", differentiate=True, differentiate_unit="D",
    )
    forecast_oper = 1000 * forecast_oper
    issue_time_enfo, forecast_enfo = hifs.get_forecast(
        CATALOG_VARIABLE, briefing_time, lead_hours, current_time,
        forecast_type="enfo", differentiate=True, differentiate_unit="D",
    )
    forecast_enfo = 1000 * forecast_enfo
    _validate_issue_times(issue_time_oper, issue_time_enfo)

    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time_oper,
                                sattracks_fc_time, "iwv_itcz_edges_enfo", ax)
    plot1 = _draw_icwv_enfo_prob(forecast_enfo, ax)
    plot2 = _draw_icwv_enfo_mean_contour(forecast_enfo, ax)
    plot3 = _draw_icwv_oper_contour(forecast_oper, ax)
    fig.colorbar(
        plot1, label=f"(Probability of 3h-mean precip.\nrate > {CONTOUR_THRESHOLD}mm/day) / %",
        shrink=0.8)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, lead_hours, ax,
                                color="C1", show_waypoints=False)
    plot_meteor_latest_position_in_ifs_forecast(
        briefing_time, lead_hours, ax, meteor=meteor_track)
    
    handles = [plot2, plot3]
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


def _draw_icwv_enfo_prob(
        forecast_enfo: xr.Dataset,
        ax
        ):
    TP_STEPS = [0, 5, 10, 20, 50, 100]
    TP_COLORMAP = cmo.cm.tempo

    probability = _get_ensemble_probabilty(forecast_enfo, CONTOUR_THRESHOLD)
    im = egh.healpix_show(
        probability,
        ax=ax,
        method="linear",
        norm=BoundaryNorm(TP_STEPS, ncolors=TP_COLORMAP.N, clip=True),
        cmap=TP_COLORMAP,
    )
    return im


def _get_ensemble_probabilty(
        forecast_enfo: xr.Dataset, threshold: float
        ) -> xr.Dataset:
    ensemble_size = forecast_enfo.sizes["member"]
    probability = (((forecast_enfo > threshold).sum(dim="member")
                    ) / ensemble_size) * 100
    return probability


def _draw_icwv_oper_contour(forecast, ax):
    color = "#000000"
    linewidth = 2.0
    egh.healpix_contour(
        forecast,
        ax=ax,
        levels=[CONTOUR_THRESHOLD],
        colors=color,
        linewidths=linewidth,
    )
    line = Line2D([0], [0], label=f"Operational forecast, 3-hourly precip rate > {CONTOUR_THRESHOLD}mm/day contour", color=color,
                  linewidth=linewidth)
    return line


def _draw_icwv_enfo_mean_contour(forecasts, ax):
    color = "#800000"
    linewidth = 2.0
    enfo_mean = forecasts.mean(dim="member")
    egh.healpix_contour(
        enfo_mean,
        ax=ax,
        levels=[CONTOUR_THRESHOLD],
        colors=color,
        linewidths=linewidth,
    )
    line = Line2D([0], [0], label=f"Ensemble mean, 3-hourly precip rate > {CONTOUR_THRESHOLD}mm/day contour", color=color,
                  linewidth=linewidth)
    return line


if __name__ == "__main__":
    import intake
    from orcestra.meteor import get_meteor_track
    
    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 9, 14).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 9, 14, 15).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 9, 14).tz_localize("UTC")
    meteor_track = get_meteor_track(deduplicate_latlon=True)
    fig = precip_enfo(briefing_time1, "36H", current_time1, sattracks_fc_time1,
                      meteor_track, hifs)
    fig.savefig("precip_enfo1.png")
