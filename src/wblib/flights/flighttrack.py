import pandas as pd

from wblib.flights._define_flights import FLIGHTS
from orcestra.flightplan import plot_path, path_preview
from wblib.figures.hifs import get_valid_time

def get_python_flightdata(
        flight_id: str
        ) -> dict:
    flight_time, flight_track = FLIGHTS[flight_id]()
    flight = {
        'time': flight_time,
        'track': flight_track,
        }
    return flight


def plot_python_flighttrack(
        flight: dict,
        briefing_time: pd.Timestamp,
        lead_hours: str,
        ax,
        **kwargs
        ):
    valid_time = get_valid_time(briefing_time, lead_hours)
    if flight['time'] == valid_time:
        plot_path(flight["track"], ax, **kwargs)


if __name__ == "__main__":
    flight_id = 'HALO-20240811a'
    flight = get_python_flightdata(flight_id)