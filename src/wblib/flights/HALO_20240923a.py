import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    LatLon,
    IntoCircle,
    FlightPlan,
    tbpb,
)
import datetime


def _flight_HALO_20240923a():
    flight_time = pd.Timestamp(2024, 9, 23, 12, 0, 0).tz_localize("UTC")
    radius = 72e3 * 1.852
    radius_meteor = 72e3
    bco = LatLon(13.16263889, -59.42875000, "BCO", fl=0)

    c_climb = bco.assign(lon=bco.lon+0.61, label="c_climb", fl=150, note="circle to climb up to FL360 and start up all the instruments")
    c_meteor = c_climb.course(90, 7e3).assign(label="c_meteor", fl=410)
    wp_meteor = LatLon(bco.lat, c_meteor.lon - 0.665)
    c_south  = LatLon(lat=10.5, lon=-46).assign(label = "c_south", fl=450)
    ec_north = LatLon(lat=12.9, lon=-48.64658626119172, label='ec_north', fl=None, time=None, note=None)
    ec_under = LatLon(lat=11.025, lon=-49.006238333333336, label='ec_under', fl=None, time=datetime.datetime(2024, 9, 23, 17, 22, 26, 569444, tzinfo=datetime.timezone.utc), note='meet EarthCARE')
    ec_south = LatLon(lat=9.15, lon=-49.362835802469135, label='ec_south', fl=None, time=None, note=None)

    waypoints = [
        tbpb,
        wp_meteor.assign(fl=150, label="wp_meteor"),
        IntoCircle(c_climb, radius=65e3, angle=360),
        IntoCircle(c_meteor, radius=radius_meteor, angle=360),
        IntoCircle(tbpb.towards(c_south, fraction=.5).assign(fl=430, label="c_mid"), radius, -360),
        IntoCircle(tbpb.towards(c_south, fraction=.75).assign(fl=450, label="c_ec"), radius, -360),
        IntoCircle(c_south.assign(fl=450), radius, -360),
        ec_south.assign(fl=450),
        ec_under.assign(fl=450),
        ec_north.assign(fl=450),
        LatLon(lat=11.1, lon=-48.99191877122569, label='wp_home', fl=450, time=None, note=None),
        IntoCircle(tbpb.towards(c_south, fraction=.25).assign(fl=450, label="c_west"), radius, -360),
        wp_meteor.assign(fl=150, label="wp_meteor"),
        tbpb,
        ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240923a()
    print(path)