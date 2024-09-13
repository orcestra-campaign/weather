import pandas as pd
from orcestra.flightplan import bco, LatLon, IntoCircle, FlightPlan
import datetime

def _flight_HALO_20240909a():
    flight_time = pd.Timestamp(2024, 9, 9, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3*1.852

    # Create elements of track
    c_north  = LatLon(lat=15.0, lon=-44.24395851851852, label = "c_north")
    c_south  = LatLon(lat=8.5, lon=-45.48992641160136, label = "c_south")
    c_mid    = LatLon(lat=11.75, lon=-44.871927337241594, label = "c_mid")

    ec_north = LatLon(lat=17.5, lon=-43.75211522544781, label = "ec_north") 
    ec_south = LatLon(lat=7.3, lon=-45.71616446637878, label = "ec_south")
    ec_under = LatLon(lat=15.5, lon=-44.146243902439025, label = "ec_under",
                      time=datetime.datetime(2024, 9, 9, 17, 5, 37, 536585,
                                             tzinfo=datetime.timezone.utc
                                             ), note = "meet EarthCARE")

    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        ec_south.assign(fl=410),   
        IntoCircle(c_south.assign(fl=410), radius, -360), 
        IntoCircle(c_mid.assign(fl=430), radius, -360), 
        LatLon(lat=10.565505734378226, lon=-45.098114884686694,
               label='fl_change', fl=450, time=None, note=None),
        c_mid.assign(fl=450),
        ec_under.assign(fl=450),
        ec_north.assign(fl=450),
        IntoCircle(c_north.assign(fl=450), radius, -360),   
        airport.assign(fl=0),
        ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240909a()
    print(path)