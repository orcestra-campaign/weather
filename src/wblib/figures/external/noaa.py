"""Download and create plot form the NCH"""

import numpy as np
from PIL import Image
import requests
from io import BytesIO
from IPython.display import display

from wblib._plots import get_fig_size

ANALYSIS_URLS = {
    "two_days_outlook": "https://www.nhc.noaa.gov/xgtwo/two_atl_2d0.png",
    "seven_days_outlook": "https://www.nhc.noaa.gov/xgtwo/two_atl_7d0.png",
    "surface_analysis_atlantic": "https://ocean.weather.gov/UA/Atl_Tropics.gif" 
}

def two_days_outlook() -> None:
    url = ANALYSIS_URLS["two_days_outlook"]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    display(image)


def seven_days_outlook() -> None:
    url = ANALYSIS_URLS["seven_days_outlook"]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    display(image)    


def surface_analysis_atlantic() -> None:
    url = ANALYSIS_URLS["surface_analysis_atlantic"]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))  
    image = image.crop((0, 300, 1720, 1260-300))
    display(image)    