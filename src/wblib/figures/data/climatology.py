"""
Get ERA5 climatology to be used in the weather reports.

This module download 
"""

import intake
import numpy as np
from importlib import resources

import easygems.healpix as egh

import wblib

VARIABLES = ["tcwv"]
CATALOG_URL = "https://tcodata.mpimet.mpg.de/internal.yaml"
CLIMATOLOGY_CUT_OUT_TIME = "2023-01-01"
CLIMATOLOGY_FILE = "hera5_climatology.nc"


def download_hera5_climatology():
    hera5 = get_hera5_climatology()
    hera5_climatology_path = str(resources.files(wblib) / CLIMATOLOGY_FILE)
    hera5.to_netcdf(hera5_climatology_path)


def get_hera5_climatology():
    cat = intake.open_catalog(CATALOG_URL)
    hera5 = cat.HERA5(time="P1D").to_dask().pipe(egh.attach_coords)
    hera5 = hera5[VARIABLES]
    hera5 = hera5.where(
        hera5["time"] < np.datetime64(CLIMATOLOGY_CUT_OUT_TIME), drop=True
    )
    hera5 = hera5.rolling(time=7, center=True).mean()
    hera5 = hera5.sel(time=hera5["time"].dt.month.isin([9, 10]))
    hera5 = hera5.groupby("time.dayofyear").mean()
    return hera5

if __name__ == "__main__":
    download_hera5_climatology()
