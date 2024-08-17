import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240818a():
    flight_time = pd.Timestamp(2024, 8, 18, 12, 0, 0).tz_localize("UTC")
     
    radius = 130e3
    atr_radius = 70e3

    airport = sal
    north_ec = LatLon(lat=13.1, lon=-28.5167, label='north_ec') # good
    circle_north = LatLon(lat=13.1, lon=-28.5167, label='circle_north') # good
    circle_cloud = LatLon(lat=10.00, lon=-29.0667, label='circle_cloud') # good
    circle_center = LatLon(lat=8.05, lon=-29.4667, label='circle_center') # good
    circle_south = LatLon(lat=3.0, lon=-30.41667, label='circle_south') # good 
    south_ec = LatLon(lat=3.0, lon=-30.41667, label='south_ec') # good
    earthcare = LatLon(lat=8.05, lon=-29.4667, label='earthcare') # good
    atr = LatLon(lat=16.4212, lon=-21.8315, label='atr')

    leg_south = [
        airport,
        north_ec,
        south_ec
    ]

    leg_circles = [
        IntoCircle(circle_south, radius, 360),
        IntoCircle(circle_center, radius, 360),
        earthcare,
        IntoCircle(circle_cloud, radius*1.5, 360),
        IntoCircle(circle_north, radius, 360),
    ]
   
    leg_home = [
        north_ec,
        IntoCircle(atr, atr_radius, -360, enter = 180),
        airport
    ]

    path = leg_south + leg_circles + leg_home 
     
    return flight_time, path