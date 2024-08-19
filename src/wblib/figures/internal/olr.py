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

from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.hifs import HifsForecasts
from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS

CATALOG_OLR_CODE = "ttr"
CATALOG_ICWV_CODE = "tcwv"

ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_COLOR = "dimgrey"

OLR_MAX = 250
OLR_MIN = 100


def toa_outgoing_longwave(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
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
    olr = -diff_ttr
    _, icwv = hifs.get_forecast(
        CATALOG_ICWV_CODE, briefing_time, lead_hours, current_time
    )
    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()},
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time,
                                sattracks_fc_time, ax)
    _draw_olr(olr, fig, ax)
    _draw_icwv_contour(icwv, ax)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, lead_hours, ax,
                                color="C1", show_waypoints=False)
    matplotlib.rc_file_defaults()
    return fig


def _draw_olr(olr, fig, ax) -> None:
    # get_orl_colormap
    spectral = plt.cm.Spectral(np.linspace(0.0, 1, 9))
    white = np.array([1.0, 1.0, 1.0, 1.0])
    colors = np.vstack((spectral, white))
    colormap = mcolors.ListedColormap(colors, "olr")
    # draw plot
    im = egh.healpix_show(
        olr, method="linear", cmap=colormap, vmin=OLR_MIN, vmax=OLR_MAX, ax=ax
    )
    # format colorbar
    fig.colorbar(im,
                 label="OLR / W/m$^2$",
                 ticks=np.linspace(OLR_MIN, OLR_MAX, 11),
                 shrink=0.8)


def _draw_icwv_contour(icwv, ax):
    hcs = egh.healpix_contour(
        icwv,
        ax=ax,
        levels=[ICWV_ITCZ_THRESHOLD],
        colors=ICWV_COLOR,
        linewidths=2,
        linestyles="dashed",
    )
    format_func = lambda level: f"{int(level)} mm"
    ax.clabel(hcs, hcs.levels, inline=True, fontsize=10, fmt=format_func)

if __name__ == "__main__":
    import intake

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 8, 11).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 11, 12).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 8, 5).tz_localize("UTC")
    fig = toa_outgoing_longwave(briefing_time1, "60H", current_time1,
                                sattracks_fc_time1, hifs)
    fig.savefig("test1.png")
