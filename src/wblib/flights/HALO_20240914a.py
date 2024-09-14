import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    bco,
    LatLon,
    IntoCircle,
    FlightPlan,
)
import datetime


def _flight_HALO_20240914a():
    flight_time = pd.Timestamp(2024, 9, 14, 12, 0, 0).tz_localize("UTC")

    airport = bco
    radius = 72e3 * 1.852

    # Create elements of track
    ec_south = LatLon(lat=5.0, lon=-50.81198296296296, label='ec_south',
                      fl=None, time=None, note=None)

    # circle centers
    c_south = LatLon(lat=6.75, lon=-50.48396944444445, label='c_south', fl=None,
                     time=None, note=None)
    c_mid = LatLon(lat=9.7, lon=-49.92710774930534, label='c_mid', fl=None,
                   time=None, note=None)
    c_south2 = c_south.towards(c_mid, distance=radius).assign(label="c_south2")
    c_north = LatLon(lat=12.75, lon=-49.344415683853036, label='c_north',
                     fl=None, time=None, note=None)
    # circle in / out (not necessary but nice to have for more waypoints
    cn_out = c_north.towards(c_mid, distance=radius).assign(label="cn_out")
    cm_out = c_mid.towards(c_south, distance=radius).assign(label="cm_out")
    cs2_out = c_south2.towards(c_south, distance=radius).assign(
        label="cs2_out"
    )
    cs_out = c_south.towards(c_mid, distance=radius).assign(label="cs_out")
    # earthcare end points
    ec_north = c_north.towards(c_mid, distance=radius).assign(label="ec_north")

    c_wait = c_south.towards(c_mid, distance=radius * 0.5).assign(
        label="c_wait"
    )
    cw_out = c_south.towards(c_mid, distance=radius * 0.9).assign(
        label="cw_out"
    )

    dir_opt = LatLon(lon=-54.7366666666667, lat=9.23666666666667).assign(
        label="wp1"
    )  # LatLon(lat=7 , lon= -54)
    add_wp = LatLon(lon=-54, lat=8.6183).assign(
        label="wp2"
    )  # dir_opt.towards(c_south, fraction=0.6)

    # intersection
    int_ss1, int_ss2 = IntoCircle(c_south, radius, 360).get_intersect(
        IntoCircle(c_south2, radius, 360)
    )
    int_sm1, int_sm2 = IntoCircle(c_south2, radius, 360).get_intersect(
        IntoCircle(c_mid, radius, 360)
    )

    xlat = c_mid.towards(cn_out, fraction=1 / 6).lat
    ec_under = LatLon(lat=10.010980712117739, lon=-49.868062926338105,
                      label='ec_under', fl=None,
                      time=datetime.datetime(2024, 9, 14, 17, 25, 35, 407705,
                                             tzinfo=datetime.timezone.utc),
                                             note='meet EarthCARE')

    # Additional Waypoints

    extra_waypoints = []

    # Define Flight Paths

    waypoints = [
        airport.assign(fl=0),
        # ec_south.assign(fl=410),
        dir_opt.assign(fl=410),
        add_wp.assign(fl=410),
        int_ss2.assign(fl=410, label="scs2_inter"),
        IntoCircle(c_south.assign(fl=410), radius, angle=-360),
        cw_out.assign(fl=430),
        IntoCircle(c_wait.assign(fl=430), radius * 0.4, angle=360),
        int_ss1.assign(fl=430, label="scs1_inter"),
        IntoCircle(c_south2.assign(fl=430, label="c_south2"), radius, 360),
        int_sm1.assign(fl=450, label="scm_inter"),
        IntoCircle(c_mid.assign(fl=450), radius, 360),
        cm_out.assign(fl=450),
        ec_under.assign(fl=450),
        IntoCircle(c_north.assign(fl=450), radius, angle=360),
        cn_out.assign(fl=450),
        airport.assign(fl=0),
    ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240914a()
    print(path)
