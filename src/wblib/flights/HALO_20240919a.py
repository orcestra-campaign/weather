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


def _flight_HALO_20240919a():
    lon_min, lon_max, lat_min, lat_max = -65, -20, 0, 20

    flight_time = pd.Timestamp(2024, 9, 19, 10, 33, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3 * 1.852
    smaller_radius = 52e3 * 1.852

    meteor = LatLon(10.65, -49.5).assign(label="meteor")

    pace_start = LatLon(lat=11.35, lon=-52.3096666666667).assign(label="pace_start")
    pace_under = LatLon(lat=16.1473333333333, lon=-53.3588333333333).assign(label="pace_under", note="meet PACE")
    pace_end = LatLon(lat=16.7791666666667, lon=-53.4995).assign(label = "pace_end")

    ec_start = LatLon(lat=16.7541666666667, lon=-53.4368333333333).assign(label = "ec_start")
    ec_under = LatLon(lat=14.8143333333333, lon=-53.8171666666667).assign(label="ec_under", note="meet EarthCARE")
    ec_end = LatLon(lat=11.88, lon=-54.3841666666667).assign(label = "ec_end")

    circ_1 =  LatLon(lat=10.0371666666667, lon=-47.1971666666667).assign(label="c1")
    circ_2 = LatLon(lat=10.8586666666667, lon=-50.3371666666667).assign(label="c2")
    circ_3 = LatLon(lat=11.6478333333333, lon=-53.494).assign(label="c3")    
    circ_4 =  LatLon(lat=15.592, lon=-53.7126666666667).assign(label="c4")
    circ_5 =  LatLon(lat=12.4203333333333, lon=-56.664).assign(label="c5")
    p2 =  LatLon(lat=11.1585, lon=-51.519).assign(label="p2")

    fl1, fl2, fl3 = 410, 430, 450
    waypoints = [
        airport.assign(fl=0),
        meteor.assign(fl=fl1),
        IntoCircle(circ_1.assign(fl=fl2), radius,  angle=-360), # anti-clockwise (optional)
        meteor.assign(fl=fl2),
        p2.assign(fl=fl2),
        IntoCircle(circ_2.assign(fl=fl2), radius,  angle=-360), # anti-clockwise (optional)
        IntoCircle(circ_3.assign(fl=fl3), radius,  angle=-360), # ANTI-CLOCKWISE
        pace_start.assign(fl=fl3),
        pace_under.assign(fl=fl3),
        pace_end.assign(fl=fl3),
        IntoCircle(circ_4.assign(fl=fl3), radius,  angle=360), # CLOCKWISE
        ec_start.assign(fl=fl3),
        ec_under.assign(fl=fl3),
        ec_end.assign(fl=fl3),
        IntoCircle(circ_5.assign(fl=fl3), smaller_radius,  angle=-360), # anti-clockwise (optional)
        airport.assign(fl=0),
    ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240919a()
    print(path)
