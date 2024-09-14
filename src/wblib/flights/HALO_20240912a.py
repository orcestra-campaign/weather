import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    bco,
    LatLon,
    IntoCircle,
    FlightPlan,
)
import datetime


def _flight_HALO_20240912a():
    flight_time = pd.Timestamp(2024, 9, 12, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3 * 1.852

    c_northeast  = LatLon(lat=12.0, lon=-48.61704672839506, label='c_northeast', fl=None, time=None, note=None)
    c_southwest  = LatLon(lat=10.5, lon=-52.40370419623573, label='c_southwest', fl=None, time=None, note=None)
    c_southeast  = LatLon(lat=9.0, lon=-49.18841539648257, label='c_southeast', fl=None, time=None, note=None)
    c_northwest  = LatLon(lat=13.5, lon=-51.8282961728395, label='c_northwest', fl=None, time=None, note=None)


    ec_north = LatLon(lat=15.0, lon=-51.53701707317073, label='ec_north', fl=None, time=None, note=None)
    ec_south = LatLon(lat=9.0, lon=-52.68841539648257, label='ec_south', fl=None, time=None, note=None)
    ec_under = LatLon(lat=12.0, lon=-52.11704672839506, label='ec_under', fl=None, time=datetime.datetime(2024, 9, 12, 17, 35, 38, 794753, tzinfo=datetime.timezone.utc), note='meet EarthCARE')
    ec_under_north = LatLon(lat=13.0, lon=-51.92483071935783, label='ec_under_n', fl=None, time=None, note='EC align north')
    ec_under_south = LatLon(lat=11.0, lon=-52.30840388888889, label='ec_under_s', fl=None, time=None, note='EC align south')


    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        IntoCircle(c_southeast.assign(fl=410), radius, 330, enter= 0),
        IntoCircle(c_northeast.assign(fl=430), radius, -360, enter = 180),
        IntoCircle(c_northwest.assign(fl=430), radius, -360, enter = 180),
        c_northwest.towards(c_southwest, distance = -radius).assign(fl = 450, label = "ec_north"), 
        ec_under_north.assign(fl=450),
        ec_under.assign(fl=450),
        ec_under_south.assign(fl=450),
        ec_south.assign(fl=450),  
        IntoCircle(c_southwest.assign(fl=450), radius, 360),   
        airport.assign(fl=0),
        ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240912a()
    print(path)
