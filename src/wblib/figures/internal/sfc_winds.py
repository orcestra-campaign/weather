"""generates surface wind speed plots with low wind speed regions identified using ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.figure import Figure
import seaborn as sns
import healpy as hp
import xarray as xr

from wblib.figures.briefing_info import get_valid_time
from wblib.figures.hifs import HifsForecasts


FORECAST_PUBLISH_LAG = "6h"
SPEED_THRESHOLD = 3  # m/s
SPEED_MAX = 15  # m/s
SPEED_MIN = 0  # m/s
SPEED_COLORMAP = "YlGn"
FIGURE_SIZE = (15, 8)
FIGURE_BOUNDARIES = (-65, -5, -10, 20)
MESH_GRID_SIZE = 50
QUIVER_SKIP = 4


def sfc_winds(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    hifs: HifsForecasts,
) -> Figure:
    issue_time, u10m = hifs.get_forecast(
        "10u", briefing_time, lead_hours, current_time
    )
    _, v10m = hifs.get_forecast("10v", briefing_time, lead_hours, current_time)
    windspeed_10m = np.sqrt(u10m**2 + v10m**2)
    # plotting
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()},
        facecolor="white",
    )
    _speed_format_axes(briefing_time, lead_hours, issue_time, ax)
    _windspeed_plot(windspeed_10m, fig, ax)
    _wind_direction_plot(u10m, v10m, ax)
    _windspeed_contour(windspeed_10m, ax)
    matplotlib.rc_file_defaults()
    return fig


def _windspeed_contour(windspeed_10m, ax):
    im = egh.healpix_contour(
        windspeed_10m,
        ax=ax,
        levels=[SPEED_THRESHOLD],
        colors="r",
    )
    ax.clabel(im, inline=True, fontsize=12, colors="r", fmt="%d")


def _windspeed_plot(windspeed_10m, fig, ax):
    im = egh.healpix_show(
        windspeed_10m,
        method="linear",
        cmap=SPEED_COLORMAP,
        vmin=SPEED_MIN,
        vmax=SPEED_MAX,
        ax=ax,
    )
    fig.colorbar(im, label="10m wind speed / m s$^{-1}$", shrink=0.8)


def _wind_direction_plot(u10m, v10m, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    lon1 = np.linspace(lon_min, lon_max, MESH_GRID_SIZE)
    lat1 = np.linspace(lat_min, lat_max, MESH_GRID_SIZE)
    pix = xr.DataArray(
        hp.ang2pix(
            u10m.crs.healpix_nside,
            *np.meshgrid(lon1, lat1),
            nest=True,
            lonlat=True,
        ),
        coords=(("lat1", lat1), ("lon1", lon1)),
    )
    Q0 = ax.quiver(
        lon1[::QUIVER_SKIP],
        lat1[::QUIVER_SKIP],
        u10m.isel(cell=pix)[::QUIVER_SKIP, ::QUIVER_SKIP],
        v10m.isel(cell=pix)[::QUIVER_SKIP, ::QUIVER_SKIP],
        color="black",
        pivot="middle",
        scale_units="inches",
        width=0.003,
        scale=20,
    )
    ax.quiverkey(
        Q0,
        0.95,
        1.05,
        10,
        r"$10 \frac{m}{s}$",
        labelpos="E",
        coordinates="axes",
        animated=True,
    )


def _speed_format_axes(briefing_time, lead_hours, issue_time, ax):
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
    ax.set_xticks(
        np.round(np.linspace(lon_min + 5, lon_max - 5, 6), 0),
        crs=ccrs.PlateCarree(),
    )
    ax.set_yticks(
        np.round(np.linspace(lat_min, lat_max, 5), 0), crs=ccrs.PlateCarree()
    )
    ax.set_ylabel("Latitude \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])
    annotation = f"Latest ECMWF IFS forecast initialization: {issue_time.strftime('%Y-%m-%d %H:%M %Z')}"
    ax.annotate(
        annotation,
        (-32.25, -9),
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

    sfc_winds(briefing_time1, "003H", current_time1, hifs)
