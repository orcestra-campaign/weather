"""Plot satellite tracks"""
from matplotlib.axes import Axes
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import xarray as xr

import orcestra


def plot_sattrack(valid_time: pd.Timestamp,
                  ax: Axes,
                  satellite: str = "EARTHCARE"):
    valid_day = str(valid_time.date())
    sattracks = orcestra.sat.SattrackLoader(satellite, "2024-07-22"
                                            ).get_track_for_day(valid_day)
    splitted_sattracks = _split_sattracks(sattracks)
    for sattrack in splitted_sattracks:
        ax.plot(sattrack.lon, sattrack.lat, ls='-', color='blue', lw=1.5,
                transform = ccrs.PlateCarree())


def _split_sattracks(sattracks: xr.Dataset) -> list:
    splitted_sattracks = []
    start_index = 0
    N_times = sattracks.sizes['time']
    delta_time = np.timedelta64(20, 's')
    for i in range(1, N_times):
        if sattracks['time'][i] - sattracks['time'][i-1] > delta_time:
            end_index = i
            splitted_sattracks.append(
                sattracks.isel(time=slice(start_index, end_index))
                )
            start_index = end_index
        if i == N_times-1:
            splitted_sattracks.append(
                sattracks.isel(time=slice(start_index, N_times))
                )
    return splitted_sattracks