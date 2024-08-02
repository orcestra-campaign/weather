"""Download and create plot form the NCH"""
import numpy as np
from PIL import Image as img
import requests

from io import BytesIO


ANALYSIS_URLS = {
    "seven_days_outlook": "https://www.nhc.noaa.gov/xgtwo/two_atl_7d0.png",
    "surface_analysis_atlantic": "https://ocean.weather.gov/UA/Atl_Tropics.gif"
}


def nhc_seven_days_outlook(*args) -> img.Image:
    url = ANALYSIS_URLS["seven_days_outlook"]
    response = requests.get(url)
    image = img.open(BytesIO(response.content))
    return image


def nhc_surface_analysis_atlantic(*args) -> img.Image:
    url = ANALYSIS_URLS["surface_analysis_atlantic"]
    response = requests.get(url)
    image = img.open(BytesIO(response.content))
    image = image.crop((0, 300, 1720, 1260-300))
    return image
