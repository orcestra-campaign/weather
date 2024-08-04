import intake
import numpy as np
import xarray as xr
import pandas as pd

import cartopy.crs as ccrs
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
import seaborn as sns
import easygems.healpix as egh

from wblib.figures.hifs import get_latest_forecast_issue_time


CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
CATALOG_OLR_CODE = "ttr"

OLR_MAX = 250
OLR_MIN = 100

FIGURE_SIZE = (15, 8)
FIGURE_BOUNDARIES = (-70, 10, -10, 30)


def toa_outgoing_longwave(
    briefing_time: pd.Timestamp, lead_hours: str, *args, **kwargs
) -> Figure:
    lead_delta = pd.Timedelta(hours=int(lead_hours[:-1]))
    issued_time = get_latest_forecast_issue_time(briefing_time)
    valid_time = briefing_time + lead_delta
    accumulated_ttr = _get_ttr_forecast_datarray(issued_time)
    olr = _convert_accumulated_ttr_to_olr(accumulated_ttr, issued_time)
    olr = olr.sel(time=valid_time.tz_localize(None))

    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _draw_olr(olr, fig, ax)
    _format_axes(briefing_time, issued_time, lead_delta, ax)
    matplotlib.rc_file_defaults()
    return fig


def _get_ttr_forecast_datarray(issued_time: pd.Timestamp) -> xr.DataArray:
    catalog = intake.open_catalog(CATALOG_URL)
    refdate = issued_time.strftime("%Y-%m-%d")
    dataset = catalog.HIFS(refdate=refdate).to_dask().pipe(egh.attach_coords)
    datarray = dataset[CATALOG_OLR_CODE]
    return datarray


def _convert_accumulated_ttr_to_olr(
    accumulated_ttr: xr.DataArray, issued_time: pd.Timestamp
) -> xr.DataArray:
    olr = xr.zeros_like(accumulated_ttr)
    for i, time in enumerate(accumulated_ttr.time.values):
        if i == 0:
            previous_time = issued_time
            timedelta = pd.Timedelta(time - issued_time.tz_localize(None))
            ttr_0 = -accumulated_ttr.loc[dict(time=time)]
            olr.loc[dict(time=time)] = ttr_0 / timedelta.total_seconds()
            continue
        previous_time = accumulated_ttr.time.values[i - 1]
        timedelta = pd.Timedelta(time - previous_time)
        ttr_2 = -accumulated_ttr.loc[dict(time=time)]
        ttr_1 = -accumulated_ttr.loc[dict(time=time - timedelta)]
        olr.loc[dict(time=time)] = (ttr_2 - ttr_1) / timedelta.total_seconds()
    return olr


def _draw_olr(olr, fig, ax) -> None:
    sns.set_context("talk")
    # get_orl_colormap
    gist_ncar = plt.cm.gist_ncar(np.linspace(0.0, 1, 128))
    white = np.array([1.0, 1.0, 1.0, 1.0])
    colors = np.vstack((gist_ncar, white))
    colormap = mcolors.LinearSegmentedColormap.from_list("olr", colors)
    # draw plot
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    ax.coastlines(lw=0.8)
    im = egh.healpix_show(
        olr, method="linear", cmap=colormap, vmin=OLR_MIN, vmax=OLR_MAX, ax=ax
    )
    # format colorbar
    fig.colorbar(im, label="OLR $W/m^2$", shrink=0.7)
    matplotlib.rc_file_defaults()


def _format_axes(briefing_time, issued_time, lead_delta, ax):
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
    annotation = f"Latest ECMWF IFS forecast initialization: {issued_time.strftime('%Y-%m-%d %H:%M %Z')}"
    ax.annotate(
        annotation,
        (-21.25, -9),
        fontsize=8,
        bbox=dict(facecolor="white", edgecolor="none", alpha=1),
    )
