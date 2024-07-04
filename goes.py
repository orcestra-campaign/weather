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
product = "Band13_Clean_Infrared" # "Band13_Clean_Infrared" or "Band2_Red_Visible_1km"
lon_start = -70
lon_end = 15
lat_start = -10
lat_end = 25

url = f'https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME={date_str}&BBOX={lat_start},{lon_start},{lat_end},{lon_end}&CRS=EPSG:4326&LAYERS=GOES-East_ABI_{product}&WRAP=x&FORMAT=image/tiff&WIDTH=2048&HEIGHT=910'
response = requests.get(url, stream=True)
response.raise_for_status()
raster = rioxarray.open_rasterio(BytesIO(response.content))

# Assume the raster has bands in the order: Red, Green, Blue
red = raster.sel(band=1)
green = raster.sel(band=2)
blue = raster.sel(band=3)

# Combine the bands into an RGB image DataArray
rgb = xr.concat([red, green, blue], dim='band')


# Compute figure aspect ratio
x_fig = 10
y_fig = (lat_start - lat_end) / (lon_start - lon_end) * x_fig

# Set up the figure and axis using cartopy
fig, ax = plt.subplots(figsize=(x_fig, y_fig), subplot_kw={'projection': ccrs.PlateCarree()})

# Plot the raster data (transpose to match the expected dimension order)
extent = [raster['x'].min(), raster['x'].max(), raster['y'].min(), raster['y'].max()]
ax.imshow(rgb.transpose('y', 'x', 'band').values, extent=extent, origin='upper')

# Add coastlines
ax.coastlines()

# Set the tick labels to the actual coordinate values
ax.set_xticks(np.round(np.linspace(lon_start, lon_end, 10),0), crs=ccrs.PlateCarree())
ax.set_yticks(np.round(np.linspace(lat_start, lat_end, 5),0), crs=ccrs.PlateCarree())

# Set axis labels and title
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title(product)

# Display the plot
plt.show()