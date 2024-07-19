"""Plot ITCZ edges based on the IWV from ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd

from matplotlib.figure import Figure

CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
FORECAST_QUERY_REFTIME = "00"
ICWV_ITCZ_THRESHOLD = 48  # mm
ICWV_MAX = 65  # mm
ICWV_MIN = 0  # mm
ICWV_COLORMAP = "cividis_r"
ICWV_CATALOG_VARIABLE = "tcwv"
FIGURE_SIZE = (15, 8)
REFDATE_COLORBAR = [
    "#ffc99d",
    "#ffa472",
    "#ff9c59",
    "#ff7e26",
    "#ff580f",
] # the ordering of the colors indicate the latest available refdate
REFDATE_LINEWIDTH = [0.75, 0.75, 0.75, 0.75, 1]


def iwv_itcz_edges(current_time: pd.Timestamp, lead_hours: str) -> Figure:
    lead_delta = pd.Timedelta(hours=int(lead_hours[:-1]))
    previous_init_times = _get_dates_of_previous_five_days(current_time)
    init_times = [current_time] + previous_init_times
    datarrays = _get_forecast_datarrays_dict(init_times)
    # plot
    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}
    )
    _draw_icwv_contours_for_previous_forecast(
        datarrays, current_time, lead_delta, previous_init_times, ax
    )
    im = _draw_icwv_current_forecast(datarrays, current_time, lead_delta, ax)
    _format_axes(current_time, lead_delta, ax)
    fig.colorbar(im, label="IWV / kg m$^{-2}$", shrink=0.9)
    return fig


def _get_dates_of_previous_five_days(
    current_time: pd.Timestamp,
) -> list[pd.Timestamp]:
    date = current_time.floor("1D")
    day = pd.Timedelta("1D")
    dates = [(date - i * day) for i in range(1, 6)]
    dates.reverse()
    return dates


def _get_forecast_datarrays_dict(previous_init_times):
    catalog = intake.open_catalog(CATALOG_URL)
    datarrays = dict()
    for init_time in previous_init_times:
        catalog_dataset = catalog.HIFS(refdate=init_time.strftime("%Y-%m-%d"))
        dataset = catalog_dataset.to_dask().pipe(egh.attach_coords)
        datarrays[init_time] = dataset[ICWV_CATALOG_VARIABLE]
    return datarrays


def _draw_icwv_contours_for_previous_forecast(
    datarrays, current_time, lead_delta, previous_init_times, ax
):
    ax.set_extent(
        [-70, 10, -25, 25]
    )  # need this line here to get the contours and lines on the plot
    for i, init_time in enumerate(previous_init_times):
        color = REFDATE_COLORBAR[i]
        linewidth = REFDATE_LINEWIDTH[i]
        field = datarrays[init_time].sel(time=current_time + lead_delta)
        egh.healpix_contour(
            field, ax=ax, levels=[ICWV_ITCZ_THRESHOLD], colors=color,
            linewidths=linewidth
        )


def _draw_icwv_current_forecast(datarrays, current_time, lead_delta, ax):
    field = datarrays[current_time].sel(time=current_time + lead_delta)
    im = egh.healpix_show(
        field,
        ax=ax,
        method="linear",
        cmap=ICWV_COLORMAP,
        vmin=ICWV_MIN,
        vmax=ICWV_MAX,
    )
    return im


def _format_axes(current_time, lead_delta, ax):
    forecast_on_str = current_time + lead_delta
    ax.set_title(forecast_on_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=ccrs.PlateCarree())
    ax.set_ylabel("Latitude \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude \N{DEGREE SIGN}E")


if __name__ == "__main__":
    time = pd.Timestamp.now().floor("1D")
    lead_hours_str = "024H"
    figure = iwv_itcz_edges(time, lead_hours_str)
    #figure.savefig("test.png")
