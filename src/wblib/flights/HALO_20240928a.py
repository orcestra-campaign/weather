import numpy as np
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

def find_intersect(ab: tuple[LatLon, LatLon], cd: tuple[LatLon, LatLon], res=1000):
  import pyproj
  import numpy as np

  geod = pyproj.Geod(ellps="WGS84")
  
  def points_on_line(a, b, num_points):
    lons = np.linspace(a.lon, b.lon, num_points)
    lats = np.linspace(a.lat, b.lat, num_points)
    return lons, lats

  a, b = ab
  c, d = cd
      
  ab_dist = geod.inv(a.lon, a.lat, b.lon, b.lat)[2]
  cd_dist = geod.inv(c.lon, c.lat, d.lon, d.lat)[2]
  n = int(ab_dist // res)
  m = int(cd_dist // res)

  lons1, lats1  = points_on_line(ab[0], ab[1], n)
  ab_points = np.asarray(list(zip(lons1, lats1)))
  lons2, lats2 = points_on_line(cd[0], cd[1], m)
  cd_points = np.asarray(list(zip(lons2, lats2)))

  dist = []
  for lon, lat in zip(lons1, lats1):
    lon = np.full(len(lons2), lon)
    lat = np.full(len(lats2), lat)
    dist.append(geod.inv(lon, lat, lons2, lats2)[2])
  dist = np.asarray(dist)

  idx = np.argwhere(dist == np.nanmin(dist))[0]
  assert len(idx) == 2 and "one and only one minimum distance must be found"
  lon = np.mean([lons1[idx[0]], lons2[idx[1]]])
  lat = np.mean([lats1[idx[0]], lats2[idx[1]]])

  return LatLon(lon = lon, lat = lat)

def _flight_HALO_20240928a():
    flight_time = pd.Timestamp(2024, 9, 28, 12, 30, 0).tz_localize("UTC")

    sat_fcst_date = "2024-09-24"  # date to get satelite forecast(s) from
    ifs_fcst_time = "2024-09-24"  # date to get IFS forecast(s) from
    ifs_fcst_time = np.datetime64(ifs_fcst_time + "T12:00:00")

    ec_track_full = orcestra.sat.SattrackLoader(
        "EARTHCARE", sat_fcst_date, kind="PRE", roi="BARBADOS"
    ).get_track_for_day(f"{flight_time:%Y-%m-%d}")

    ec_track = ec_track_full.where(
        (ec_track_full.lat>-10)&
        (ec_track_full.lat<25)&
        (ec_track_full.lon>-60)&
        (ec_track_full.lon<-35), 
        drop = True).sel(time = slice(
        f"{flight_time:%Y-%m-%d} 10:00", f"{flight_time:%Y-%m-%d} 22:00"))

    ec_lons, ec_lats = ec_track.lon.values, ec_track.lat.values

    radius = 72e3 * 1.852 # Mass flux circle radius (m)
    radius_small = 39e3 * 1.852 # Mass flux circle radius ATR sized (m)
    speed_halo = 240  # m/s

    # EC Track

    ref_east = LatLon(lat = 10, lon = -44.1, label = "reference value")
    ec_south = point_on_track(ec_track, lat=11.0)
    ec_north = point_on_track(ec_track, lat=13.0)

    ec_start = find_intersect((tbpb, ref_east), (ec_south, ec_north)).assign(label = "ec_start")
    ec_under = point_on_track(ec_track, lat=float(ec_start.lat - 1.5), with_time = True).assign(label = "ec_under", note = "meet EarthCARE")#, time = "2024-09-28T17:42Z")
    ec_end = point_on_track(ec_track, lat=ec_start.lat - 3.5).assign(label = "ec_end")

    # Circles

    circle_west = ec_start.towards(tbpb, distance=radius).assign(label="west")

    fac_rad = 2.80
    circle_mid_west = circle_west.towards(ref_east, distance=radius*fac_rad).assign(label="mid_west")
    circle_mid_east = circle_west.towards(ref_east, distance=radius*fac_rad*2.0).assign(label="mid_east")
    circle_east = circle_west.towards(ref_east, distance=radius*fac_rad*3.0).assign(label="east")
    circ_last = ec_end.towards(tbpb, fraction= 0.5).assign(label = "circ_last")

    # Create plan 

    fl1 = 430
    fl2 = 450

    waypoints = [
        tbpb,
        IntoCircle(circle_east.assign(fl = fl1), radius = radius, angle = 360),
        IntoCircle(circle_mid_east.assign(fl = fl1), radius = radius, angle = 360, enter = -90),
        IntoCircle(circle_mid_west.assign(fl = fl2), radius = radius, angle = 360, enter = 90),
        IntoCircle(circle_west.assign(fl = fl2), radius = radius, angle = 360, enter = -90),
        ec_start.assign(fl = fl2),
        ec_under.assign(fl = fl2),
        ec_end.assign(fl = fl2),
        IntoCircle(circ_last.assign(fl = fl2), radius = radius_small, angle = 360),
        tbpb,
    ]
    # Plan
    plan = FlightPlan(waypoints, None)
    return flight_time, plan.path


if __name__ == "__main__":
    time, path = _flight_HALO_20240928a()
    print(path)
