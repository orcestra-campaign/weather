"""Plot satellite tracks"""
from matplotlib.axes import Axes
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import xarray as xr

from orcestra.sat import SattrackLoader

from wblib.figures.briefing_info import get_valid_time


def plot_sattrack(ax: Axes,
                  briefing_time: pd.Timestamp,
                  lead_hours: str,
                  sattracks_fc_time: pd.Timestamp,
                  satellite: str = "EARTHCARE",
                  which_orbit: list = ["ascending"],
                  kind: str = "PRE",
                  roi: str = "BARBADOS",
                  ):
    valid_time = get_valid_time(briefing_time, lead_hours)
    valid_time = valid_time.tz_localize(None).date()
    sattracks = SattrackLoader(satellite, sattracks_fc_time, kind=kind,
                               roi=roi).get_track_for_day(valid_time)
    splitted_sattracks = _split_sattracks(sattracks)
    splitted_sattracks = _add_orbit_attribute(splitted_sattracks)
    for sattrack in splitted_sattracks:
        if sattrack.attrs['orbit'] in which_orbit:
            ax.plot(sattrack.lon, sattrack.lat, ls=':', color='black', lw=1.8,
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

def _add_orbit_attribute(sattrack_list: list) -> list:
    for i, sattrack in enumerate(sattrack_list):
        dlat_dt = sattrack['lat'].diff(dim='time')
        if all(dlat_dt < 0):
            orbit = "descending"
        elif all(dlat_dt > 0):
            orbit = "ascending"
        else:
            raise ValueError('Unclear satellite orbit, please have a look.')
        sattrack_list[i] = sattrack_list[i].assign_attrs(orbit=orbit)
    return sattrack_list


if __name__ == "__main__":
    sattracks = SattrackLoader('EARTHCARE', "2024-08-21", kind="PRE",
                               ).get_track_for_day("2024-08-22")
    splitted_sattracks = _split_sattracks(sattracks)
    print(splitted_sattracks)
