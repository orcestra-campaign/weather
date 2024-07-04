from matplotlib import pyplot as plt
import xarray as xr
import requests
from io import BytesIO
import rioxarray
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature


execution_datetime = pd.Timestamp(2024, 7, 4, 11)
date_str = execution_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
product = "Clean_Infrared"
lon_start = 15
lon_end = -70
lat_start = 25
lat_end = -10

url = f'https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME={date_str}&BBOX={lon_start},{lon_end},{lat_start},{lat_end}&CRS=EPSG:4326&LAYERS=GOES-East_ABI_Band13_{product}&WRAP=x&FORMAT=image/tiff&WIDTH=2048&HEIGHT=910'
response = requests.get(url, stream=True)
response.raise_for_status()
raster = rioxarray.open_rasterio(BytesIO(response.content))

# Assume the raster has bands in the order: Red, Green, Blue
red = raster.sel(band=1)
green = raster.sel(band=2)
blue = raster.sel(band=3)

# Combine the bands into an RGB image DataArray
rgb = xr.concat([red, green, blue], dim='band')

# Compute image aspect ratio
x = 10
y = (lat_start - lat_end) / (lon_start - lon_end) * 10

ax = rgb.plot.imshow(rgb='band', figsize=(x, y))


# Set axis labels and title
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title(product)

# Display the plot
plt.show()