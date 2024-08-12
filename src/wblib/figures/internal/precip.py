"""Plot the cloud forecast from ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd

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

TP_THRESHOLD = 50  # mm
TCWV_THRESHOLD = 48  # mm
TP_STEPS = [0, 5, 25, 50, 75, 100]
TP_COLORMAP = cmo.cm.rain
DATA_CATALOG_VARIABLE = ["tp", "tcwv"]
REFDATE_COLORBAR_TP = [
    "#ff7e26",
    "#ff580f",
]  # the ordering of the colors indicate the latest available refdate
REFDATE_COLORBAR_TCWV = [
    "dodgerblue",
    "royalblue",
]
REFDATE_LINEWIDTH = [1.0, 1.4]

def precip(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
    flight: dict,
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
    precip_forecasts = hifs.get_previous_forecasts(
        DATA_CATALOG_VARIABLE[0],
        briefing_time,
        lead_hours,
        current_time,
        number=2,
        differentiate=True,
        differentiate_unit="D",
    )
    precip_forecasts = (
        (issue_time, 1000 * precip) for issue_time, precip in precip_forecasts
    )
    tcwv_forecasts = hifs.get_previous_forecasts(
        DATA_CATALOG_VARIABLE[1],
        briefing_time,
        lead_hours,
        current_time,
        number=2,
    )
    # plotting
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time,
                                sattracks_fc_time, ax)
    _draw_tp_contours_for_previous_forecasts(precip_forecasts, ax)
    _draw_tcwv_contours_for_previous_forecasts(tcwv_forecasts, ax)
    _draw_current_forecast(precip, fig, ax)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    plot_python_flighttrack(flight, briefing_time, lead_hours, ax, color="C1",
                            show_waypoints=False)
    matplotlib.rc_file_defaults()
    return fig


def _draw_tp_contours_for_previous_forecasts(precip_forecasts, ax):
    for i, (_, precip) in enumerate(precip_forecasts):
        color = REFDATE_COLORBAR_TP[i]
        linewidth = REFDATE_LINEWIDTH[i]
        egh.healpix_contour(
            precip,
            ax=ax,
            levels=[TP_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )


def _draw_tcwv_contours_for_previous_forecasts(tcwv_forecasts, ax):
    issued_times = []
    for i, (issued_time_, tcwv_forecasts) in enumerate(tcwv_forecasts):
        color = REFDATE_COLORBAR_TCWV[i]
        linewidth = REFDATE_LINEWIDTH[i]
        im = egh.healpix_contour(
            tcwv_forecasts,
            ax=ax,
            levels=[TCWV_THRESHOLD],
            linestyles="--",
            colors=color,
            linewidths=linewidth,
        )
        ax.clabel(im, inline=True, fontsize=10)
        issued_times.append(issued_time_)
    _add_legend(issued_times, loc="lower left")


def _draw_current_forecast(precip, fig, ax):
    im = egh.healpix_show(
        precip,
        ax=ax,
        method="linear",
        norm=BoundaryNorm(TP_STEPS, ncolors=TP_COLORMAP.N, clip=True),
        cmap=TP_COLORMAP,
    )
    fig.colorbar(im, label="mean precip. rate / mm day$^{-1}$", shrink=0.8)


def _add_legend(init_times: list, **kwargs):
    lines = [
        Line2D(
            [0],
            [0],
            color=REFDATE_COLORBAR_TP[i],
            linewidth=REFDATE_LINEWIDTH[i],
            linestyle="-",
        )
        for i in range(len(init_times) - 1, -1, -1)
    ]
    labels = [
        f'init: {init_time.strftime("%Y-%m-%d %H:%M")}UTC'
        for init_time in init_times[::-1]
    ]
    plt.legend(lines, labels, **kwargs, fontsize=12)


if __name__ == "__main__":
    import intake
    from wblib.flights.flighttrack import get_python_flightdata

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 8, 11).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 11, 12).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 8, 5).tz_localize("UTC")
    test_flight = get_python_flightdata('HALO-20240813a')
    fig = precip(briefing_time1, "60H", current_time1,
                 sattracks_fc_time1, test_flight, hifs)
    fig.savefig("test1.png")
