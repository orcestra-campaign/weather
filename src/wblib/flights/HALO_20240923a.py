import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    point_on_track,
    LatLon,
    IntoCircle,
    FlightPlan,
    tbpb,
)


def _flight_HALO_20240923a():
    flight_time = pd.Timestamp(2024, 9, 23, 12, 0, 0).tz_localize("UTC")
    radius = 72e3 * 1.852
    radius_meteor = 72e3
    bco = LatLon(13.16263889, -59.42875000, "BCO", fl=0)

    ec_fcst_time  = "2024-09-18"
    ec_track = (
        orcestra.sat.SattrackLoader(
            "EARTHCARE", ec_fcst_time, kind="PRE", roi="BARBADOS"
        )
        .get_track_for_day(f"{flight_time:%Y-%m-%d}")
        .sel(time=slice(f"{flight_time:%Y-%m-%d} 14:00", None))
    )

    meteor = LatLon(10.65, -49.5).assign(label="meteor")
    c_climb = bco.assign(
        lon=bco.lon + 0.5,
        label="c_climb",
        fl=150,
        note="circle to climb up to FL360 and start up all the instruments",
    )
    c_meteor = c_climb.course(90, 22e3).assign(label="c_meteor", fl=360)
    c_south = LatLon(lat=9.3, lon=-46).assign(label="c_south")
    c_ec = point_on_track(ec_track, lat=10).assign(label="c_ec")
    ec_north = point_on_track(ec_track, lat=12).assign(label="ec_north")
    ec_under = point_on_track(ec_track, lat=10.5, with_time=True).assign(
        label="ec_under", note="meet EarthCARE"
    )
    ec_south = point_on_track(ec_track, lat=9).assign(label="ec_south")

    waypoints = [
        tbpb,
        IntoCircle(c_climb, radius=50e3, angle=-305, enter=180),
        IntoCircle(c_meteor, radius=radius_meteor, angle=-360),
        IntoCircle(c_south.assign(fl=450), radius, 360),
        IntoCircle(
            tbpb.towards(c_south, fraction=0.75).assign(fl=450, label="c_ec"),
            radius,
            360,
            0,
        ),
        ec_south.assign(fl=450),
        ec_under.assign(fl=450),
        ec_north.assign(fl=450),
        point_on_track(ec_track, lat=10.3).assign(fl=450, label="wp_home"),
        IntoCircle(
            tbpb.towards(c_south, fraction=0.5).assign(fl=430, label="c_mid"),
            radius,
            360,
        ),
        IntoCircle(
            tbpb.towards(c_south, fraction=0.25).assign(
                fl=410, label="c_west"
            ),
            radius,
            360,
        ),
        c_climb,
        tbpb,
    ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240923a()
    print(path)
