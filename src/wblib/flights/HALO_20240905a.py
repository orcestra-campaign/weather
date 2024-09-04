import pandas as pd
import numpy as np
import orcestra.sat
import orcestra.flightplan as fp
from orcestra.flightplan import sal, bco, LatLon, IntoCircle, find_ec_lon

def ec_time_at_lat(ec_track, lat):
    e = np.datetime64("2024-08-01")
    s = np.timedelta64(1, "ns")
    return (((ec_track.swap_dims({"time":"lat"}).time - e) / s).interp(lat=lat) * s + e)


def _flight_HALO_20240905a():
    flight_time = pd.Timestamp(2024, 9, 5, 12, 0, 0).tz_localize("UTC")

    radius = 130e3

    # Load ec satellite track for 
    ec_track = orcestra.sat.SattrackLoader(
        "EARTHCARE", "2024-09-02", kind="PRE", roi="BARBADOS"
        ).get_track_for_day(f"{flight_time:%Y-%m-%d}")
    ec_track = ec_track.sel(time=slice(f"{flight_time:%Y-%m-%d} 06:00", None))
    ec_lons, ec_lats = ec_track.lon.values, ec_track.lat.values

    # Latitudes where we enter, underfly, and leave the ec track (visually estimated)
    lat_ec_north = bco.lat
    lat_ec_under = 10.0
    lat_ec_south = 9.0

    # create ec track
    ec_north = LatLon(lat_ec_north, find_ec_lon(lat_ec_north, ec_lons, ec_lats), label = "ec_north")
    ec_south = LatLon(lat_ec_south, find_ec_lon(lat_ec_south, ec_lons, ec_lats), label = "ec_south")

    # ec underpass
    ec_under = LatLon(lat_ec_under, find_ec_lon(lat_ec_under, ec_lons, ec_lats), label = "ec_under")
    ec_under = ec_under.assign(time=str(ec_time_at_lat(ec_track, ec_under.lat).values)+"Z")

    # create circles
    lat_circ = lat_ec_south
    c_track_on = LatLon(lat_circ, -32.0, label = "c_track_on")
    c_east = LatLon(lat_circ, -35.0, label = "c_east")
    c_center = LatLon(lat_circ, -40.0, label = "c_center")
    lat_c_west = 12.0
    c_west = LatLon(lat_c_west, find_ec_lon(lat_c_west, ec_lons, ec_lats), label = "c_west")

    # extra waypoints
    lat_circ_alt = lat_ec_south - 1.0
    meteor = LatLon(lat_circ_alt, -35.0, label = "meteor")
    c_center_s = LatLon(lat_circ_alt, -40.0, label = "c_center_s")

    # Define flight track
    outbound_legs = [
        sal,
        c_track_on.assign(fl=410)
        ]

    circle_legs = [
        IntoCircle(c_east.assign(fl=430), radius, 360),
        IntoCircle(c_center.assign(fl=430), radius, 360),
        ]

    ec_legs = [
        ec_south.assign(fl=450),
        ec_under.assign(fl=450),
        IntoCircle(c_west.assign(fl=450), radius, -360, enter = 90),
    ]

    inbound_legs = [
        bco,
        ]

    waypoints = outbound_legs + circle_legs + ec_legs + inbound_legs 

    waypoint_centers = []
    for point in waypoints:
        if isinstance(point, IntoCircle):
            point = point.center
        waypoint_centers.append(point)

    path = fp.expand_path(waypoints, dx=10e3)

    return flight_time, path