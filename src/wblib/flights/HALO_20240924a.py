import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    tbpb,
    point_on_track,
    LatLon,
    IntoCircle,
    FlightPlan,
)
from orcestra.flightplan import tbpb
import datetime


def _flight_HALO_20240924a():
    lon_min, lon_max, lat_min, lat_max = -65, -20, 0, 20

    flight_time = pd.Timestamp(2024, 9, 24, 12, 00, 0).tz_localize("UTC")

    airport = tbpb
    radius = 72e3*1.852

    # Load satellite tracks
    ec_fcst_time  = "2024-09-19"
    ec_track = orcestra.sat.SattrackLoader("EARTHCARE", ec_fcst_time, kind="PRE",roi="BARBADOS") \
        .get_track_for_day(f"{flight_time:%Y-%m-%d}")\
        .sel(time=slice(f"{flight_time:%Y-%m-%d} 14:00", None))

    # Use PACE_loader once only
    #pace_track = orcestra.sat.pace_track_loader() \
    #    .get_track_for_day(f"{flight_time:%Y-%m-%d}")
    #
    #pace_track = pace_track.where(
    #    (pace_track.lat >lat_min)&
    #    (pace_track.lat <lat_max)&
    #    (pace_track.lon >-60)&
    #    (pace_track.lon <-30), 
    #    drop = True) \
    #    .sel(time=slice(f"{flight_time:%Y-%m-%d} 11:00", f"{flight_time:%Y-%m-%d} 21:00"))

    # Create elements of track
    c_west_in = LatLon(11.8,-56.0).assign(label = "c_west_in")
    c_east_out = LatLon(10,-50).assign(label = "c_east_out")

    c_west = c_west_in.towards(c_east_out, distance = radius).assign(label = "c_west")
    c_east = c_west.towards(c_east_out, distance = 2*radius+radius).assign(label = "c_east")

    ec_north = point_on_track(ec_track,lat= 16.50).assign(label = "ec_north") 
    ec_south = point_on_track(ec_track,lat=  12.50).assign(label = "ec_south")
    ec_under = point_on_track(ec_track, lat= 14.50, with_time=True).assign(label = "ec_under", note = "meet EarthCARE")

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
