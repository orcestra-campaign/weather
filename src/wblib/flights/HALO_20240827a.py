import pandas as pd
import numpy as np
import orcestra.sat
import orcestra.flightplan as fp
from orcestra.flightplan import sal, mindelo, LatLon, IntoCircle, find_ec_lon

def ec_time_at_lat(ec_track, lat):
    e = np.datetime64("2024-08-01")
    s = np.timedelta64(1, "ns")
    return (((ec_track.swap_dims({"time":"lat"}).time - e) / s).interp(lat=lat) * s + e)


def _flight_HALO_20240827a():
    flight_time = pd.Timestamp(2024, 8, 27, 12, 0, 0).tz_localize("UTC")
     
    # Load ec satellite track for 
    ec_track = orcestra.sat.SattrackLoader(
        "EARTHCARE", "2024-08-24", kind="PRE"
        ).get_track_for_day(f"{flight_time:%Y-%m-%d}")
    ec_track = ec_track.sel(time=slice(f"{flight_time:%Y-%m-%d} 06:00", None))
    ec_lons, ec_lats = ec_track.lon.values, ec_track.lat.values

    ## Setting lat/lon coordinates
    # Mass flux circle radius (m)
    radius = 130e3
    atr_radius = 72e3

    band = "east"
    airport = sal if band == "east" else bco

    # Basic information
    lon_min, lon_max, lat_min, lat_max = -65, -5, -5, 25

    # Define dates for forecast initialization and flight

    flight_index = f"HALO-{flight_time.strftime('%Y%m%d')}a"

    # Load ec satellite track for 
    ec_track = orcestra.sat.SattrackLoader("EARTHCARE", "2024-08-24", kind="PRE").get_track_for_day(f"{flight_time:%Y-%m-%d}")
    ec_track = ec_track.sel(time=slice(f"{flight_time:%Y-%m-%d} 06:00", None))
    ec_lons, ec_lats = ec_track.lon.values, ec_track.lat.values

# Latitudes where we enter and leave the ec track (visually estimated)
    lat_ec_north = 14.5
    lat_ec_south = 5.75

# latitude of circle centers
    lat_c_south = 4.0
    lat_c_north = 11.5

    c_atr_nw = LatLon(17.433,-23.500, label = "c_atr")
    c_atr_se = LatLon(16.080,-21.715, label = "c_atr")

# create ec track
    ec_north = LatLon(lat_ec_north, find_ec_lon(lat_ec_north, ec_lons, ec_lats), label = "ec_north")
    ec_south = LatLon(lat_ec_south, find_ec_lon(lat_ec_south, ec_lons, ec_lats), label = "ec_south")

# create circles
    c_north = LatLon(lat_c_north, find_ec_lon(lat_c_north, ec_lons, ec_lats), label = "c_north")
    c_south = LatLon(lat_c_south, find_ec_lon(lat_c_south, ec_lons, ec_lats), label = "c_south")
    c_mid = c_south.towards(c_north).assign(label = "c_mid")

# extra way point on track
    x_wp1  = c_mid.towards(c_north,fraction=2/5.).assign(label = "x_wp1")

# ec underpass
    ec_under = c_north.towards(ec_north,fraction=1./2.).assign(label = "ec_under")
    ec_under.assign(time=str(ec_time_at_lat(ec_track, ec_under.lat).values)+"Z")

# Define flight track
    outbound_legs = [
     airport, 
     ec_north.assign(fl=410),
     ]

    ec_legs = [
     ec_south.assign(fl=410),
     IntoCircle(c_south.assign(fl=430), radius, -330,enter=220),   
     ec_south.assign(fl=430),
     IntoCircle(c_mid.assign(fl=430), radius, 360), 
     x_wp1.assign(fl=450),
     IntoCircle(c_north.assign(fl=450), radius, 360),   
     ec_under.assign(fl=450),
     ]

    inbound_legs = [
     ec_north.assign(fl=450),
     IntoCircle(c_atr_se.assign(fl=350), atr_radius, 330),
     airport,
     ]

    waypoints = outbound_legs + ec_legs + inbound_legs 

    path = fp.expand_path(waypoints, dx=10e3)
     
    return flight_time, path