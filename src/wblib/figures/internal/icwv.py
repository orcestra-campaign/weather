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

from wblib.figures.internal.sattrack import plot_sattrack
from wblib.figures.hifs import get_latest_forecast_issue_time
from wblib.figures.hifs import get_dates_of_five_previous_initializations

CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
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


def iwv_itcz_edges(briefing_time: pd.Timestamp,
                   lead_hours: str,
                   sattrack_time: pd.Timestamp) -> Figure:
    lead_delta = pd.Timedelta(hours=int(lead_hours[:-1]))
    issued_time = get_latest_forecast_issue_time(briefing_time)
    issued_times = get_dates_of_five_previous_initializations(issued_time)
    datarrays = _get_forecast_datarrays_dict(issued_times)
    # plot
    sns.set_context('talk')
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _draw_icwv_contours_for_previous_forecasts(
        datarrays, briefing_time, lead_delta, issued_times, ax
    )
    im = _draw_icwv_current_forecast(
        datarrays, briefing_time, lead_delta, issued_times, ax
    )
    plot_sattrack(sattrack_time, ax)
    _format_axes(briefing_time, issued_time, lead_delta, sattrack_time, ax)
    fig.colorbar(im, label="IWV / kg m$^{-2}$", shrink=0.7)
    matplotlib.rc_file_defaults()
    return fig


def _get_forecast_datarrays_dict(issued_times):
    catalog = intake.open_catalog(CATALOG_URL)
    datarrays = dict()
    for issued_time in issued_times:
        refdate = issued_time.strftime("%Y-%m-%d")
        dataset = (
            catalog.HIFS(refdate=refdate).to_dask().pipe(egh.attach_coords)
        )
        datarrays[issued_time] = dataset[ICWV_CATALOG_VARIABLE]
    return datarrays


def _draw_icwv_contours_for_previous_forecasts(
    datarrays, briefing_time, lead_delta, init_times, ax
):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    ax.set_extent(
        [lon_min, lon_max, lat_min, lat_max]
    )  # need this line here to get the contours and lines on the plot
    for i, init_time in enumerate(init_times):
        color = REFDATE_COLORBAR[i]
        linewidth = REFDATE_LINEWIDTH[i]
        valid_time = briefing_time + lead_delta
        valid_time = valid_time.tz_localize(None)
        field = datarrays[init_time].sel(time=valid_time)
        egh.healpix_contour(
            field,
            ax=ax,
            levels=[ICWV_ITCZ_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )


def _draw_icwv_current_forecast(
    datarrays, briefing_time, lead_delta, init_times, ax
):
    valid_time = briefing_time + lead_delta
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


def _format_axes(briefing_time, issued_time, lead_delta, sattrack_time, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    valid_time = briefing_time + lead_delta
    title_str = (
        f"Valid time: {valid_time.strftime('%Y-%m-%d %H:%M')} \n"
        f"Lead hours: {int(lead_delta.total_seconds() / 3600):03d}"
                 )
    ax.set_title(title_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=ccrs.PlateCarree())
    ax.set_ylabel("Latitude \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])
    annotation = ("Latest ECMWF IFS forecast initialization: "
                  f"{issued_time.strftime('%Y-%m-%d %H:%M %Z')}"
                  "\nSatellite tracks forecast issued on: "
                  f"{sattrack_time.strftime('%Y-%m-%d %H:%M')}")
    ax.annotate(annotation,
                xy=(-16.5, -9),
                xycoords='data',
                fontsize=8,
                bbox = dict(facecolor='white',
                            edgecolor='none',
                            alpha=1))
