from wblib.flights.HALO_20240811a import _flight_HALO_20240811a
from wblib.flights.HALO_20240813a import _flight_HALO_20240813a

FLIGHTS = {
     "HALO-20240811a": _flight_HALO_20240811a,
     "HALO-20240813a": _flight_HALO_20240813a,
}

if __name__ == "__main__":
     print(FLIGHTS['HALO-20240811a'])