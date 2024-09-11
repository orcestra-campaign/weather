"""Functions to help efficiently loading healpix data."""

import numpy as np
import xarray as xr
from wblib.figures.briefing_info import ORCESTRA_DOMAIN


def load_forecast_datarray(forecast: xr.DataArray) -> xr.DataArray:
    """Loads a datarray from the server while minimizing downloads."""
    index = _get_orecesta_region_healpix_index(forecast)
    target = _empty_target_from_healpix(forecast)
    sample = _subsample(forecast, index).compute()
    upsampled = _upsample(sample, index, target)
    return upsampled


def _get_orecesta_region_healpix_index(datarray: xr.DataArray) -> np.ndarray:
    min_lon, max_lon, min_lat, max_lat = ORCESTRA_DOMAIN
    latitude = datarray.lat.compute()
    longitude = datarray.lon.compute()
    longitude = np.where(longitude > 180, longitude - 360, longitude)
    mask_index = latitude < max_lat + 1
    mask_index = np.logical_and(mask_index, latitude > min_lat - 1)
    mask_index = np.logical_and(mask_index, longitude < max_lon + 1)
    mask_index = np.logical_and(mask_index, longitude > min_lon - 1)
    return mask_index


def _empty_target_from_healpix(datarray: xr.DataArray) -> np.ndarray:
    target = xr.zeros_like(datarray).compute()
    return target


def _subsample(datarray: xr.DataArray, mask_index: np.ndarray):
    sample = datarray[dict(cell=mask_index)]
    return sample


def _upsample(subsampled_datarray: xr.DataArray, 
              mask_index: np.ndarray,
              target_datarray: xr.DataArray) -> xr.DataArray:
    upsampled = target_datarray.copy()
    upsampled.loc[dict(cell=mask_index)] = subsampled_datarray
    return upsampled