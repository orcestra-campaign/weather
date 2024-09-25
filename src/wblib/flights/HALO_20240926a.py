import pandas as pd
import orcestra.sat
from orcestra.flightplan import (
    tbpb,
    LatLon,
    IntoCircle,
    FlightPlan,
    point_on_track
)
from orcestra.flightplan import tbpb
import datetime


def _flight_HALO_20240926a():
    flight_time = pd.Timestamp(2024, 9, 26, 12, 00, 0).tz_localize("UTC")

    radius = 72e3*1.852
    speed_halo = 240  # m/s

    # Load satellite track
    sat_fcst_date = "2024-09-24"
    ec_track = orcestra.sat.SattrackLoader(
        "EARTHCARE", sat_fcst_date, kind="PRE", roi="BARBADOS"
    ).get_track_for_day(f"{flight_time:%Y-%m-%d}")
    ec_track = ec_track.sel(time=slice(f"{flight_time:%Y-%m-%d} 07:00", None))

    # Circles
    lat_south = 10.5
    mid_south = point_on_track(ec_track, lat_south).assign(fl=450, label="c_south")

    lat_north = 16.5
    mid_north = point_on_track(ec_track, lat_north).assign(fl=450, label="c_north")

    mid_mid = mid_south.towards(mid_north, 0.5).assign(label="c_mid", fl=410)

    lat_neast = 14
    lon_neast = mid_mid.lon + 3.5
    mid_neast = LatLon(lat_neast, lon_neast, fl=430, label="c_northeast")

    lat_seast = 11
    lon_seast = mid_mid.lon + 2.3 + ((5 * 60 * speed_halo) / 110e3)
    mid_seast = LatLon(lat_seast, lon_seast, fl=450, label="c_southeast")

    # Ec points
    ec_south = point_on_track(ec_track, lat=mid_south.lat - 1.2).assign(
        label="ec_south", fl=450
    )
    ec_north = point_on_track(ec_track, lat=mid_north.lat + 1.2).assign(
        label="ec_north", fl=450
    )
    ec_under = point_on_track(
        ec_track, lat=(ec_north.lat + ec_south.lat) / 2, with_time=True
    ).assign(label="ec_under", fl=450, note="Meet EarthCARE")

    # Define Flight Paths
    waypoints = [
        tbpb,
        IntoCircle(mid_mid, radius=radius, enter=-90, angle=-360),
        IntoCircle(mid_neast, radius=radius, enter=-90, angle=-360),
        IntoCircle(mid_seast, radius=radius, enter=180, angle=-360),
        IntoCircle(mid_south, radius=radius, enter=0, angle=420),
        ec_south,
        ec_under,
        ec_north,
        IntoCircle(mid_north, radius=radius, angle=-420),
        tbpb,
    ]

    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240926a()
    print(path)
