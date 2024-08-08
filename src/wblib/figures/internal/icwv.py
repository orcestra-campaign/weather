"""Plot ITCZ edges based on the IWV from ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd

import matplotlib
from matplotlib.figure import Figure

import seaborn as sns

from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.hifs import HifsForecasts


ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_MAX = 65  # mm
ICWV_MIN = 0  # mm
ICWV_COLORMAP = "bone"
ICWV_CATALOG_VARIABLE = "tcwv"
REFDATE_COLORBAR = [
    "#ffc99d",
    "#ffa472",
    "#ff9c59",
    "#ff7e26",
    "#ff580f",
]  # the ordering of the colors indicate the latest available refdate
REFDATE_LINEWIDTH = [1, 1.1, 1.2, 1.3, 1.5]


def iwv_itcz_edges(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    hifs: HifsForecasts,
) -> Figure:
    issue_time, forecast = hifs.get_forecast(
        ICWV_CATALOG_VARIABLE, briefing_time, lead_hours, current_time
    )
    forecasts = hifs.get_previous_forecasts(
        ICWV_CATALOG_VARIABLE, briefing_time, lead_hours, current_time
    )
    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time, ax)
    _draw_icwv_contours_for_previous_forecasts(forecasts, ax)
    im = _draw_icwv_current_forecast(forecast, ax)
    fig.colorbar(im, label="IWV - kg m$^{-2}$", shrink=0.8)
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
        cmap=ICWV_COLORMAP,
        vmin=ICWV_MIN,
        vmax=ICWV_MAX,
    )
    return im


if __name__ == "__main__":
    import intake

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 8, 7).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 15).tz_localize("UTC")

    fig = iwv_itcz_edges(briefing_time1, "003H", current_time1, hifs)
    fig.tight_layout()
    fig.savefig("test2.png")
