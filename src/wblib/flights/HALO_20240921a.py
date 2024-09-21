import pandas as pd
from orcestra.flightplan import (
    tbpb,
    LatLon,
    IntoCircle,
    FlightPlan,
)
import datetime


def _flight_HALO_20240921a():
    flight_time = pd.Timestamp(2024, 9, 21, 11, 25, 0).tz_localize("UTC")

    airport = tbpb
    radius = 72e3 * 1.852

    # Create points for flight path
    ec_circ = LatLon(
        lat=10.0, lon=-51.993406666666665, label='ec_circ', fl=None, time=None,
        note=None
        )
    ec_under = LatLon(
        lat=11.0, lon=-51.80293317901234, label='ec_under', fl=None,
        time=datetime.datetime(
            2024, 9, 21, 17, 33, 39, 149691, tzinfo=datetime.timezone.utc),
        note='meet EarthCARE'
        )
    ec_south = LatLon(
        lat=8.8, lon=-52.220948703703705, label='ec_south', fl=None, time=None,
        note=None
        )
    ec_north = LatLon(
        lat=13.074722, lon=-51.404937365853655, label='ec_north', fl=None,
        time=None, note=None
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
