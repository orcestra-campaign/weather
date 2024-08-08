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

from wblib.figures.briefing_info import get_valid_time
from wblib.figures.hifs import HifsForecasts


ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_MAX = 65  # mm
ICWV_MIN = 0  # mm
ICWV_COLORMAP = "bone"
ICWV_CATALOG_VARIABLE = "tcwv"
FIGURE_SIZE = (15, 8)
FIGURE_BOUNDARIES = (-70, 10, -10, 30)
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
        figsize=FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _format_axes(briefing_time, lead_hours, issue_time, ax)
    _draw_icwv_contours_for_previous_forecasts(forecasts, ax)
    im = _draw_icwv_current_forecast(forecast, ax)
    fig.colorbar(im, label="IWV / kg m$^{-2}$", shrink=0.7)
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


def _format_axes(briefing_time, lead_hours, issued_time, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    ax.set_extent(
        [lon_min, lon_max, lat_min, lat_max]
    )  # need this line here to get the contours and lines on the plot
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    valid_time = get_valid_time(briefing_time, lead_hours)
    title_str = (
        f"Valid time: {valid_time.strftime('%Y-%m-%d %H:%M')} \n"
        f"Lead hours: {lead_hours}"
    )
    ax.set_title(title_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=ccrs.PlateCarree())
    ax.set_ylabel("Latitude \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])
    annotation = f"Latest ECMWF IFS forecast initialization: {issued_time.strftime('%Y-%m-%d %H:%M %Z')}"
    ax.annotate(
        annotation,
        (-21.25, -9),
        fontsize=8,
        bbox=dict(facecolor="white", edgecolor="none", alpha=1),
    )


if __name__ == "__main__":
    import intake

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 8, 7).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 15).tz_localize("UTC")

    iwv_itcz_edges(briefing_time1, "003H", current_time1, hifs)
