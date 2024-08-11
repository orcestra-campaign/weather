import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240813a():
     flight_time = pd.Timestamp(2024, 8, 13, 12, 0, 0).tz_localize("UTC")

     radius = 100e3
     airport = sal
     north = LatLon(lat=17.475, lon=-22.223, label='north')
     far_north = LatLon(lat=21.354, lon=-21.441, label='far_north')
     circle_north = LatLon(lat=14.000, lon=-22.910, label='circle_north')
     circle_mid = LatLon(lat=11.250, lon=-23.480, label='circle_mid')
     circle_south = LatLon(lat=8.500, lon=-23.970, label='circle_south')
     south = LatLon(lat=2.000, lon=-25.174, label='south')
     return_sal = LatLon(lat=14.888, lon=-22.712, label='return_sal')

     leg_south = [
          airport,
          north,
          far_north,
          north,
          circle_north,
          circle_mid,
          circle_south,
          south
     ]

     leg_circles = [
          IntoCircle(circle_south, radius, 360),
          IntoCircle(circle_mid, radius, 360),
          IntoCircle(circle_north, radius, 360),
     ]
     
     leg_home = [
          return_sal,
          airport
     ]

     path = leg_south + leg_circles + leg_home
     
     return flight_time, path