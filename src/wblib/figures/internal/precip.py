"""Plot the cloud forecast from ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd

import matplotlib
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import seaborn as sns
import cmocean as cmo

#import orcestra.sat

#from wblib.figures.internal._general_plotting_functions import plot_sattrack

CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
FORECAST_PUBLISH_LAG = "6h"
DATA_THRESHOLD_TP = 50  # mm
DATA_THRESHOLD_TCWV = 48 # mm
DATA_STEPS_TP = [0, 5, 25, 50, 75, 100]
DATA_COLORMAP = cmo.cm.rain
DATA_CATALOG_VARIABLE = ["tp", "tcwv"]
FIGURE_SIZE = (15, 8)
DOMAIN = 'Sal'
REFDATE_COLORBAR_TP = [
    "#ff7e26",
    "#ff580f",
]  # the ordering of the colors indicate the latest available refdate
REFDATE_COLORBAR_TCWV = [
    "dodgerblue",
    "royalblue",
]

REFDATE_LINEWIDTH = [1.0, 1.4]

def _select_latlonbox(domain: str) -> tuple:
    if domain == 'full_Atlantic':
        return (-70, 10, -10, 30)
    elif domain == 'Sal':
        return (-50, 0, -5, 20)
    elif domain == 'Barbados':
        return (-70, 10, -10, 30)
    else:
        raise ValueError ('Please provide a valid domain! Valid domains are:' +
                          ' "full_Atlantic", "Sal", and "Barbados".')


def _get_latest_forecast_time(current_time: pd.Timestamp):
    publish_lag = pd.Timedelta(FORECAST_PUBLISH_LAG)
    forecast_time = (current_time - publish_lag).floor("1D")
    return forecast_time


def _get_dates_of_previous_N_days(
    current_time: pd.Timestamp,
    N_days: int,
) -> list[pd.Timestamp]:
    day = pd.Timedelta("1D")
    dates = [(current_time.floor("1D") - i * day) for i in range(0, N_days)]
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
        datarrays[init_time] = dataset[DATA_CATALOG_VARIABLE]
    return datarrays


def plot_precip(current_time: pd.Timestamp, lead_hours: str) -> Figure:
    # retrieve the forecast data
    lead_delta = pd.Timedelta(hours=int(lead_hours[:-1]))
    valid_time = current_time.floor("1D") + lead_delta
    valid_time = valid_time.tz_localize(None)
    forcast_latest_time = _get_latest_forecast_time(current_time)
    init_times = _get_dates_of_previous_N_days(forcast_latest_time, 2)
    datarrays = _get_forecast_datarrays_dict(init_times)
    precip = {init_time: datarrays[init_time]['tp'] for init_time in init_times}
    tcwv = {init_time: datarrays[init_time]['tcwv'] for init_time in init_times}
    for i, init_time in enumerate(init_times):
        precip[init_time] = precip[init_time].diff('time') * 8000
    
    # plotting
    sns.set_context('talk')
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _draw_tp_contours_for_previous_forecast_at_lead_time(
        precip, valid_time, init_times, ax
    )
    _draw_tcwv_contours_for_previous_forecast_at_lead_time(
        tcwv, valid_time, init_times, ax
    )
    im = _draw_current_forecast_at_lead_time(
        precip, valid_time, init_times, ax
    )
    #plot_sattrack(valid_time, ax)
    _format_axes(current_time, lead_delta, ax)
    _add_legend(init_times, loc='lower right')
    fig.colorbar(im, label="3h mean precip. rate / mm$\,$day$^{-1}$",
                 shrink=0.7)
    matplotlib.rc_file_defaults()
    return fig

def _draw_tp_contours_for_previous_forecast_at_lead_time(
    datarrays, valid_time, init_times, ax
):
    lon_min, lon_max, lat_min, lat_max = _select_latlonbox(DOMAIN)
    ax.set_extent(
        [lon_min, lon_max, lat_min, lat_max]
    )  # need this line here to get the contours and lines on the plot
    for i, init_time in enumerate(init_times):
        color = REFDATE_COLORBAR_TP[i]
        linewidth = REFDATE_LINEWIDTH[i]
        field = datarrays[init_time].sel(time=valid_time)
        im = egh.healpix_contour(
            field,
            ax=ax,
            levels=[DATA_THRESHOLD_TP],
            colors=color,
            linewidths=linewidth,
            label=init_time
        )

def _draw_tcwv_contours_for_previous_forecast_at_lead_time(
    datarrays, valid_time, init_times, ax
):
    lon_min, lon_max, lat_min, lat_max = _select_latlonbox(DOMAIN)
    ax.set_extent(
        [lon_min, lon_max, lat_min, lat_max]
    )  # need this line here to get the contours and lines on the plot
    for i, init_time in enumerate(init_times):
        color = REFDATE_COLORBAR_TCWV[i]
        linewidth = REFDATE_LINEWIDTH[i]
        field = datarrays[init_time].sel(time=valid_time)
        im = egh.healpix_contour(
            field,
            ax=ax,
            levels=[DATA_THRESHOLD_TCWV],
            linestyles = '--',
            colors=color,
            linewidths=linewidth,
        )
        ax.clabel(im, inline=True, fontsize=10)
        
def _draw_current_forecast_at_lead_time(
    datarrays, valid_time, init_times, ax
):
    from matplotlib.colors import BoundaryNorm
    field = datarrays[init_times[-1]].sel(time=valid_time)
    im = egh.healpix_show(
        field,
        ax=ax,
        method="linear",
        norm = BoundaryNorm(DATA_STEPS_TP, ncolors=DATA_COLORMAP.N, clip=True),
        cmap=DATA_COLORMAP,
    )
    return im

def _format_axes(current_time, lead_delta, ax):
    lon_min, lon_max, lat_min, lat_max = _select_latlonbox(DOMAIN)
    forecast_on_str = current_time.floor("1D") + lead_delta
    ax.set_title(f'Valid: {forecast_on_str}')
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=ccrs.PlateCarree())
    ax.set_ylabel("Latitude / \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude / \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])

def _add_legend(init_times: list, **kwargs):
    lines = [Line2D([0], [0],
                    color=REFDATE_COLORBAR_TP[i],
                    linewidth=REFDATE_LINEWIDTH[i],
                    linestyle='-') for i in range(len(init_times)-1, -1, -1)]
    labels = [f'init: {init_time}UTC' for init_time in init_times[::-1]]
    plt.legend(lines, labels, **kwargs, fontsize=12)

if __name__ == "__main__":
    time = pd.Timestamp.now("UTC").tz_localize(None)
    lead_hours_str = "12H"
    figure = plot_precip(time, lead_hours_str)
    figure.savefig("test.png")