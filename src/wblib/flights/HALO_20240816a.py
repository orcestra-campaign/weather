import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240816a():
     flight_time = pd.Timestamp(2024, 8, 16, 12, 0, 0).tz_localize("UTC")
     
     radius = 130e3
     atr_radius = 70e3

     airport = sal
     north_ec = LatLon(lat=12.2994, lon=-31.1748, label='north_ec')
     circle_north = LatLon(lat=11.0045, lon=-31.4247, label='circle_north')
     circle_center = LatLon(lat=7.119, lon=-32.1586, label='circle_center')
     circle_south = LatLon(lat=3.2327, lon=-32.8863, label='circle_south')
     south_ec = LatLon(lat=1.5, lon=-33.2358, label='south_ec')
     earthcare = LatLon(lat=8.4143, lon=-31.9163, label='earthcare')
     atr = LatLon(lat=17.43333, lon=-23.500000, label='atr')

     leg_south = [
          airport,
          north_ec,
          south_ec
     ]

     leg_circles = [
          IntoCircle(circle_south, radius, 360),
          IntoCircle(circle_center, radius, 360),
          earthcare,
          IntoCircle(circle_north, radius, 360),
     ]
     
     leg_home = [
          north_ec,
          IntoCircle(atr, atr_radius, -360, enter = 180),
          airport
     ]

     path = leg_south + leg_circles + leg_home
     
     return flight_time, path