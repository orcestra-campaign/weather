import requests
from PIL import Image as img
from io import BytesIO
import pandas as pd

from wblib.figures.hifs import expected_issue_time
from wblib.figures.hifs import get_valid_time


ANALYSIS_URLS = {
    "ifs_meteogram": "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/",
    "ifs_dust": "https://charts.ecmwf.int/opencharts-api/v1/products/aerosol-forecasts/",
    "ifs_cloud_top_height": "https://charts.ecmwf.int/opencharts-api/v1/products/medium-cloud-parameters/",
}


def ifs_dust(
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp
        ) -> img.Image:
    url = ANALYSIS_URLS["ifs_dust"]
    params = _create_ifs_var_params(
        briefing_time, lead_hours, current_time,
        var="composition_duaod550", projection='classical_west_tropic',
        )
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    figure_url = response.json().get("data").get("link").get("href")
    response = requests.get(figure_url)
    image = img.open(BytesIO(response.content))
    image = image.crop((1300, 400, 1900, 720))
    return image


def ifs_cloud_top_height(
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp
        ) -> img.Image:
    url = ANALYSIS_URLS["ifs_cloud_top_height"]
    params = _create_ifs_var_params(
        briefing_time, lead_hours, current_time,
        var="hcct", projection="opencharts_west_tropic",
        )
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    figure_url = response.json().get("data").get("link").get("href")
    response = requests.get(figure_url)
    image = img.open(BytesIO(response.content))
    image = image.crop((1300, 500, 1900, 800))
    return image


def ifs_meteogram(current_time: pd.Timestamp, location: str) -> img.Image:
    url = ANALYSIS_URLS["ifs_meteogram"]
    params = _create_ifs_meteogram_params(location)
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


def _create_ifs_var_params(
        briefing_time: pd.Timestamp,
        lead_hours: str,
        current_time: pd.Timestamp,
        var: str,
        projection: str,
        ):
    issue_time = expected_issue_time(briefing_time, current_time)
    valid_time = get_valid_time(briefing_time, lead_hours)
    valid_time = valid_time.tz_localize(None)
    params = {
        'valid_time': valid_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'base_time': issue_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'projection': projection,
        'layer_name': var,
    }
    return params


def _create_ifs_meteogram_params(location: str) -> dict:
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
    briefing_time1 = pd.Timestamp(2024, 8, 9).tz_localize("UTC")
    current_time1 = pd.Timestamp(2024, 8, 9, 12).tz_localize("UTC")
    sattracks_fc_time1 = pd.Timestamp(2024, 8, 5).tz_localize("UTC")
    figure1 = ifs_meteogram(
        current_time1, location
        )
    figure2 = ifs_dust(
        briefing_time1, "108H", current_time1, sattracks_fc_time1
        )
    figure3 = ifs_cloud_top_height(
        briefing_time1, "108H", current_time1, sattracks_fc_time1
        )
    figure3.show()