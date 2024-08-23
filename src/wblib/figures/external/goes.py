"""Generate satellite images form GOES east"""

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import xarray as xr
import requests
from io import BytesIO
import rioxarray
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from wblib.figures.sattrack import plot_sattrack
from wblib.flights.flighttrack import plot_python_flighttrack
from wblib.flights.flighttrack import get_python_flightdata
from wblib.flights._define_flights import FLIGHTS

from wblib.figures.meteor_pos import plot_meteor_latest_position

API_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TIME_ROUND_FREQUENCY = "10min"
TIME_LAG = "1h"

GOES_PRODUCT_NAME = {
    "infrared": "Band13_Clean_Infrared",
    "visible": "Band2_Red_Visible_1km",
}
GOES_QUERY_BOUNDARIES = (-70, 5, -25, 25)  # lon_min, lon_max, lat_min, lat_max
GOES_QUERY_URL = (
    "https://wvs.earthdata.nasa.gov/api/v1/snapshot?"
    "REQUEST=GetSnapshot&TIME={query_time_str}&BBOX={lat_min},{lon_min}"
    ",{lat_max},{lon_max}&CRS=EPSG:4326&LAYERS=GOES-East_ABI_"
    "{goes_product_name}&WRAP=x&FORMAT=image/"
    "tiff&WIDTH=2048&HEIGHT=910"
)

FIGURE_TITLES = {
    "infrared": "GOES EAST Clean Infrared",
    "visible": "GOES EAST Red Visible 1km",
}
FIGURE_BOUNDARIES = (-70, 5, -10, 25)


def current_satellite_image_vis(
        current_time: pd.Timestamp,
        briefing_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp,
        current_location: str,
        meteor_track: xr.Dataset,
        ) -> Figure:
    fig = _get_satellite_image(
        current_time, briefing_time, sattracks_fc_time, meteor_track, "visible"
        )
    return fig


def current_satellite_image_ir(
        current_time: pd.Timestamp,
        briefing_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp,
        curent_location: str,
        meteor_track: xr.Dataset,
        ) -> Figure:
    fig = _get_satellite_image(
        current_time, briefing_time, sattracks_fc_time, meteor_track, "infrared")
    return fig


def _get_satellite_image(
    current_time: pd.Timestamp,
    briefing_time: pd.Timestamp,
    sattracks_fc_time: pd.Timestamp,
    meteor_track: xr.Dataset,
    plot_type: str,
    ) -> plt.Figure:
    query_time_str = _get_query_date_string(current_time)
    goes_image = _get_goes_image_datarray(plot_type, query_time_str)
    fig = _get_figure(briefing_time, sattracks_fc_time, meteor_track, plot_type,
                      query_time_str, goes_image)
    return fig


def _get_figure(
        briefing_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp,
        meteor_track: xr.Dataset,
        plot_type: str,
        query_time_str: str,
        goes_image: xr.DataArray,
        ) -> Figure:
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    y_slice = slice(lat_max, lat_min)
    x_slice = slice(lon_min, lon_max)
    goes_image = goes_image.sel(y=y_slice, x=x_slice)
    goes_image = goes_image.transpose("y", "x", "band")
    x_fig = 10
    y_fig = (lat_min - lat_max) / (lon_min - lon_max) * x_fig
    extent = [
        goes_image.x.min(),
        goes_image.x.max(),
        goes_image.y.min(),
        goes_image.y.max(),
    ]
    # create figure
    fig, ax = plt.subplots(
        figsize=(x_fig, y_fig), subplot_kw={"projection": ccrs.PlateCarree()}
    )
    ax.imshow(
        goes_image.values,
        extent=extent,
        origin="upper",
    )
    plot_sattrack(ax, briefing_time, "00H", sattracks_fc_time,
                  which_orbit="descending")
    for flight_id in FLIGHTS:
        flight = get_python_flightdata(flight_id)
        plot_python_flighttrack(flight, briefing_time, "00", ax,
                                color="C1", show_waypoints=False)
    plot_meteor_latest_position(ax, meteor=meteor_track)
    _format_axes(plot_type, query_time_str, ax)
    return fig


def _format_axes(plot_type, query_time_str, ax) -> None:
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    ax.coastlines()
    xticks = np.round(np.linspace(lon_min, lon_max, 6), 0)
    yticks = np.round(np.linspace(lat_min, lat_max, 8), 0)
    ax.set_xticks(xticks, crs=ccrs.PlateCarree())
    ax.set_yticks(yticks, crs=ccrs.PlateCarree())
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(FIGURE_TITLES[plot_type])
    ax.annotate(query_time_str, (-11.75, -8.5), backgroundcolor="white")


def _get_goes_image_datarray(plot_type, query_time_str):
    # get raster image
    lon_min, lon_max, lat_min, lat_max = GOES_QUERY_BOUNDARIES
    goes_product_name = GOES_PRODUCT_NAME[plot_type]
    url = GOES_QUERY_URL.format(
        query_time_str=query_time_str,
        lat_min=lat_min,
        lon_min=lon_min,
        lat_max=lat_max,
        lon_max=lon_max,
        goes_product_name=goes_product_name,
    )
    response = requests.get(url, stream=True)
    response.raise_for_status()
    raster = rioxarray.open_rasterio(BytesIO(response.content))
    # convert to an xarray dataarray
    red = raster.sel(band=1)
    green = raster.sel(band=2)
    blue = raster.sel(band=3)
    goes_image = xr.concat([red, green, blue], dim="band")
    return goes_image


def _get_query_date_string(current_time):
    query_time = current_time.floor(TIME_ROUND_FREQUENCY) - pd.Timedelta(
        TIME_LAG
    )
    query_time_str = query_time.strftime(API_DATE_FORMAT)
    return query_time_str


if __name__ == "__main__":
    from orcestra.meteor import get_meteor_track
    
    sattracks_fc_time = pd.Timestamp(2024, 8, 21).tz_localize("UTC")
    briefing_time = pd.Timestamp(2024, 8, 24).tz_localize("UTC")
    current_time = pd.Timestamp.now("UTC")
    meteor_track = get_meteor_track(deduplicate_latlon=True)
    fig = _get_satellite_image(current_time, briefing_time, sattracks_fc_time,
                               meteor_track, "infrared")
    fig.savefig("test.png")