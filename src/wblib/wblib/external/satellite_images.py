from wblib import plotting_config
from matplotlib import pyplot as plt
import xarray as xr
import requests
from io import BytesIO
import rioxarray
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def get_product_specs(product):
    if product == 'infrared':
        product_name = 'Band13_Clean_Infrared'
        figure_title = 'GOES infrared satellite image'
    elif product == 'visible':
        product_name = 'Band2_Red_Visible_1km'
        figure_title = 'GOES visible satellite image'
    else:
        raise RuntimeError("Invalid product name, enter 'infrared' or 'visible'.")
    return product_name, figure_title


execution_datetime = pd.Timestamp(2024, 7, 4, 11)
date_str = execution_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
product_str = 'infrared'

def satellite_image(date = date_str, product = product_str):

    lon_min, lon_max, lat_min, lat_max = plotting_config.box_boundaries_lonlat()
    product_name, figure_title = get_product_specs(product)

    # Get tiff file from website
    url = f'https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME={date_str}&BBOX={lat_min},{lon_min},{lat_max},{lon_max}&CRS=EPSG:4326&LAYERS=GOES-East_ABI_{product_name}&WRAP=x&FORMAT=image/tiff&WIDTH=2048&HEIGHT=910'
    response = requests.get(url, stream=True)
    response.raise_for_status()
    raster = rioxarray.open_rasterio(BytesIO(response.content))

    # Combine the bands into an RGB image DataArray
    red = raster.sel(band=1)
    green = raster.sel(band=2)
    blue = raster.sel(band=3)
    rgb = xr.concat([red, green, blue], dim='band')

    # Compute figure aspect ratio 
    # QUESTION: Should this be a plotting_config.py?
    x_fig = 10
    y_fig = (lat_min - lat_max) / (lon_min - lon_max) * x_fig

    # Plotting
    fig, ax = plt.subplots(figsize=(x_fig, y_fig), subplot_kw={'projection': ccrs.PlateCarree()})
    extent = [raster['x'].min(), raster['x'].max(), raster['y'].min(), raster['y'].max()]
    ax.imshow(rgb.transpose('y', 'x', 'band').values, extent=extent, origin='upper')
    ax.coastlines()
    ax.set_xticks(np.round(np.linspace(lon_min, lon_max, 10),0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(lat_min, lat_max, 5),0), crs=ccrs.PlateCarree())
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(figure_title)
    fig.tight_layout()

    # Save plot 
    # CAUTION: Path still needs to be adapted for final workflow
    plt.savefig(product + '_example_image.png', dpi=150)


satellite_image()