import pandas as pd
from dataclasses import asdict
from datetime import datetime
import orcestra.sat
from orcestra.flightplan import bco, point_on_track, LatLon, IntoCircle, FlightPlan

def _flight_HALO_20240907a():
    flight_time = pd.Timestamp(2024, 9, 7, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3*1.852

    # Create elements of track
    c_south  = LatLon(lat=7.0, lon=-48.62143522516965, label='c_south', fl=None, time=None, note=None)
    c_mid    = LatLon(lat=10.25, lon=-48.00697796976242, label='c_mid', fl=None, time=None, note=None)
    c_north  = LatLon(lat=13.5, lon=-47.384013580246915, label='c_north', fl=None, time=None, note=None)

    c_wait   = c_south.towards(c_mid,distance=radius*0.75).assign(label = "c_wait")
    join     = c_south.towards(c_mid,distance=radius).assign(label = "join")
    c_out    = c_north.towards(c_mid,distance=radius).assign(label = "c_out")
    ec_north = LatLon(lat=15.0, lon=-47.09269777777778, label='ec_north', fl=None, time=None, note=None)
    xlat     = c_south.towards(c_mid,distance=-radius).lat
    ec_south = LatLon(lat=5.814799550641501, lon=-48.84389638285317, label='ec_south', fl=None, time=None, note=None)
    ec_mid   = ec_north.towards(ec_south).assign(label = "ec_mid")
    ec_turn  = ec_mid.towards(ec_south,fraction=2/3.).assign(label = "ec_turn")

    xlat     = c_mid.towards(c_north,fraction=1/6).lat
    ec_under = LatLon(lat=10.79180908120098, lon=-47.90378833317426, label='ec_under', fl=None, time=None)

    # Additional Waypoints
    extra_waypoints = []

    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        join.assign(fl=410),
        IntoCircle(c_wait.assign(fl=410), radius/4,  360),   
        IntoCircle(c_south.assign(fl=410), radius,360),   
        join.assign(fl=410),
        IntoCircle(c_mid.assign(fl=430), radius, -360,enter=-90), 
        c_mid.assign(fl=450),
        ec_under.assign(fl=450),
        c_out.assign(fl=450),
        IntoCircle(c_north.assign(fl=450), radius, -360), 
        airport.assign(fl=0),
    ]

    # Plan
    plan = FlightPlan(waypoints, None, extra_waypoints=extra_waypoints)

    return flight_time, plan.path

if __name__ == "__main__":
    time, path = _flight_HALO_20240907a()
    print(path)