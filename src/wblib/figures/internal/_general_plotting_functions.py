import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd

import orcestra.sat

def _plot_sattrack(valid_time, ax):
    valid_day = str(valid_time.date())
    sattrack = orcestra.sat.SattrackLoader("EARTHCARE", "2024-07-22"
                                           ).get_track_for_day(valid_day)
    print(sattrack)
    ax.plot(sattrack.lon, sattrack.lat, ls='-', color='blue', lw=1.5,
            transform = ccrs.PlateCarree())