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

from wblib.figures.briefing_info import get_valid_time
from wblib.figures.hifs import HifsForecasts

CATALOG_OLR_CODE = "ttr"
CATALOG_ICWV_CODE = "tcwv"

ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_COLOR = "dimgrey"

OLR_MAX = 250
OLR_MIN = 100

FIGURE_SIZE = (15, 8)
FIGURE_BOUNDARIES = (-70, 10, -10, 30)


def toa_outgoing_longwave(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    hifs: HifsForecasts,
) -> Figure:
    issue_time, diff_ttr = hifs.get_forecast(
        CATALOG_OLR_CODE,
        briefing_time,
        lead_hours,
        current_time,
        differentiate=True,
        differentiate_unit="s",
    )
    olr = - diff_ttr
    _, icwv = hifs.get_forecast(
        CATALOG_ICWV_CODE, briefing_time, lead_hours, current_time
    )
    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _format_axes(briefing_time, lead_hours, issue_time, ax)
    _draw_olr(olr, fig, ax)
    _draw_icwv_contour(icwv, ax)
    matplotlib.rc_file_defaults()
    return fig


def _draw_olr(olr, fig, ax) -> None:
    # get_orl_colormap
    gist_ncar = plt.cm.Spectral(np.linspace(0.0, 1, 128))
    white = np.array([1.0, 1.0, 1.0, 1.0])
    colors = np.vstack((gist_ncar, white))
    colormap = mcolors.LinearSegmentedColormap.from_list("olr", colors)
    # draw plot
    im = egh.healpix_show(
        olr, method="linear", cmap=colormap, vmin=OLR_MIN, vmax=OLR_MAX, ax=ax
    )
    # format colorbar
    fig.colorbar(im, label="OLR $W/m^2$", shrink=0.7)


def _draw_icwv_contour(icwv, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    color = ICWV_COLOR
    hcs = egh.healpix_contour(
        icwv,
        ax=ax,
        levels=[ICWV_ITCZ_THRESHOLD],
        colors=color,
        linewidths=2,
        linestyles="dashed",
    )
    format_func = lambda level: f"{int(level)} mm"
    ax.clabel(hcs, hcs.levels, inline=True, fontsize=10, fmt=format_func)


def _format_axes(briefing_time, lead_hours, issue_time, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    valid_time = get_valid_time(briefing_time, lead_hours)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    ax.coastlines(lw=0.8)
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
    annotation = f"Latest ECMWF IFS forecast initialization: {issue_time.strftime('%Y-%m-%d %H:%M %Z')}"
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
    briefing_time1 = pd.Timestamp(2024, 8, 1).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 1, 11).tz_localize("UTC")

    toa_outgoing_longwave(briefing_time1, "003H", current_time1, hifs)
