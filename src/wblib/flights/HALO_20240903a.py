import pandas as pd
import datetime
from orcestra.flightplan import sal, LatLon, IntoCircle, FlightPlan

def _flight_HALO_20240903a():
    flight_time = pd.Timestamp(2024, 9, 3, 12, 0, 0).tz_localize("UTC")

    radius = 72e3*1.852
    atr_radius = 38e3*1.852
    airport = sal

    ec_north = LatLon(lat=14.75, lon=-29.64460064814815, label=None, fl=None, time=None, note=None)
    ec_south = LatLon(lat=2.0, lon=-32.05971354102406, label=None, fl=None, time=None, note=None)
    c_north  = LatLon(lat=13.0, lon=-29.983627306386914, label=None, fl=None, time=None, note=None)
    c_south  = LatLon(lat=4.0, lon=-31.686613475177307, label=None, fl=None, time=None, note=None)
    c_mid    = LatLon(lat=8.501448886319212, lon=-30.841571222673966, label=None, fl=None, time=None, note=None)
    c_atr    = LatLon(ec_north.lat+atr_radius/1852./60.,-22.1, label = "c_atr")
    j_beg    = LatLon(lat=ec_north.lat,lon=-25.).assign(label = "junction")
    ec_under = LatLon(lat=10.301303243452365, lon=-30.50034768724039, label=None, fl=None, time=datetime.datetime(2024, 9, 3, 16, 8, 30, 758740, tzinfo=datetime.timezone.utc), note=None)

    # Additional Waypoints
    x_cnn = LatLon(lat=13.67, lon=-29.85425074074074, label=None, fl=None, time=None, note=None)
    x_cns = LatLon(lat=11.5, lon=-30.271701820425793, label=None, fl=None, time=None, note=None)
    x_cms = LatLon(lat=7.75, lon=-30.983356940160395, label=None, fl=None, time=None, note=None)
    x_xsd = c_south.towards(c_mid).assign(label="x_sonde", note="Position for an extra sonde heading south")
    j_atr = c_atr.towards(sal,distance=-atr_radius).assign(label="j_atr", note = "ATR circle start and end")
    extra_waypoints = [LatLon(17.5,-24.00).assign(label="x_atr", note="alternative ATR circle")]

    # Define Flight Paths
    waypoints = [
        airport.assign(fl=0),
        j_beg.assign(fl=390),
        ec_north.assign(fl=410),
        c_mid.assign(fl=410),
        x_xsd.assign(fl=410),
        IntoCircle(c_south.assign(fl=410), radius, -360),
        x_cms.assign(fl=450).assign(note='might be to soon to rise to FL450, if so rise to FL430 and higher later'),
        IntoCircle(c_mid.assign(fl=450), radius, -360),
        ec_under.assign(fl=450),
        x_cns.assign(fl=450),
        IntoCircle(c_north.assign(fl=450), radius, -360,enter=90),
        x_cnn.assign(fl=450),
        ec_north.assign(fl=450),
        j_beg.assign(fl=450),
        j_atr.assign(fl=350),
        IntoCircle(c_atr.assign(fl=350), atr_radius,-360),
        airport.assign(fl=0),
        ]

    plan = FlightPlan(waypoints, None, extra_waypoints=extra_waypoints)
    return flight_time, plan.path