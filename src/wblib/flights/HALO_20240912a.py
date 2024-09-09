import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    bco,
    point_on_track,
    LatLon,
    IntoCircle,
    FlightPlan,
)


def _flight_HALO_20240912a():
    flight_time = pd.Timestamp(2024, 9, 12, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3 * 1.852

    # Load satellite tracks
    ec_fcst_time = "2024-09-08"
    ec_track = (
        orcestra.sat.SattrackLoader(
            "EARTHCARE", ec_fcst_time, kind="PRE", roi="BARBADOS"
        )
        .get_track_for_day(f"{flight_time:%Y-%m-%d}")
        .sel(time=slice(f"{flight_time:%Y-%m-%d} 14:00", None))
    )

    # Create elements of track
    ec_track5 = ec_track.assign(lon=lambda ds: ds.lon + 3.5)

    c_northeast  = point_on_track(ec_track5,lat= 12.00).assign(label = "c_northeast")
    c_southwest  = point_on_track(ec_track,lat= 10.50).assign(label = "c_southwest")
    c_southeast  = point_on_track(ec_track5,lat= 9.00).assign(label = "c_southeast")
    c_northwest  = point_on_track(ec_track,lat= 13.5).assign(label = "c_northwest")

    ec_north = point_on_track(ec_track,lat= 15.00).assign(label = "ec_north") 
    ec_south = point_on_track(ec_track,lat=  c_southwest.lat - 1.5).assign(label = "ec_south")
    ec_under = point_on_track(ec_track, lat= 12.00, with_time=True).assign(label = "ec_under", note = "meet EarthCARE")
    ec_under_north = point_on_track(ec_track, lat= 13.00).assign(label = "ec_under_n", note = "EC align north")
    ec_under_south = point_on_track(ec_track, lat= 11.00).assign(label = "ec_under_s", note = "EC align south")


    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        #c_southwest.assign(fl=410),
        IntoCircle(c_southeast.assign(fl=410), radius, 330, enter= 0),
        IntoCircle(c_northeast.assign(fl=430), radius, -360, enter = 180),
        IntoCircle(c_northwest.assign(fl=430), radius, -360, enter = 180),
        c_northwest.towards(c_southwest, distance = -radius).assign(fl = 450, label = "ec_north"), 
        ec_under_north.assign(fl=450),
        ec_under.assign(fl=450),
        ec_under_south.assign(fl=450),
        ec_south.assign(fl=450),  
        IntoCircle(c_southwest.assign(fl=450), radius, 360),   
        airport.assign(fl=0),
        ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240912a()
    print(path)
