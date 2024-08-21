import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240821a():
    flight_time = pd.Timestamp(2024, 8, 21, 12, 0, 0).tz_localize("UTC")
     
    radius = 130e3
    atr_radius = 70e3

    airport=sal
    mindelo = LatLon(lat=16.8778, lon=-24.995,label= "mindelo")
    north_in = LatLon(lat=15.00, lon=-26.71,label= "north_in")
    north_out = LatLon(lat=16.8778, lon=-26.71,label= "north_out")
    south_tp = LatLon(lat=3., lon=-26.71,label= "south_tp")

    c_north = LatLon(13.7,-26.71, "c_north")
    c_south = LatLon(5.5, -26.71, "c_south")
    c_mid1=LatLon(11.1,-26.71,"c_mid1")
    c_mid2=LatLon(8.3,-26.71,"c_mid2")

    leg_south = [
        airport, 
        north_in,
        south_tp
    ]

    leg_circles = [
        IntoCircle(c_south, radius, 360),
            IntoCircle(c_mid2, radius, 360),
        IntoCircle(c_mid1, radius, 360),
        IntoCircle(c_north, radius, 360),
    ]

    leg_home = [
        north_out,
        airport
    ]  

    path = leg_south+leg_circles+leg_home
     
    return flight_time, path