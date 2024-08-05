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
import healpy as hp
import xarray as xr

from wblib.figures.hifs import get_latest_forecast_issue_time

CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
FORECAST_PUBLISH_LAG = "6h"
SPEED_THRESHOLD = 3  # m/s
SPEED_MAX = 15  # m/s
SPEED_MIN = 0  # m/s
SPEED_COLORMAP = "YlGn"
FIGURE_SIZE = (15, 8)
FIGURE_BOUNDARIES = (-65, -5, -10, 20)
MESH_GRID_SIZE = 50
QUIVER_SKIP = 4

def surface_wind_quivers(briefing_time: pd.Timestamp, lead_hours: str) -> Figure:
    lead_delta = pd.Timedelta(hours=int(lead_hours[:-1]))
    issued_time = get_latest_forecast_issue_time(briefing_time)
    refdate = issued_time.strftime("%Y-%m-%d")
    print(refdate)
    # issued_time = '2024-08-04'
    # refdate = '2024-08-04'
    cat = intake.open_catalog(CATALOG_URL)
    ds = cat['HIFS'](refdate=refdate).to_dask().pipe(egh.attach_coords)
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
   
    # windspeed_100m = np.sqrt(ds['100u']**2 + ds['100v']**2)
    windspeed_10m = np.sqrt(ds['10u']**2 + ds['10v']**2)
    lon1 = np.linspace(lon_min, lon_max, MESH_GRID_SIZE)
    lat1 = np.linspace(lat_min, lat_max, MESH_GRID_SIZE)
    pix = xr.DataArray(
        hp.ang2pix(ds.crs.healpix_nside, *np.meshgrid(lon1, lat1), nest=True, lonlat=True),
        coords=(("lat1", lat1), ("lon1", lon1)),
    )
    valid_time = briefing_time + lead_delta
    valid_time = valid_time.tz_localize(None)

    # plotting
    sns.set_context('talk')
    fig, ax = plt.subplots(figsize=FIGURE_SIZE, subplot_kw={"projection": ccrs.PlateCarree()}, facecolor='white')
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    ax.coastlines(lw=0.8)
    # filled contours
    im1 = egh.healpix_show(
        windspeed_10m.sel(time=valid_time),
        method="linear",
        cmap=SPEED_COLORMAP,
        vmin=SPEED_MIN,
        vmax=SPEED_MAX,
    )   
    # quiver plot
    Q0 = ax.quiver(lon1[::QUIVER_SKIP], lat1[::QUIVER_SKIP], ds['10u'].sel(time=valid_time).isel(cell = pix)[::QUIVER_SKIP, ::QUIVER_SKIP]
                   , ds['10v'].sel(time = valid_time).isel(cell = pix)[::QUIVER_SKIP, ::QUIVER_SKIP]
                   , color = 'black', pivot = 'middle', scale_units = 'inches', width = 0.003, scale = 20) 
    ax.quiverkey(Q0, 0.95, 1.02, 10, r'$10 \frac{m}{s}$', labelpos='E', coordinates='axes', animated=True)
    # 3 m/s wind speed contour
    im2 = egh.healpix_contour(windspeed_10m.sel(time=valid_time), ax = ax, 
            levels = [SPEED_THRESHOLD], colors = 'r'
            )
    # axes formatting
    fig.colorbar(im1, label = '10m wind speed / m s$^{-1}$', shrink = 0.8)
    plt.clabel(im2, inline=True, fontsize=12, colors='r', fmt="%d")
    _speed_format_axes(briefing_time, issued_time, lead_delta, ax)
    matplotlib.rc_file_defaults()
    return fig
    
def _speed_format_axes(briefing_time, issued_time, lead_delta, ax):
    lon_min, lon_max, lat_min, lat_max = FIGURE_BOUNDARIES
    valid_time = briefing_time + lead_delta
    title_str = (
            f"Valid time: {valid_time.strftime('%Y-%m-%d %H:%M')} \n"
            f"Lead hours: {int(lead_delta.total_seconds() / 3600):03d}"
                     )
    ax.set_title(title_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(lon_min+5, lon_max-5, 6),0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(lat_min, lat_max, 5),0), crs=ccrs.PlateCarree()) 
    ax.set_ylabel("Latitude \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])
    annotation = f"Latest ECMWF IFS forecast initialization: {issued_time.strftime('%Y-%m-%d %H:%M %Z')}"
    ax.annotate(annotation,
                (-32.25, -9),
                fontsize=8,
                bbox = dict(facecolor='white',
                            edgecolor='none',
                            alpha=1))
    
# # if name == "main":
# briefing_time = pd.Timestamp(2024, 8, 4, tz="UTC")
# lead_hours = "048H"
# fig = surface_wind_quivers(briefing_time, lead_hours)
# # fig.show()
# fig.savefig("test.png")


