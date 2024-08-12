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
        return _overlay_nhc(
            image,
            proj=ccrs.Mercator(),
            extents=[-106.7, 20, -2.8, 41.8],
        )
    else:
        return image


def nhc_hovmoller(*args, add_overlay=True) -> img.Image:
    url = ANALYSIS_URLS["hovmoller"]
    response = requests.get(url)
    image = img.open(BytesIO(response.content))
    image = image.crop((0, 4 * 95, 722 - 165, 950))

    if add_overlay:
        tiles = create_tiles(image, num=6)

        overlayed_tiles = [
            _overlay_nhc(
                tile,
                proj=ccrs.Mercator(),
                extents=[-70, 38, 4, 24],
                color="white",
                fontsize=4,
                linewidth=0.4,
                markersize=2,
            ) for tile in tiles
        ]

    return vstack_images(overlayed_tiles)


def _overlay_nhc(
    image: img.Image,
    proj,
    extents,
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


def create_tiles(img, num=6):
    """Split an image into `num` vertical tiles."""
    width, height = img.size
    vchunksize = height // num

    return [
        img.crop([0, i * vchunksize, width, (i + 1) * vchunksize]) for i in range(num)
    ]


def vstack_images(images):
    """Vertically stack a series of PIL.Images objects."""
    # Create a new image with the total height and maximum width
    total_height = sum(image.height for image in images)
    max_width = max(image.width for image in images)

    concatenated_image = img.new("RGB", (max_width, total_height))

    # Paste the images onto the concatenated image
    y = 0
    for image in images:
        concatenated_image.paste(image, (0, y))
        y += image.height

    return concatenated_image
