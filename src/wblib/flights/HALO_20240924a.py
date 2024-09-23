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

    ec_north = LatLon(lat=16.5, lon=-58.09336235330451, label='ec_north', fl=None, time=None, note=None)
    ec_south = LatLon(lat=11.5, lon=-59.063401667181225, label='ec_south', fl=None, time=None, note=None)
    ec_under = LatLon(lat=14.0, lon=-58.58195379864113, label='ec_under', fl=None, time=datetime.datetime(2024, 9, 24, 18, 2, 14, 780111, tzinfo=datetime.timezone.utc), note='meet EarthCARE')

    c_pirouette = (c_west.towards(c_east_out, distance = radius)).towards(ec_north, fraction = 0.5).assign(label = "c_pirouette")

    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        c_west_in.assign(fl = 410),
        IntoCircle(c_west.assign(fl=410), radius, -360),
        IntoCircle(c_east.assign(fl=430), radius, -360), 
        IntoCircle(c_east.assign(fl=430), radius, -360), 
        IntoCircle(c_west.assign(fl=450), radius, -360), 
        IntoCircle(c_pirouette.assign(fl=450), radius*0.3, -360),
        ec_north.assign(fl=450),  
        ec_under.assign(fl=450),
        ec_south.assign(fl=450),
        c_west_in.assign(fl = 450),
        IntoCircle(c_west.assign(fl=450), radius, -360), 
        airport.assign(fl=0),
        ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240924a()
    print(path)
