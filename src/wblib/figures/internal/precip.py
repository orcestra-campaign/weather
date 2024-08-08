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
from wblib.figures.briefing_info import get_valid_time

TP_THRESHOLD = 50  # mm
TCWV_THRESHOLD = 48  # mm
TP_STEPS = [0, 5, 25, 50, 75, 100]
TP_COLORMAP = cmo.cm.rain
DATA_CATALOG_VARIABLE = ["tp", "tcwv"]
FIGURE_SIZE = (15, 8)
DOMAIN = "Sal"
REFDATE_COLORBAR_TP = [
    "#ff7e26",
    "#ff580f",
]  # the ordering of the colors indicate the latest available refdate
REFDATE_COLORBAR_TCWV = [
    "dodgerblue",
    "royalblue",
]
REFDATE_LINEWIDTH = [1.0, 1.4]
FIGURE_BOUNDARIES = (-70, 10, -10, 30)


def precip(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
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
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _format_axes(briefing_time, lead_hours, issue_time, ax)
    _draw_tp_contours_for_previous_forecasts(precip_forecasts, ax)
    _draw_tcwv_contours_for_previous_forecasts(tcwv_forecasts, ax)
    _draw_current_forecast(precip, fig, ax)
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
    fig.colorbar(im, label="mean precip. rate / mm day$^{-1}$", shrink=0.7)


def _format_axes(briefing_time, lead_hours, issue_time, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    valid_time = get_valid_time(briefing_time, lead_hours)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    title_str = (
        f"Valid time: {valid_time.strftime('%Y-%m-%d %H:%M')}UTC \n"
        f"Lead hours: {lead_hours}"
    )
    ax.set_title(title_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=ccrs.PlateCarree())
    ax.set_ylabel("Latitude / \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude / \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])
    annotation = f"Latest ECMWF IFS forecast initialization: {issue_time.strftime('%Y-%m-%d %H:%M %Z')}"
    ax.annotate(
        annotation,
        (-21.25, -9),
        fontsize=8,
        bbox=dict(facecolor="white", edgecolor="none", alpha=1),
    )


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

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 8, 1).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 1, 11).tz_localize("UTC")

    precip(briefing_time1, "003H", current_time1, hifs)
