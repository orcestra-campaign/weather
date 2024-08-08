"""Download and create plot form the NCH"""
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image as img
import requests

from io import BytesIO

from orcestra import bco, sal


ANALYSIS_URLS = {
    "seven_days_outlook": "https://www.nhc.noaa.gov/xgtwo/two_atl_7d0.png",
    "surface_analysis_atlantic": "https://ocean.weather.gov/UA/Atl_Tropics.gif",
    "hovmoller": "https://www.nhc.noaa.gov/tafb_latest/methov1latest.gif",
}


def nhc_seven_days_outlook(*args) -> img.Image:
    url = ANALYSIS_URLS["seven_days_outlook"]
    response = requests.get(url)
    image = img.open(BytesIO(response.content))
    return image


def nhc_surface_analysis_atlantic(*args, add_overlay=True) -> img.Image:
    url = ANALYSIS_URLS["surface_analysis_atlantic"]
    response = requests.get(url)
    image = img.open(BytesIO(response.content))
    image = image.crop((0, 300, 1720, 1260-300))
    
    if add_overlay:
        return _overlay_nhc(image)
    else:
        return image


def nhc_hovmoller(*args) -> img.Image:
    url = ANALYSIS_URLS["hovmoller"]
    response = requests.get(url)
    image = img.open(BytesIO(response.content))
    return image


def _overlay_nhc(
    image: img.Image,
    color="#00267F",
    linewidth=1.2,
    fontfamily="monospace",
    fontsize="small",
    fontweight="bold",
    markersize=36,
    dpi=200,
):
    """Overlay the NHC surface analysis with coastlines and waypoints."""
    nhc = np.asarray(image.convert("RGBA"))
    ny, nx, _ = nhc.shape

    # Hard-coded extent and map projection
    # (Needs to be adjusted for ohter map producs!)
    proj = ccrs.Mercator()
    extents = [-106.7, 20, -2.8, 41.8]

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
    ax.spines["geo"].set_visible(False)
    ax.coastlines(color=color, lw=linewidth, resolution="110m")

    # Plot the original image based on it's geolocation (projection + extent)
    ax.imshow(nhc, extent=img_extents, transform=proj)
    ax.set_extent(extents=img_extents, crs=proj)

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