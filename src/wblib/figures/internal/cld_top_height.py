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
CATALOG_TEMPERATURE_CODE = "t"
CATALOG_GEOPOT_HEIGHT_CODE = "gh"

ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_COLOR = "dimgrey"

CLOUD_TOP_HEIGHT_MIN = 5.
CLOUD_TOP_HEIGHT_MAX = 18.5


def cloud_top_height(
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
    T_bright = _calc_brightness_temperature(olr)
    _, icwv = hifs.get_forecast(
        CATALOG_ICWV_CODE, briefing_time, lead_hours, current_time
        )
    _, temperature = hifs.get_forecast(
        CATALOG_TEMPERATURE_CODE, briefing_time, lead_hours, current_time
        )
    _, geopot_height = hifs.get_forecast(
        CATALOG_GEOPOT_HEIGHT_CODE, briefing_time, lead_hours, current_time
        )
    cloud_top_height = _get_cloud_top_height_in_km(
        T_bright, temperature, geopot_height,
        )
    # plot
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()},
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time,
                                sattracks_fc_time, ax)
    _draw_cloud_top_height(cloud_top_height, fig, ax)
    _draw_icwv_contour(icwv, ax)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, lead_hours, ax,
                                color="C1", show_waypoints=False)
    matplotlib.rc_file_defaults()
    return fig


def _calc_brightness_temperature(
        olr: xr.DataArray
        ) -> xr.DataArray:
    sigma = 5.670374419*10**(-8) 
    T_bright = (olr/sigma)**(1./4.)
    return T_bright


def _get_cloud_top_height_in_km(
        T_bright: xr.DataArray,
        temperature: xr.DataArray,
        geopot_height: xr.DataArray
        ) -> xr.DataArray:
    T_diff = np.abs(temperature - T_bright)
    index = T_diff[:, :].argmin(axis=0)
    cloud_top_height = geopot_height.isel(level=index.compute()) * 0.001
    return cloud_top_height


def _draw_cloud_top_height(cloud_top_height, fig, ax) -> None:
    # get colorbar
    accent = plt.cm.Accent(np.linspace(0.0, 1, 8))
    white = np.array([1.0, 1.0, 1.0, 1.0])
    colors = np.vstack((white, accent))
    colormap = mcolors.ListedColormap(colors, "cloud_top_height")
    # draw plot
    im = egh.healpix_show(
        cloud_top_height, method="linear", cmap=colormap,
        vmin=CLOUD_TOP_HEIGHT_MIN, vmax=CLOUD_TOP_HEIGHT_MAX,
        ax=ax
    )
    # format colorbar
    fig.colorbar(im,
                 label="Cloud top height / km",
                 ticks=np.linspace(CLOUD_TOP_HEIGHT_MIN, CLOUD_TOP_HEIGHT_MAX,
                                   10),
                 shrink=0.8,
                 extend='both')


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
    fig = cloud_top_height(
        briefing_time1, "60H", current_time1, sattracks_fc_time1, hifs
        )
    fig.savefig("test1.png")
