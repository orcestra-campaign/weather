import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240821a():
    flight_time = pd.Timestamp(2024, 8, 21, 12, 0, 0).tz_localize("UTC")
     
    radius = 130e3
    atr_radius = 70e3

    airport=sal
    north_tp = LatLon(lat=15., lon=-26.71,label= "north_tp")
    enter_atr1 = LatLon(lat=16.9, lon=-23.1, label='enter_atr1')
    enter_atr2 = LatLon(lat=15.2, lon=-22.7, label='enter_atr2')
    south_tp = LatLon(lat=2., lon=-26.71,label= "south_tp")

    circle_north = LatLon(13.,-26.71, "circle_north")
    circle_south = LatLon(5.9, -26.71, "circle_south")
    circle_center=LatLon(10.6,-26.71,"circle_center1")
    circle_center2=LatLon(8.2,-26.71,"circle_center2")
    circle_atr = LatLon(15.5,-22.15,'circle_atr1')
    circle_atr2 = LatLon(17.43,-23.5,'circle_atr2')

    leg_south = [
        airport, 
        enter_atr1,
        IntoCircle(circle_atr2, atr_radius, 360),
        north_tp,
        south_tp
    ]

    leg_circles = [
        IntoCircle(circle_north, radius, 360),
            IntoCircle(circle_center, radius, 360),
        IntoCircle(circle_center2, radius, 360),
        IntoCircle(circle_south, radius, 360),
    ]

    leg_home = [
     north_tp,
     enter_atr2,
     IntoCircle(circle_atr, atr_radius, 360),
     airport
]  

    path = leg_south + leg_circles + leg_home 
     
    return flight_time, path