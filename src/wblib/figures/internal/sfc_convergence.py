"""generates surface wind convergence plots using 10m u and v using ECMWF IFS"""

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

from wblib.figures.briefing_info import INTERNAL_FIGURE_SIZE
from wblib.figures.briefing_info import ORCESTRA_DOMAIN
from wblib.figures.briefing_info import format_internal_figure_axes
from wblib.figures.hifs import HifsForecasts
from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS
from wblib.figures.meteor_pos import plot_meteor_latest_position_in_ifs_forecast

CATALOG_ICWV_CODE = "tcwv"
FORECAST_PUBLISH_LAG = "6h"
CONV_MAX = 5e-5  # m/s
CONV_MIN = -5e-5  # m/s
CONV_COLORMAP = "bwr"

REFDATE_COLORBAR_TCWV = [
    "#ff0000",
    "#bf0000",
    "#800000",
    "#400000",
    "#000000"
] # the ordering of the colors indicate the latest available refdate
REFDATE_LINEWIDTH = [1, 1.1, 1.2, 1.3, 1.5]

TCWV_THRESHOLD = 48  # mm

def sfc_convergence(
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
    lat = u10m.lat
    nside = egh.get_nside(u10m)
    nest = egh.get_nest(u10m)
    ring_index = _nest2ring_index(u10m, nside)

    conv_10m = _compute_conv(u10m.isel(cell = ring_index)
                             , v10m.isel(cell = ring_index), lat.isel(cell = ring_index), nside)
    nest_index = _ring2nest_index(conv_10m, nside)

    tcwv_forecasts = hifs.get_previous_forecasts(
        CATALOG_ICWV_CODE,
        briefing_time,
        lead_hours,
        current_time,
        issue_time,
        number=5,
    )
    # plotting
    sns.set_context("talk")
    fig, ax = plt.subplots(
        figsize=INTERNAL_FIGURE_SIZE,
        subplot_kw={"projection": ccrs.PlateCarree()},
        facecolor="white",
    )
    format_internal_figure_axes(briefing_time, lead_hours, issue_time,
                                sattracks_fc_time, "sfc_convergence", ax)
    _windconv_plot(conv_10m[nest_index], fig, ax)
    _draw_tcwv_contours_for_previous_forecasts(tcwv_forecasts, ax)

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


def _compute_hder(var, nside):
    """computes the horizontal derivatives of any variable (1 vertical level, 1 time) using spherical harmonics"""
    var_alm = hp.sphtfunc.map2alm(var)
    der_arr = hp.sphtfunc.alm2map_der1(var_alm, nside)
    return der_arr[1, :], der_arr[2, :] # dvar_dtheta (lat), dvar_dphi (lon)

def _compute_conv(ua, va, lat, nside):
    _, dua_dphi = _compute_hder(ua.values, nside)
    dva_dtheta, _  = _compute_hder(va.values, nside)
    va_tanlat = va * np.tan(np.deg2rad(lat.values))
    return -(dua_dphi - dva_dtheta - va_tanlat) / 6371/1000 #+ 2*7.2921e-5 *np.sin(np.deg2rad(lat))

def _nest2ring_index(u10m, nside):
    return np.array([hp.ring2nest(nside, i) for i in u10m.cell.values])

def _ring2nest_index(conv_10m, nside):
    return np.array([hp.nest2ring(nside, i) for i in np.arange(len(conv_10m))])

def _windconv_plot(conv_10m, fig, ax):
    im = egh.healpix_show(
        conv_10m,
        method="linear",
        cmap=CONV_COLORMAP,
        vmin=CONV_MIN,
        vmax=CONV_MAX,
        ax=ax,
        nest=False
    )
    fig.colorbar(im, label="10m wind convergence / s$^{-1}$", shrink=0.8)

def _draw_tcwv_contours_for_previous_forecasts(tcwv_forecasts, ax):
    issued_times = []
    for i, (issued_time_, tcwv_forecasts) in enumerate(tcwv_forecasts):
        color = REFDATE_COLORBAR_TCWV[i]
        linewidth = REFDATE_LINEWIDTH[i]
        im = egh.healpix_contour(
            tcwv_forecasts,
            ax=ax,
            levels=[TCWV_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )
        issued_times.append(issued_time_)

if __name__ == "__main__":
    import intake
    from orcestra.meteor import get_meteor_track

    CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
    incatalog = intake.open_catalog(CATALOG_URL)
    hifs = HifsForecasts(incatalog)
    briefing_time1 = pd.Timestamp(2024, 9, 8).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 9, 8, 12).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 9, 7).tz_localize("UTC")
    meteor_track = get_meteor_track(deduplicate_latlon=True)
    fig = sfc_convergence(briefing_time1, "12H", current_time1,
                    sattracks_fc_time1, meteor_track, hifs)
    fig.savefig("test_sfc_conv.png")