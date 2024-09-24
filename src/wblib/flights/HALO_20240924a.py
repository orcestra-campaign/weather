import pandas as pd
from orcestra.flightplan import (
    tbpb,
    LatLon,
    IntoCircle,
    FlightPlan,
)
from orcestra.flightplan import tbpb
import datetime


def _flight_HALO_20240924a():
    flight_time = pd.Timestamp(2024, 9, 24, 12, 00, 0).tz_localize("UTC")

    airport = tbpb
    radius = 72e3*1.852

    # Create elements of track
    c_west_in = LatLon(12.2,-56.0).assign(label = "c_west_in")
    c_east_out = LatLon(11,-50).assign(label = "c_east_out")

    c_west = c_west_in.towards(c_east_out, distance = radius).assign(label = "c_west")
    c_east = c_west.towards(c_east_out, distance = 2*radius+radius).assign(label = "c_east")

    ec_north = LatLon(lat=14.0, lon=-58.59031000617665, label='ec_north', fl=None, time=None, note=None)
    ec_south = LatLon(lat=10.0, lon=-59.35789308641975, label='ec_south', fl=None, time=None, note=None)
    ec_under = LatLon(lat=12.0, lon=-58.976008305032416, label='ec_under', fl=None, time=datetime.datetime(2024, 9, 24, 18, 2, 47, 514356, tzinfo=datetime.timezone.utc), note='meet EarthCARE')

    ferry = ec_out = ec_under.assign(time=None, note=None)
    
    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        ferry.assign(fl=390),
        c_west_in.assign(fl = 410),
        IntoCircle(c_west.assign(fl=410), radius, -360), 
        ec_south.assign(fl=430),
        ec_under.assign(fl=430),
        ec_north.assign(fl=430),  
        ec_out.assign(fl=450),
        c_west_in.assign(fl = 450),
        IntoCircle(c_west.assign(fl=450), radius, -360),
        IntoCircle(c_west.assign(fl=450), radius, -360),
        ferry.assign(fl=450, time=None),
        airport.assign(fl=0),
        ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240924a()
    print(path)
