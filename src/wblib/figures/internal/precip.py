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
from matplotlib.colors import BoundaryNorm

import seaborn as sns
import cmocean as cmo

#import orcestra.sat
#from wblib.figures.internal._general_plotting_functions import plot_sattrack

from wblib.figures.hifs import get_latest_forecast_issue_time
from wblib.figures.hifs import get_dates_of_previous_initializations

CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
TP_THRESHOLD = 50  # mm
TCWV_THRESHOLD = 48 # mm
TP_STEPS = [0, 5, 25, 50, 75, 100]
TP_COLORMAP = cmo.cm.rain
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

def precip(briefing_time: pd.Timestamp, lead_hours: str) -> Figure:
    # retrieve the forecast data
    lead_delta = pd.Timedelta(hours=int(lead_hours[:-1]))
    issued_time = get_latest_forecast_issue_time(briefing_time)
    issued_times = get_dates_of_previous_initializations(issued_time, number=2)
    datarrays = _get_forecast_datarrays_dict(issued_times)
    precip = {init_time: datarrays[init_time]['tp'] for init_time in
              issued_times}
    tcwv = {init_time: datarrays[init_time]['tcwv'] for init_time in
            issued_times}
    for init_time in issued_times:
        precip[init_time] = precip[init_time].differentiate(
            'time', datetime_unit='D') * 1000
    
    # plotting
    sns.set_context('talk')
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _draw_tp_contours_for_previous_forecasts(
        precip, briefing_time, lead_delta, issued_times, ax
    )
    _draw_tcwv_contours_for_previous_forecasts(
        tcwv, briefing_time, lead_delta, issued_times, ax
    )
    im = _draw_current_forecast(
        precip, briefing_time, lead_delta, issued_times, ax
    )
    #plot_sattrack(valid_time, ax)
    _format_axes(briefing_time, lead_delta, ax)
    _add_legend(issued_times, loc='lower right')
    fig.colorbar(im, label="mean precip. rate / mm day$^{-1}$",
                 shrink=0.7)
    matplotlib.rc_file_defaults()
    return fig

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

def _draw_tp_contours_for_previous_forecasts(
    datarrays, briefing_time, lead_delta, init_times, ax
):
    lon_min, lon_max, lat_min, lat_max = _select_latlonbox(DOMAIN)
    ax.set_extent(
        [lon_min, lon_max, lat_min, lat_max]
    )  # need this line here to get the contours and lines on the plot
    for i, init_time in enumerate(init_times):
        color = REFDATE_COLORBAR_TP[i]
        linewidth = REFDATE_LINEWIDTH[i]
        valid_time = briefing_time + lead_delta
        valid_time = valid_time.tz_localize(None)
        field = datarrays[init_time].sel(time=valid_time)
        im = egh.healpix_contour(
            field,
            ax=ax,
            levels=[TP_THRESHOLD],
            colors=color,
            linewidths=linewidth,
        )

def _draw_tcwv_contours_for_previous_forecasts(
    datarrays, briefing_time, lead_delta, init_times, ax
):
    lon_min, lon_max, lat_min, lat_max = _select_latlonbox(DOMAIN)
    ax.set_extent(
        [lon_min, lon_max, lat_min, lat_max]
    )  # need this line here to get the contours and lines on the plot
    for i, init_time in enumerate(init_times):
        color = REFDATE_COLORBAR_TCWV[i]
        linewidth = REFDATE_LINEWIDTH[i]
        valid_time = briefing_time + lead_delta
        valid_time = valid_time.tz_localize(None)
        field = datarrays[init_time].sel(time=valid_time)
        im = egh.healpix_contour(
            field,
            ax=ax,
            levels=[TCWV_THRESHOLD],
            linestyles = '--',
            colors=color,
            linewidths=linewidth,
        )
        ax.clabel(im, inline=True, fontsize=10)
        
def _draw_current_forecast(
    datarrays, briefing_time, lead_delta, init_times, ax
):
    valid_time = briefing_time + lead_delta
    valid_time = valid_time.tz_localize(None)
    field = datarrays[init_times[-1]].sel(time=valid_time)
    im = egh.healpix_show(
        field,
        ax=ax,
        method="linear",
        norm = BoundaryNorm(TP_STEPS, ncolors=TP_COLORMAP.N, clip=True),
        cmap=TP_COLORMAP,
    )
    return im

def _format_axes(briefing_time, lead_delta, ax):
    lon_min, lon_max, lat_min, lat_max = _select_latlonbox(DOMAIN)
    valid_time = briefing_time + lead_delta
    title_str = (
        f"Valid time: {valid_time.strftime('%Y-%m-%d %H:%M')}UTC \n"
        f"Lead hours: {int(lead_delta.total_seconds() / 3600):03d}"
                 )
    ax.set_title(title_str)
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
    labels = [f'init: {init_time.strftime("%Y-%m-%d %H:%M")}UTC' for
              init_time in init_times[::-1]]
    plt.legend(lines, labels, **kwargs, fontsize=12)

if __name__ == "__main__":
    briefing_time = pd.Timestamp("2024-07-31").tz_localize("UTC")
    lead_hours_str = "12H"
    figure = precip(briefing_time, lead_hours_str)
    figure.savefig("test.png")