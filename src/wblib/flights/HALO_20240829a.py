import pandas as pd
import numpy as np
import orcestra.sat
import orcestra.flightplan as fp
from orcestra.flightplan import sal, mindelo, LatLon, IntoCircle, find_ec_lon

def ec_time_at_lat(ec_track, lat):
    e = np.datetime64("2024-08-01")
    s = np.timedelta64(1, "ns")
    return (((ec_track.swap_dims({"time":"lat"}).time - e) / s).interp(lat=lat) * s + e)


def _flight_HALO_20240829a():
    flight_time = pd.Timestamp(2024, 8, 29, 12, 0, 0).tz_localize("UTC")

    radius = 130e3
    atr_radius = 72e3

    band = "east"
    airport = sal if band == "east" else bco

    # Load ec satellite track for 
    ec_track = orcestra.sat.SattrackLoader("EARTHCARE", "2024-08-26", kind="PRE").get_track_for_day(f"{flight_time:%Y-%m-%d}")
    ec_track = ec_track.sel(time=slice(f"{flight_time:%Y-%m-%d} 06:00", None))
    ec_lons, ec_lats = ec_track.lon.values, ec_track.lat.values

    # Latitudes where we enter and leave the ec track (visually estimated)
    lat_ec_north = 15.0
    lat_ec_south = 2.5

    # latitude of circle centers
    lat_c_south_s = 3.5
    lat_c_south = 4.5
    lat_c_south_n = 5.5
    lat_c_north = 13.0

    lat_c_mid_s = 7.5
    lat_c_mid = 8.5
    lat_c_mid_n = 9.5

    lat_ec_under = 5.0

    c_atr_nw = LatLon(18.58125000,-24.27616667, label = "c_atr")
    c_atr_se = LatLon(15.79318333,-24.82891944, label = "c_atr")

    # create ec track
    ec_north = LatLon(lat_ec_north, find_ec_lon(lat_ec_north, ec_lons, ec_lats), label = "ec_north")
    ec_south = LatLon(lat_ec_south, find_ec_lon(lat_ec_south, ec_lons, ec_lats), label = "ec_south")

    # create circles
    c_north = LatLon(lat_c_north, find_ec_lon(lat_c_north, ec_lons, ec_lats), label = "c_north")

    c_south = LatLon(lat_c_south, find_ec_lon(lat_c_south, ec_lons, ec_lats), label = "c_south")
    c_south_s = LatLon(lat_c_south_s, find_ec_lon(lat_c_south_s, ec_lons, ec_lats), label = "c_south_s")
    c_south_n = LatLon(lat_c_south_n, find_ec_lon(lat_c_south_n, ec_lons, ec_lats), label = "c_south_n")

    c_mid = LatLon(lat_c_mid, find_ec_lon(lat_c_mid, ec_lons, ec_lats), label = "c_mid")
    c_mid_s = LatLon(lat_c_mid_s, find_ec_lon(lat_c_mid_s, ec_lons, ec_lats), label = "c_mid_s")
    c_mid_n = LatLon(lat_c_mid_n, find_ec_lon(lat_c_mid_n, ec_lons, ec_lats), label = "c_mid_n")

    # ec underpass
    ec_under = LatLon(lat_ec_under, find_ec_lon(lat_ec_under, ec_lons, ec_lats), label = "ec_under")
    ec_under = ec_under.assign(time=str(ec_time_at_lat(ec_track, ec_under.lat).values)+"Z")

    # Define flight track
    outbound_legs = [
        airport,
        mindelo,
        ec_north.assign(fl=410),
        ]

    ec_legs = [
        IntoCircle(c_south.assign(fl=430), radius, 360),   
        ec_south.assign(fl=410),
        ec_under.assign(fl=450),
        IntoCircle(c_mid.assign(fl=430), radius, 360), 
        IntoCircle(c_north.assign(fl=450), radius, 360),   
        ]
    inbound_legs = [
        ec_north.assign(fl=450),
        IntoCircle(c_atr_nw.assign(fl=350), atr_radius, 360),
        IntoCircle(c_atr_se.assign(fl=350), atr_radius, 360),
        airport,
        ]

    waypoints = outbound_legs + ec_legs + inbound_legs 

    waypoint_centers = []
    for point in waypoints:
        if isinstance(point, IntoCircle):
            point = point.center
        waypoint_centers.append(point)

    path = fp.expand_path(waypoints, dx=10e3)

    return flight_time, path