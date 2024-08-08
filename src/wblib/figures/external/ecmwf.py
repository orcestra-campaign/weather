import requests
from PIL import Image as img
from io import BytesIO
import pandas as pd


ANALYSIS_URLS = {
    "IFS_meteogram": "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/",
}


def ifs_meteogram(current_time: pd.Timestamp, location: str) -> img.Image:
    url = ANALYSIS_URLS["IFS_meteogram"]
    params = _create_params(location)
    headers = {
        "accept": "application/json",
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    figure_url = response.json().get("data").get("link").get("href")
    response = requests.get(figure_url)
    image = img.open(BytesIO(response.content))
    return image


def _create_params(location: str) -> dict:
    coords = _get_coordinates(location)
    params = {"lat": coords[0], "lon": coords[1], "station_name": ""}
    return params


def _get_coordinates(location: str) -> tuple:
    if location == "Sal":
        lat = "16.73883"  # degN
        lon = "-22.942"  # degE
    elif location == "Barbados":
        lat = "13.075418"  # degN
        lon = "-59.493768"  # degE
    else:
        error_str = (
            "Please provide a valid location. Valid locations are "
            + "currently: 'Sal' or 'Barbados'."
        )
        raise ValueError(error_str)
    return (lat, lon)


if __name__ == "__main__":
    location = "Sal"
    current_time = pd.Timestamp("2024-08-07").tz_localize("UTC")
    figure = ifs_meteogram(current_time, location)
