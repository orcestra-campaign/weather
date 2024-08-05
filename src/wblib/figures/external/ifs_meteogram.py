import requests
from PIL import Image as img
from io import BytesIO
import pandas as pd

from wblib.figures.hifs import get_latest_forecast_issue_time

ANALYSIS_URLS = {
    "IFS_meteogram": 'https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/',
}

def _create_params(location: str, issued_time: str) -> dict:
    coords = _get_coordinates(location)
    params = {
        'lat': coords[0],
        'lon': coords[1],
        'station_name': '',
        'base_time': issued_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    return params


def _get_coordinates(location: str) -> tuple:
    if location == 'Sal':
        lat = '16.73883'    #degN
        lon = '-22.942'     #degE
    elif location == 'Barbados':
        lat = '13.075418'   #degN
        lon = '-59.493768'  #degE
    else:
        error_str = ("Please provide a valid location. Valid locations are " +
                     "currently: 'Sal' or 'Barbados'.")
        raise ValueError(error_str)
    return (lat, lon)


def ifs_meteogram(location: str, briefing_time: str) -> img.Image:
    url = ANALYSIS_URLS["IFS_meteogram"]
    issued_time = get_latest_forecast_issue_time(briefing_time)
    params = _create_params(location, issued_time)
    headers = {
        'accept': 'application/json',
    }
    
    response = requests.get(
        url,
        params=params,
        headers=headers,
    )

    figure_url = response.json().get('data').get('link').get('href')
    response = requests.get(figure_url)
    image = img.open(BytesIO(response.content))
    return image

if __name__ == "__main__":
    location = 'Sal'
    briefing_time = pd.Timestamp("2024-08-05").tz_localize("UTC")
    figure = ifs_meteogram(location, briefing_time)