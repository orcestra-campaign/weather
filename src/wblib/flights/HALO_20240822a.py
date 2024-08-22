import pandas as pd
from orcestra.flightplan import sal, bco, LatLon, IntoCircle

def _flight_HALO_20240822a():
    flight_time = pd.Timestamp(2024, 8, 22, 12, 0, 0).tz_localize("UTC")
     
    radius = 1.852 * 72e3 # factor of 1.852 is km/nm (definition)
    atr_radius = 1.852 * 38e3 

    airport = sal

    lat_north = 19.0
    lat_south = 4.0

    lat_edge_north = 13.3
    lat_edge_center = 9.5
    lat_edge_south = 6.0

    lat_north_ec = 17.0
    lat_meet_ec = 15.75
    lat_south_ec = 14.5

    lat_mindelo =  16.877833
    lon_mindelo = -24.994975

    lat_atr_circle_ec = 17.7

    # Setting lat/lon coordinates

    # Points where we get on ec track?
    north_ec = LatLon(lat_north, -22.15938483419649, "north")
    south_ec = LatLon(lat_south, -25.041858611111113, "south")

    # Points where to meet atr and earthcare
    north_ec_atr = LatLon(lat_north_ec, -22.55787757262052, "north_ec")
    meet_ec_atr = LatLon(lat_meet_ec, -22.804044257356917, "meet_ec")
    south_ec_atr = LatLon(lat_south_ec, -23.048144165572634, "south_ec")

    # Intersection of ITCZ edges with ec track
    circle_north = LatLon(lat_edge_north, -23.28071609789994, "circle_north")

    circle_center = LatLon(lat_edge_center, -24.007665138535156, "circle_center")

    circle_south = LatLon(lat_edge_south, -24.667570555555557, "circle_south")

    circle_atr_ec = LatLon(lat_atr_circle_ec, -22.419178307573418,'circle_atr_ec')

    mindelo = LatLon(lat_mindelo, lon_mindelo, 'mindelo')



    leg_south = [
        airport,
        north_ec_atr,
        north_ec,
        IntoCircle(circle_atr_ec, atr_radius, 360),
        north_ec_atr,
        meet_ec_atr,
        south_ec_atr,
        circle_north,
        circle_center,
        circle_south,
        south_ec
    ]

    leg_circles = [
        IntoCircle(circle_south, radius, 360),
        IntoCircle(circle_center, radius, 360),
        IntoCircle(circle_north, radius, 360),
    ]
        
    leg_home = [
        south_ec_atr,
        mindelo,
        IntoCircle(circle_atr_ec, atr_radius, 360),
        airport
    ]

    path = leg_south + leg_circles + leg_home
     
    return flight_time, path