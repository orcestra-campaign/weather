import pandas as pd
import numpy as np
import orcestra.sat
import orcestra.flightplan as fp
from orcestra.flightplan import sal, mindelo, LatLon, IntoCircle, find_ec_lon

def _flight_HALO_20240825a():
    flight_time = pd.Timestamp(2024, 8, 25, 12, 0, 0).tz_localize("UTC")
     
    # Load ec satellite track for 
    ec_track = orcestra.sat.SattrackLoader(
        "EARTHCARE", "2024-08-21", kind="PRE"
        ).get_track_for_day(f"{flight_time:%Y-%m-%d}")
    ec_track = ec_track.sel(time=slice(f"{flight_time:%Y-%m-%d} 06:00", None))
    ec_lons, ec_lats = ec_track.lon.values, ec_track.lat.values

    ## Setting lat/lon coordinates
    # Mass flux circle radius (m)
    radius = 130e3
    atr_radius = 70e3

    # Setting region (Cabo Verde vs. Barbados)
    airport = sal #bco

    # Latitudes where we enter and leave the ec track (visually estimated)
    lat_ec_north_out = 16.0
    lat_ec_north_in = 12.0
    lat_ec_south = 2.5

    # ITCZ edges visually estimated from iwv contours
    lat_c_south = 4.0
    lat_c_north = 10.0

    # Points where we get on ec track
    north_ec_in = LatLon(lat_ec_north_in, find_ec_lon(lat_ec_north_in, ec_lons, ec_lats), label = "north_ec_in")
    north_ec_out = LatLon(lat_ec_north_out, find_ec_lon(lat_ec_north_out, ec_lons, ec_lats), label = "north_ec_out")
    south_ec = LatLon(lat_ec_south, find_ec_lon(lat_ec_south, ec_lons, ec_lats), label = "south_ec")

    # Intersection of ITCZ edges with ec track
    c_north = LatLon(lat_c_north, find_ec_lon(lat_c_north, ec_lons, ec_lats), label = "c_north")
    c_south = LatLon(lat_c_south, find_ec_lon(lat_c_south, ec_lons, ec_lats), label = "c_south")

    # Center of middle circle
    c_mid = c_south.towards(c_north).assign(label = "c_mid")

    # EarthCARE underpass
    ec_under = c_north.towards(north_ec_out).assign(label = "ec_under")

    def ec_time_at_lat(ec_track, lat):
        e = np.datetime64("2024-08-01")
        s = np.timedelta64(1, "ns")
        return (((ec_track.swap_dims({"time":"lat"}).time - e) / s).interp(lat=lat) * s + e)

    # ATR circle
    atr_circ = LatLon(17.433, -23.5, label = "atr")

    # Define flight track, can be split into different legs
    waypoints = [
        airport.assign(time='2024-08-25T09:30:00Z'), 
        north_ec_in.assign(fl=400),
        c_north.assign(fl=400),
        c_mid.assign(fl=400),
        c_south.assign(fl=400),
        south_ec.assign(fl=430),
        IntoCircle(c_south.assign(fl=430), radius, 360),  
        IntoCircle(c_mid.assign(fl=430), radius, 360), 
        IntoCircle(c_north.assign(fl=450), radius, 360),
        ec_under.assign(fl=450),
        north_ec_out.assign(fl=450),
        mindelo.assign(fl=450),
        IntoCircle(atr_circ.assign(fl=350), atr_radius, 360),
        airport
    ] 

    path = fp.expand_path(waypoints, dx=10e3)
     
    return flight_time, path