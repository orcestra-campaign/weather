import pandas as pd
from dataclasses import asdict
from datetime import datetime
import orcestra.sat
from orcestra.flightplan import bco, point_on_track, LatLon, IntoCircle, FlightPlan

def _flight_HALO_20240907a():
    flight_time = pd.Timestamp(2024, 9, 7, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3*1.852

    # Load satellite tracks 
    ec_fcst_time  = "2024-08-19"
    ec_track = orcestra.sat.SattrackLoader(
        "EARTHCARE", ec_fcst_time, kind="LTP",roi="BARBADOS"
        ).get_track_for_day(f"{flight_time:%Y-%m-%d}").sel(
            time=slice(f"{flight_time:%Y-%m-%d} 14:00", None)
            )

    # Create elements of track
    ec_north = point_on_track(ec_track,lat= 15.00).assign(label = "ec_north") 
    ec_south = point_on_track(ec_track,lat=  5.00).assign(label = "ec_south")
    c_north  = point_on_track(ec_track,lat= 13.50).assign(label = "c_north")
    c_south  = point_on_track(ec_track,lat=  7.00).assign(label = "c_south")
    c_mid    = point_on_track(ec_track,lat= 10.25).assign(label = "c_south")
    ec_under = point_on_track(ec_track,lat=  7, with_time=True).assign(
        label = "ec_under", note = "meet EarthCARE")

    # Additional Waypoints
    extra_waypoints = []

    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        ec_north.assign(fl=410),
        IntoCircle(c_north.assign(fl=410), radius, -360),   
        IntoCircle(c_mid.assign(fl=430), radius, -360), 
        IntoCircle(c_south.assign(fl=450), radius, -360), 
        ec_under.assign(fl=450),
        ec_south.assign(fl=450),    
        airport.assign(fl=0),
        ]

    # Plan
    plan = FlightPlan(waypoints, None, extra_waypoints=extra_waypoints)

    return flight_time, plan.path

if __name__ == "__main__":
    time, path = _flight_HALO_20240907a()
    print(path)