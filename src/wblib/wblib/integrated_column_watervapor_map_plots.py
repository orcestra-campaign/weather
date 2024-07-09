import intake
import easygems.healpix as egh
import cmocean
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import cartopy.feature as cfeature
import seaborn as sns
sns.set_context('talk')
import pandas as pd
import datashader
from datashader.mpl_ext import dsshow
import datashader.transfer_functions as tf
import warnings
warnings.filterwarnings("ignore")

cat = intake.open_catalog("https://tcodata.mpimet.mpg.de/internal.yaml")

def get_init_dates(flight_day, flight_month, flight_year):
    days_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    day_arr = np.array([flight_day-5 + days_month[flight_month-2]*((flight_day-5)<=0), flight_day-4 + days_month[flight_month-2]*((flight_day-4)<=0)
                        , flight_day-3 + days_month[flight_month-2]*((flight_day-3)<=0), flight_day-2 + days_month[flight_month-2]*((flight_day-1)<=0)
                        , flight_day-1 + days_month[flight_month-2]*((flight_day-1)<=0)])
    
    month_arr = np.array([flight_month - 1*((flight_day-5)<=0), flight_month - 1*((flight_day-4)<=0)
                        , flight_month - 1*((flight_day-3)<=0), flight_month - 1*((flight_day-1)<=0)
                        , flight_month - 1*((flight_day-1)<=0)])
    # date_arr = [str(flight_year) + '-' + str(month_arr[i]) + '-' + str(day_arr[i]) for i in np.arange(len(day_arr))]

    date_arr = [pd.Timestamp(flight_year, month_arr[i], day_arr[i], 0).strftime("%Y-%m-%d") for i in np.arange(len(day_arr))]

    return date_arr

def icwv_maps(cat, flight_date_arr, colors_arr, hours_from_init):
    init_times = get_init_dates(flight_date_arr[2], flight_date_arr[1], flight_date_arr[0])

    fig, ax = plt.subplots(figsize=(15, 8), subplot_kw={"projection": ccrs.PlateCarree()}, facecolor = 'white')
    fig.canvas.draw_idle()
    ax.coastlines(lw=1.0, color = 'k')
    
    days_from_init = int(hours_from_init/24) 
    hours_from_init_updated = hours_from_init - days_from_init*24
    ax.set_title('Forecast on ' + pd.Timestamp(flight_date_arr[0], flight_date_arr[1]
                                         , flight_date_arr[2]+days_from_init, hours_from_init_updated).strftime("%Y-%m-%dT%H:%M:%S") 
                                         + '; red line (48 mm) ref time = -1 day')
    
    for date_n, date in enumerate(init_times):
        ds = cat.HIFS(refdate=date).to_dask().pipe(egh.attach_coords)
        im2 = egh.healpix_contour(
            ds["tcwv"].sel(time=pd.Timestamp(flight_date_arr[0], flight_date_arr[1]
                                         , flight_date_arr[2]+days_from_init, hours_from_init_updated).strftime("%Y-%m-%dT%H:%M:%S")), ax = ax, 
            levels = [48], colors = colors_arr[date_n], linewidth = 2
            )
    
    im = egh.healpix_show(
        ds["tcwv"].sel(time=pd.Timestamp(flight_date_arr[0], flight_date_arr[1]
                                         , flight_date_arr[2]+days_from_init, hours_from_init_updated).strftime("%Y-%m-%dT%H:%M:%S")),
        method="linear",
        cmap="bone",
        vmin=0,
        vmax=65,
        )
    fig.colorbar(im,label='IWV / kg m$^{-2}$',shrink=0.9)
    ax.set_extent([-70, 0, -25, 25])
    ax.set_xticks(np.round(np.linspace(-70, 10, 9),0), crs=ccrs.PlateCarree())
    ax.set_yticks(np.round(np.linspace(-20, 20, 5),0), crs=ccrs.PlateCarree()) 
    ax.set_ylabel('Latitude/ \N{DEGREE SIGN}N')
    ax.set_xlabel('Longitude/ \N{DEGREE SIGN}E')
    date =pd.Timestamp(flight_date_arr[0], flight_date_arr[1]
                                         , flight_date_arr[2]+days_from_init, hours_from_init_updated).strftime("%Y-%m-%dT%H:%M:%S") 
    fig.show()
    fig.savefig('tcwv_'+str(date)+'.png', bbox_inches='tight')
    # plt.close()

    return None

# the following are the color schemes I got from this website https://www.color-hex.com/
# the ordering of the colors (bright orange and red indicate the latest available refdate)
orange_creamsickle = ['#ffc99d', '#ffa472', '#ff9c59', '#ff7e26', '#ff580f']
rainbow_dash = ['#0392cf', '#7bc043', '#fdf498', '#f37736', '#ee4035'] 

icwv_maps(cat, [2024, 6, 4], orange_creamsickle, 12) # weather 12 hours from the flight day 2024-06-04 