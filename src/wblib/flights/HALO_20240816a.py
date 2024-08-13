import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240816a():
     flight_time = pd.Timestamp(2024, 8, 16, 12, 0, 0).tz_localize("UTC")
     
     radius = 130e3
     atr_radius = 70e3

     airport = sal
     north_ec = LatLon(lat=15.500000, lon=-30.502500, label='north_ec')
     circle_north = LatLon(lat=12.700000, lon=-31.005200, label='circle_north')
     circle_center = LatLon(lat=8.851118, lon=-31.749216, label='circle_center')
     circle_south = LatLon(lat=5.000000, lon=-32.477900, label='circle_south')
     south_ec = LatLon(lat=3.500000, lon=-32.720100, label='south_ec')
     earthcare = LatLon(lat=10.775902, lon=-31.379572, label='earthcare')
     atr = LatLon(lat=17.800000, lon=-23.600000, label='atr')

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