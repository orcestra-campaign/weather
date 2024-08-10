from orcestra.flightplan import sal, bco, LatLon, IntoCircle
from datetime import datetime

def _flight_HALO_20240811a():
     flight_time = datetime(2024, 8, 11, 12, 0, 0)

     radius = 100e3
     airport = sal
     north = LatLon(lat=15.529, lon=-24.982, label='north')
     south = LatLon(lat=2.586, lon=-27.440, label='south')
     edge_south = LatLon(lat=5.0, lon=-26.996, label='circle_south')
     center = LatLon(lat=8.251, lon=-26.389, label='circle_center')
     edge_north = LatLon(lat=11.5, lon=-25.772, label='circle_north')
     mindelo = LatLon(lat=16.891, lon=-25.006, label='mindelo')

     leg_south = [
          airport,
          north,
          edge_north,
          center,
          edge_south,
          south
     ]

     leg_circles = [
          IntoCircle(edge_south, radius, 360),
          IntoCircle(center, radius, 360),
          IntoCircle(edge_north, radius, 360),
     ]
     
     leg_home = [
          north,
          mindelo,
          airport
     ]

     path = leg_south + leg_circles + leg_home
     return flight_time, path