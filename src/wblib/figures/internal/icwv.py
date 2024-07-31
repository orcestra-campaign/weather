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

from wblib.figures.internal._general_plotting_functions import _plot_sattrack

CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
FORECAST_PUBLISH_LAG = "6h"
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


def iwv_itcz_edges(current_time: pd.Timestamp, lead_hours: str) -> Figure:
    lead_delta = pd.Timedelta(hours=int(lead_hours[:-1]))
    forcast_latest_time = _get_latest_forecast_time(current_time)
    init_times = _get_dates_of_previous_five_days(forcast_latest_time)
    datarrays = _get_forecast_datarrays_dict(init_times)
    # plot
    sns.set_context('talk')
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _draw_icwv_contours_for_previous_forecast_at_lead_time(
        datarrays, current_time, lead_delta, init_times, ax
    )
    im = _draw_icwv_current_forecast_at_lead_time(
        datarrays, current_time, init_times, lead_delta, ax
    )
    valid_time = current_time.floor("1D") + lead_delta
    valid_time = valid_time.tz_localize(None)
    _plot_sattrack(valid_time, ax)
    _format_axes(current_time, lead_delta, ax)
    fig.colorbar(im, label="IWV / kg m$^{-2}$", shrink=0.7)
    matplotlib.rc_file_defaults()
    return fig


def _get_latest_forecast_time(current_time: pd.Timestamp):
    publish_lag = pd.Timedelta(FORECAST_PUBLISH_LAG)
    forecast_time = (current_time - publish_lag).floor("1D")
    return forecast_time


def _get_dates_of_previous_five_days(
    current_time: pd.Timestamp,
) -> list[pd.Timestamp]:
    day = pd.Timedelta("1D")
    dates = [(current_time.floor("1D") - i * day) for i in range(1, 6)]
    dates.reverse()
    return dates


def _get_forecast_datarrays_dict(init_times):
    catalog = intake.open_catalog(CATALOG_URL)
    datarrays = dict()
    for init_time in init_times:
        refdate = init_time.strftime("%Y-%m-%d")
        dataset = (
            catalog.HIFS(refdate=refdate).to_dask().pipe(egh.attach_coords)
        )
        datarrays[init_time] = dataset[ICWV_CATALOG_VARIABLE]
    return datarrays


def _draw_icwv_contours_for_previous_forecast_at_lead_time(
    datarrays, current_time, lead_delta, init_times, ax
):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    ax.set_extent(
        [lon_min, lon_max, lat_min, lat_max]
    )  # need this line here to get the contours and lines on the plot
    for i, init_time in enumerate(init_times):
        color = REFDATE_COLORBAR[i]
        linewidth = REFDATE_LINEWIDTH[i]
        valid_time = current_time.floor("1D") + lead_delta
        valid_time = valid_time.tz_localize(None)
        field = datarrays[init_time].sel(time=valid_time)
        egh.healpix_contour(
            field,
            ax=ax,
            levels=[ICWV_ITCZ_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )


def _draw_icwv_current_forecast_at_lead_time(
    datarrays, current_time, init_times, lead_delta, ax
):
    valid_time = current_time.floor("1D") + lead_delta
    valid_time = valid_time.tz_localize(None)
    field = datarrays[init_times[-1]].sel(time=valid_time)
    im = egh.healpix_show(
        field,
        ax=ax,
        method="linear",
        cmap=ICWV_COLORMAP,
        vmin=ICWV_MIN,
        vmax=ICWV_MAX,
    )
    return im


def _format_axes(current_time, lead_delta, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    forecast_on_str = current_time.floor("1D") + lead_delta
    ax.set_title(forecast_on_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=ccrs.PlateCarree())
    ax.set_ylabel("Latitude \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])


if __name__ == "__main__":
    time = pd.Timestamp.now("UTC").tz_localize(None)
    lead_hours_str = "108H"
    figure = iwv_itcz_edges(time, lead_hours_str)
    figure.savefig("test2.png")
