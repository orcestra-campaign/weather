import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    bco,
    point_on_track,
    LatLon,
    IntoCircle,
    FlightPlan,
)


def _flight_HALO_20240916a():
    lon_min, lon_max, lat_min, lat_max = -65, -20, 0, 20
    
    flight_time = pd.Timestamp(2024, 9, 16, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3 * 1.852

    # Load satellite tracks
    ec_fcst_time  = "2024-09-14"
    ec_track = orcestra.sat.SattrackLoader("EARTHCARE", ec_fcst_time, kind="PRE",roi="BARBADOS") \
        .get_track_for_day(f"{flight_time:%Y-%m-%d}")\
        .sel(time=slice(f"{flight_time:%Y-%m-%d} 14:00", None))

    # Use PACE_loader once only
    #pace_track = orcestra.sat.pace_track_loader() \
    #    .get_track_for_day(f"{flight_time:%Y-%m-%d}")

    #pace_track = pace_track.where(
    #    (pace_track.lat >lat_min)&
    #    (pace_track.lat <lat_max)&
    #    (pace_track.lon >-60)&
    #    (pace_track.lon <-30), 
    #    drop = True) \
    #    .sel(time=slice(f"{flight_time:%Y-%m-%d} 11:00", f"{flight_time:%Y-%m-%d} 21:00"))

    # Create elements of track
    c_north  = point_on_track(ec_track,lat= 11.5).assign(label = "c_north")
    c_south  = LatLon(lat= 7, lon= -50).assign(label = "c_south")
    c_mid    = point_on_track(ec_track,lat= 8.7).assign(label = "c_mid")

    ec_north = point_on_track(ec_track, lat=  9).assign(label = "ec_north") 
    ec_south = point_on_track(ec_track, lat=  3.0).assign(label = "ec_south")
    ec_under = point_on_track(ec_track, lat=  5.5, with_time=True).assign(label = "ec_under", note = "meet EarthCARE")

    pace_north = LatLon(lat=8, lon=-50.364828373907265, label='pace_north',
                        fl=None, time=None, note=None)
    pace_under = LatLon(lat=5.5, lon=-49.834834624942985, label='pace_under',
                        fl=None, time=None, note=None)
    pace_south = LatLon(lat=3.0, lon=-49.30790160443203, label='pace_south',
                        fl=None, time=None, note=None)

    c_south_entry = LatLon(lat=8.1, lon=-50.38612627013003,
                           label='c_south_entry', fl=None, time=None, note=None)
    c_north_home  = point_on_track(ec_track, lat= c_north.lat - 1.25).assign(label = "c_north_home")

    #c_wait4EC    = LatLon(lat=3.75, lon=-49.46574773190844, label='c_wait4EC', fl=None, time=None, note=None)
    c_wait4EC    = LatLon(lat=3.0, lon=-49.30790160443203, label='c_wait4EC', fl=None, time=None, note=None)

    #point_atlantic  = LatLon(lat= ec_south.lat, lon= -47).assign(label = "c_south")

    waypoints = [
        #airport.assign(fl=0, time = ""),
        airport.assign(fl=0),
        IntoCircle(c_mid.assign(fl=410), radius, -360),
        
        c_south_entry.assign(fl=410),
        IntoCircle(c_south.assign(fl=410), radius, -360), 
        pace_north.assign(fl=450),
        pace_under.assign(fl=450),

        #point_atlantic.assign(fl=450),
        

        IntoCircle(c_wait4EC.assign(fl=450), radius=36e3, angle=280), 
        pace_south.assign(fl=450),
        ec_south.assign(fl=450),
        ec_under.assign(fl=450),
        ec_north.assign(fl=450),
        
        IntoCircle(c_north.assign(fl=450), radius, 360),     
        c_north_home.assign(fl=450),
        airport.assign(fl=0),
        ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240916a()
    print(path)
