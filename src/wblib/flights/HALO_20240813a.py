import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240813a():
     flight_time = pd.Timestamp(2024, 8, 13, 12, 0, 0).tz_localize("UTC")

     radius = 130e3
     radius_atr = 70e3

     airport = sal
     north_ec = LatLon(lat=17.475000, lon=-22.222900, label='north_ec')
     north_tp = LatLon(lat=21.350000, lon=-21.440600, label='north_tp')
     south_ec = LatLon(lat=5.000000, lon=-24.702000, label='south_ec')
     south_tp = LatLon(lat=5.000000, lon=-23.502000, label='south_tp')
     circle_north = LatLon(lat=16.000000, lon=-21.278500, label='circle_north')
     circle_center = LatLon(lat=11.751952, lon=-22.160695, label='circle_center')
     circle_south = LatLon(lat=7.500000, lon=-23.016200, label='circle_south')

     circle_atr = LatLon(lat=15.5, lon=-22.1, label='circle_atr')

     leg_south = [
          airport,
          north_ec,
          north_tp,
          north_ec,
          south_ec,
          south_tp
     ]

     leg_circles = [
          IntoCircle(circle_south, radius, 360),
          IntoCircle(circle_center, radius, 360),
          IntoCircle(circle_north, radius, 360, enter = 90),
          IntoCircle(circle_atr, radius_atr, 360)
     ]
     
     leg_home = [
          airport
     ]

     path = leg_south + leg_circles + leg_home
     
     return flight_time, path