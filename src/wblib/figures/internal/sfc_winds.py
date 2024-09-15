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
import itertools

from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE
from wblib.figures.briefing_info import ORCESTRA_DOMAIN
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.hifs import HifsForecasts
from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS
from wblib.figures.meteor_pos import plot_meteor_latest_position_in_ifs_forecast

FORECAST_PUBLISH_LAG = "6h"
SPEED_THRESHOLD = 3  # m/s
SPEED_MAX = 15  # m/s
SPEED_MIN = 0  # m/s
SPEED_COLORMAP = "YlGn"
MESH_GRID_SIZE = 50
QUIVER_SKIP = 4
NUMBER_FORECASTS = 5

REFDATE_COLORBAR_TCWV = [
    "#ff0000",
    "#bf0000",
    "#800000",
    "#400000",
    "#000000"
] # the ordering of the colors indicate the latest available refdate
REFDATE_LINEWIDTH = [1, 1.1, 1.2, 1.3, 1.5]

def sfc_winds(
    briefing_time: pd.Timestamp,
    lead_hours: str,
    current_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
    meteor_track: xr.Dataset,
    hifs: HifsForecasts,
) -> Figure:
    issue_time, u10m = hifs.get_forecast(
        "10u", briefing_time, lead_hours, current_time
    )
    _, v10m = hifs.get_forecast("10v", briefing_time, lead_hours, current_time)
    windspeed_10m = np.sqrt(u10m**2 + v10m**2)

    u10m_latest_five = hifs.get_previous_forecasts(
        "10u", briefing_time, lead_hours, current_time, issue_time,
        number=NUMBER_FORECASTS,
    )
    v10m_latest_five = hifs.get_previous_forecasts(
        "10v", briefing_time, lead_hours, current_time, issue_time,
        number=NUMBER_FORECASTS,
    )
    #for u10, v10 in itertools.zip(u10m_latest_five, v10m_latest_five):
    windspeed_10m_latest = [np.sqrt(u10[1]**2 + v10[1]**2) for u10, v10 in zip(u10m_latest_five, v10m_latest_five)]

    # plotting
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()},
        facecolor="white",
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time,
                                sattracks_fc_time, "sfc_winds", ax)
    _windspeed_plot(windspeed_10m, fig, ax)
    _wind_direction_plot(u10m, v10m, ax)
    #_windspeed_contour(windspeed_10m, ax)
    _windspeed_contour_for_previous_forecasts(windspeed_10m_latest, ax)
    _draw_confluence_contour(v10m, ax)
    plot_sattrack(ax, briefing_time, lead_hours, sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, lead_hours, ax,
                                color="C1", show_waypoints=False)
    plot_meteor_latest_position_in_ifs_forecast(
        briefing_time, lead_hours, ax, meteor=meteor_track)
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

def _windspeed_contour_for_previous_forecasts(windspeed_10m, ax):
    issued_times = []
    for i, windspeed_forecast in enumerate(windspeed_10m):
        color = REFDATE_COLORBAR_TCWV[i]
        linewidth = REFDATE_LINEWIDTH[i]
        im = egh.healpix_contour(
            windspeed_forecast,
            ax=ax,
            levels=[SPEED_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )
        #issued_times.append(issued_time_)

def _draw_confluence_contour(v10m, ax):
    im = egh.healpix_contour(
        v10m,
        ax=ax,
        levels=[0],
        colors="gray",
        linewidths = 1.2
    )
    ax.clabel(im, inline=True, fontsize=10, colors="gray", fmt="%d")


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
    lon_min, lon_max, lat_min, lat_max = ORCESTRA_DOMAIN
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


if __name__ == "__main__":
    import intake
    from orcestra.meteor import get_meteor_track

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 9, 13).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 9, 13, 10, 50).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 9, 13).tz_localize("UTC")
    meteor_track = get_meteor_track(deduplicate_latlon=True)
    fig = sfc_winds(briefing_time1, "108H", current_time1,
                    sattracks_fc_time1, meteor_track, hifs)
    fig.savefig("test_sfc_winds_108H.png")
