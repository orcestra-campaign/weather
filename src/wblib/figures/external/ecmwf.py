import requests
from PIL import Image as img
from io import BytesIO
import pandas as pd
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from wblib.figures.briefing_info import ORCESTRA_DOMAIN
from wblib.figures.hifs import expected_issue_time
from wblib.figures.hifs import get_valid_time

from orcestra import bco, sal

ANALYSIS_URLS = {
    "ifs_meteogram": "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/",
    "ifs_dust": "https://charts.ecmwf.int/opencharts-api/v1/products/aerosol-forecasts/",
    "ifs_cloud_top_height": "https://charts.ecmwf.int/opencharts-api/v1/products/medium-cloud-parameters/",
}


def ifs_dust(
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp, 
        add_overlay: bool = True
        ) -> img.Image:
    url = ANALYSIS_URLS["ifs_dust"]
    params = _create_ifs_var_params(
        briefing_time, lead_hours, current_time,
        var="composition_duaod550", projection='classical_west_tropic',
        )
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    figure_url = response.json().get("data").get("link").get("href")
    response = requests.get(figure_url)
    image = img.open(BytesIO(response.content))
    image = image.crop((11, 222, 1989, 1210))
    if add_overlay:
        return _overlay_ecmwf(image)    
    return image


def ifs_cloud_top_height(
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp
        ) -> img.Image:
    url = ANALYSIS_URLS["ifs_cloud_top_height"]
    params = _create_ifs_var_params(
        briefing_time, lead_hours, current_time,
        var="hcct", projection="opencharts_west_tropic",
        )
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    figure_url = response.json().get("data").get("link").get("href")
    response = requests.get(figure_url)
    image = img.open(BytesIO(response.content))
    image = image.crop((1300, 500, 1900, 800))
    return image


def ifs_meteogram(
        current_time: pd.Timestamp,
        briefing_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp,
        location: str,
        meteor_track: xr.Dataset,
        ) -> img.Image:
    url = ANALYSIS_URLS["ifs_meteogram"]
    params = _create_ifs_meteogram_params(location)
    headers = {
        "accept": "application/json",
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    figure_url = response.json().get("data").get("link").get("href")
    response = requests.get(figure_url)
    image = img.open(BytesIO(response.content))
    image = image.crop((60, 0, 620, 760))
    return image


def _create_ifs_var_params(
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        var: str,
        projection: str,
        ):
    issue_time = expected_issue_time(briefing_time, current_time)
    valid_time = get_valid_time(briefing_time, lead_hours)
    valid_time = valid_time.tz_localize(None)
    params = {
        'valid_time': valid_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'base_time': issue_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'projection': projection,
        'layer_name': var,
    }
    return params


def _create_ifs_meteogram_params(location: str) -> dict:
    coords = _get_coordinates(location)
    params = {"lat": coords[0], "lon": coords[1], "station_name": ""}
    return params


def _get_coordinates(location: str) -> tuple:
    if location == "Sal":
        lat = "16.73883"  # degN
        lon = "-22.942"  # degE
    elif location == "Barbados":
        lat = "13.075418"  # degN
        lon = "-59.493768"  # degE
    else:
        error_str = (
            "Please provide a valid location. Valid locations are "
            + "currently: 'Sal' or 'Barbados'."
        )
        raise ValueError(error_str)
    return (lat, lon)


def _overlay_ecmwf(
    image: img.Image,
    color="#00267F",
    linewidth=1.2,
    fontfamily="monospace",
    fontsize="small",
    fontweight="bold",
    markersize=36,
    dpi=200
):
    """Overlay the ECMWF forecast with coastlines, grid and waypoints."""
    proj = ccrs.PlateCarree()
    extents = [-180, 0, -45, 45]
    nhc = np.asarray(image.convert("RGBA"))
    ny, nx, _ = nhc.shape

    # Convert map extent to Mercator projection
    img_extents = proj.transform_points(
        ccrs.PlateCarree(), np.asarray(extents[:2]), np.asarray(extents[2:])
    )[:, :2].T.ravel()

    # Create a GeoAxis based on the original image size
    fig, ax = plt.subplots(
        figsize=(nx / dpi, ny / dpi),
        dpi=dpi,
        subplot_kw={"projection": proj},
    )
    ax.set_position([0, 0, 1, 1])
    ax.spines["geo"]
    ax.coastlines(color=color, lw=linewidth, resolution="110m")

    # Plot the original image based on it's geolocation (projection + extent)
    ax.imshow(nhc, extent=img_extents, transform=proj)
    ax.set_extent(extents=ORCESTRA_DOMAIN, crs=proj)
    ax.set_xticks([-60, -40, -20], crs=ccrs.PlateCarree())
    ax.set_yticks([-10, 0, 10, 20], crs=ccrs.PlateCarree())  
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)    

    
    for pnt in (bco, sal):
        ax.scatter(
            pnt.lon,
            pnt.lat,
            marker=".",
            s=markersize,
            color=color,
            transform=ccrs.Geodetic(),
        )
        ax.text(
            pnt.lon,
            pnt.lat,
            " " + pnt.label,
            color=color,
            font=dict(
                family=fontfamily,
                size=fontsize,
                weight=fontweight,
            ),
            transform=ccrs.Geodetic(),
        )

    # Return matplotlib figure as PIL.Image
    buf = BytesIO()
    fig.savefig(buf)
    buf.seek(0)

    return img.open(buf)

if __name__ == "__main__":
    location = "Sal"
    briefing_time1 = pd.Timestamp(2024, 8, 19).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 19, 12).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 8, 5).tz_localize("UTC")
    figure2 = ifs_dust(
        briefing_time1, "003H", current_time1, sattracks_fc_time1
        )