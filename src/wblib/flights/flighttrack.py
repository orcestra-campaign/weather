from wblib.flights._define_flights import FLIGHTS
from orcestra.flightplan import path_preview

def get_python_flightdata(
        flight_id: str):
    flight_time, flight_track = FLIGHTS[flight_id]()
    flight = {
        'time': flight_time,
        'track': flight_track,
        }
    return flight

if __name__ == "__main__":
    flight_id = 'HALO-20240811a'
    flight = get_python_flightdata(flight_id)
    