import pandas as pd
from orcestra.flightplan import (
    bco,
    LatLon,
    IntoCircle,
    FlightPlan,
)
import datetime


def _flight_HALO_20240916a():
    flight_time = pd.Timestamp(2024, 9, 16, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3 * 1.852

    c_north = LatLon(lat=11.5, lon=-46.927411728395064, label='c_north', fl=None, time=None, note=None)
    c_south = LatLon(lat=7, lon=-50).assign(label="c_south")
    c_mid = LatLon(lat=8.7, lon=-47.45979058641976, label='c_mid', fl=None, time=None, note=None)

    ec_north = LatLon(lat=9, lon=-47.40303132716049, label='ec_north', fl=None, time=None, note=None)
    ec_south = LatLon(lat=3.0, lon=-48.52921481024375, label='ec_south', fl=None, time=None, note=None)
    ec_under = LatLon(lat=5.5, lon=-48.06194174637457, label='ec_under', fl=None, time=datetime.datetime(2024, 9, 16, 17, 16, 3, 963900, tzinfo=datetime.timezone.utc), note='meet EarthCARE')

    pace_north = LatLon(lat=8, lon=-50.3673333333333, label="pace_north",
                        fl=None, time=None, note=None)
    pace_under = LatLon(lat=6, lon=-49.943, label="pace_under",
                        fl=None, time=None, note=None)
    pace_south = LatLon(lat=3.0, lon=-49.3103333333333, label="pace_south",
                        fl=None, time=None, note=None)

    c_south_entry = LatLon(lat=8.1, lon=-50.3885, label="c_south_entry",
                        fl=None, time=None, note=None)
    c_north_home = LatLon(lat=10.25, lon=-47.165854320987656, label='c_north_home', fl=None, time=None, note=None)

    c_wait4EC = LatLon(lat=3.0, lon=-49.3103333333333, label="c_wait4EC", fl=None, time=None, note=None)

    # point_atlantic  = LatLon(lat= ec_south.lat, lon= -47).assign(label = "c_south")

    waypoints = [
        # airport.assign(fl=0, time = ""),
        airport.assign(fl=0),
        IntoCircle(c_mid.assign(fl=410), radius, -360),
        c_south_entry.assign(fl=410),
        IntoCircle(c_south.assign(fl=410), radius, -360),
        pace_north.assign(fl=450),
        pace_under.assign(fl=450),
        # point_atlantic.assign(fl=450),
        IntoCircle(c_wait4EC.assign(fl=450), radius=36e3, angle=280),
        pace_south.assign(fl=450),
        ec_south.assign(fl=450),
        ec_under.assign(fl=450),
        ec_north.assign(fl=450),
        IntoCircle(c_north.assign(fl=450), radius, 360),
        c_north_home.assign(fl=450),
        airport.assign(fl=0),
    ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240916a()
    print(path)
