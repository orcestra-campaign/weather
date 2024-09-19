import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    bco,
    point_on_track,
    LatLon,
    IntoCircle,
    FlightPlan,
)
from orcestra.flightplan import tbpb


def _flight_HALO_20240921a():
    lon_min, lon_max, lat_min, lat_max = -65, -20, 0, 20

    flight_time = pd.Timestamp(2024, 9, 21, 11, 25, 0).tz_localize("UTC")

    airport = tbpb
    radius = 72e3 * 1.852
    sat_fcst_date = "2024-09-18"  # date to get satelite forecast(s) from
    ec_time_slice = slice(
        f"{flight_time:%Y-%m-%d} 17:30", f"{flight_time:%Y-%m-%d} 17:40"
    )
    
    ec_track = (
        orcestra.sat.SattrackLoader(
            "EARTHCARE", sat_fcst_date, kind="PRE", roi="BARBADOS"
        )
        .get_track_for_day(f"{flight_time:%Y-%m-%d}")
        .sel(time=ec_time_slice)
    )

    # Create points for flight path
    ec_circ = point_on_track(ec_track, lat=10.00).assign(label="ec_circ")
    ec_under = point_on_track(ec_track, lat=11.00, with_time=True).assign(
        label="ec_under", note="meet EarthCARE"
    )
    ec_south = point_on_track(ec_track, lat=ec_circ.lat - 1.2).assign(
        label="ec_south"
    )
    ec_north = point_on_track(ec_track, lat=airport.lat).assign(
        label="ec_north"
    )

    meteor = LatLon(11.7, -56).assign(label="meteor")
    west = meteor.towards(ec_circ, fraction=2.0).assign(
        label="west", note="circle two times"
    )  # LatLon(lat = 7.50, lon = -48.00).assign(label = "west")

    # Define Waypoints
    fl1, fl2, fl3 = 410, 430, 450
    waypoints = [
        airport.assign(fl=0),
        # meteor.assign(fl=fl2),
        IntoCircle(meteor.assign(fl=fl2), radius, -360),
        IntoCircle(west.assign(fl=fl2), radius, -360 * 2),
        ec_south.assign(fl=fl3),
        IntoCircle(ec_circ.assign(fl=fl3), radius, 360),
        ec_south.assign(fl=fl3),
        ec_under.assign(fl=fl3),
        ec_north.assign(fl=fl3),
        IntoCircle(meteor.assign(fl=fl3), radius, -360, enter=180),
        airport.assign(fl=0),
    ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240921a()
    print(path)
