"""generates surface wind speed plots with low wind speed regions identified using ECMWF IFS."""

import intake
import easygems.healpix as egh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.figure import Figure
import seaborn as sns
sns.set_context('talk')
import healpy as hp
import xarray as xr

CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
FORECAST_PUBLISH_LAG = "6h"
SPEED_THRESHOLD = 3  # m/s
SPEED_MAX = 15  # m/s
SPEED_MIN = 0  # m/s
SPEED_COLORMAP = "YlGn"
FIGURE_SIZE = (15, 8)
FIGURE_BOUNDARIES = (-65, -5, -10, 20)

date = "2024-08-04"
plot_time = "2024-08-11T12:00:00.000000000"

cat = intake.open_catalog("https://tcodata.mpimet.mpg.de/internal.yaml")
ds = cat['HIFS'](refdate=date, reftime='12').to_dask().pipe(egh.attach_coords)
windspeed_100m = np.sqrt(ds['100u']**2 + ds['100v']**2)
windspeed_10m = np.sqrt(ds['10u']**2 + ds['10v']**2)

lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES

fig, ax = plt.subplots(figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()})
ax.set_extent([lon_min, lon_max, lat_min, lat_max])
ax.coastlines(lw=0.8)
im1 = egh.healpix_show(
    windspeed_10m.sel(time=plot_time),
    method="linear",
    cmap=SPEED_COLORMAP,
    vmin=SPEED_MIN,
    vmax=SPEED_MAX,
)
fig.colorbar(im1, shrink = 0.8)

mesh_grid_size = 50

lon1 = np.linspace(lon_min, lon_max, mesh_grid_size)
lat1 = np.linspace(lat_min, lat_max, mesh_grid_size)

pix = xr.DataArray(
    hp.ang2pix(ds.crs.healpix_nside, *np.meshgrid(lon1, lat1), nest=True, lonlat=True),
    coords=(("lat1", lat1), ("lon1", lon1)),
)

skip = 4
Q0 = ax.quiver(lon1[::skip], lat1[::skip], ds['100u'].sel(time=plot_time).isel(cell = pix)[::skip, ::skip], ds['100v'].sel(time = plot_time).isel(cell = pix)[::skip, ::skip], 
                color = 'black', pivot = 'middle', scale_units = 'inches', width = 0.003, scale = 20) 

ax.quiverkey(Q0, 0.95, 1.02, 10, r'$10 \frac{m}{s}$', labelpos='E', coordinates='axes', animated=True)


im2 = egh.healpix_contour(windspeed_10m.sel(time=plot_time), ax = ax, 
            levels = [SPEED_THRESHOLD], colors = 'r'
            )
plt.clabel(im2, inline=True, fontsize=12, colors='r', fmt="%d")
ax.set_xticks(np.round(np.linspace(lon_min+5, lon_max-5, 6),0), crs=ccrs.PlateCarree())
ax.set_yticks(np.round(np.linspace(lat_min, lat_max, 5),0), crs=ccrs.PlateCarree()) 
ax.set_ylabel('Latitude/ \N{DEGREE SIGN}N')
ax.set_xlabel('Longitude/ \N{DEGREE SIGN}E')

plt.show()