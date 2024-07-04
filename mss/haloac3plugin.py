# -*- coding: utf-8 -*-
"""

    mslib.plugins.io.csv
    ~~~~~~~~~~~~~~~~~~~~

    plugin for csv format flight track export

    This file is part of mss.

    :copyright: Copyright 2008-2014 Deutsches Zentrum fuer Luft- und Raumfahrt e.V.
    :copyright: Copyright 2011-2014 Marc Rautenhaus (mr)
    :copyright: Copyright 2016-2019 by the mss team, see AUTHORS.
    :license: APACHE-2.0, see LICENSE for details.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from __future__ import absolute_import
from __future__ import division

from builtins import str

import unicodecsv as csv
import os

import mslib.msui.flighttrack as ft
from fs import open_fs

nm = 1.852  # nautical mile in kilometers


def get_deg_min(coord):
    de = int(abs(coord))
    mi = (abs(coord) - de) * 60
    if coord < 0:
        return -de, -mi
    else:
        return de, mi


def seconds_to_hhmmss(seconds):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"


def save_to_csv_halo(filename, name, waypoints):
    if not filename:
        raise ValueError("fileexportname to save flight track cannot be None")
    _dirname, _name = os.path.split(filename)
    _fs = open_fs(_dirname)
    with _fs.open(_name, "wb") as csvfile:
        csv_writer = csv.writer(csvfile, dialect='excel', delimiter=";", lineterminator="\n", encoding="1252")
        csv_writer.writerow([name])
        csv_writer.writerow(["Index", "Lat (+-90)", "Lon (+-180)", "Location", "Lat (D°M.m)", "Lon (D°M.m)",
                             "Flightlevel", "Pressure (hPa)", "Leg dist. (km)", "Leg dist. (nm)",
                             "Cum. dist. (km)", "Cum. dist. (nm)", "Leg time", "Cum. time", "Time (UTC)", "Comments"])
        for i, wp in enumerate(waypoints):
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            loc = str(wp.location)
            lat = "{:.3f}".format(wp.lat)
            lon = "{:.3f}".format(wp.lon)
            lat_dm = f"{lade:02.0f}°{lami:04.1f}' {'S' if wp.lat < 0 else 'N'}"
            lon_dm = f"{lode:03.0f}°{lomi:04.1f}' {'W' if wp.lon < 0 else 'E'}"
            lvl = "{:.0f}".format(wp.flightlevel)
            pre = "{:.1f}".format(wp.pressure / 100.)
            leg = "{:.1f}".format(wp.distance_to_prev)
            leg_nm = f"{wp.distance_to_prev / nm:.1f}"
            cum = "{:.1f}".format(wp.distance_total)
            cum_nm = f"{wp.distance_total / nm:.1f}"
            leg_t = seconds_to_hhmmss(wp.leg_time)
            cum_t = seconds_to_hhmmss(wp.cum_time)
            utc = wp.utc_time
            com = str(wp.comments)
            csv_writer.writerow([f"W{i}", lat, lon, loc, lat_dm, lon_dm, lvl, pre, leg, leg_nm, cum, cum_nm, leg_t,
                                 cum_t, utc, com])


def save_to_txt_halo(filename, name, waypoints):
    if not filename:
        raise ValueError("fileexportname to save flight track cannot be None")
    _dirname, _name = os.path.split(filename)
    _fs = open_fs(_dirname)
    with _fs.open(_name, "wb") as csvfile:
        csv_writer = csv.writer(csvfile, dialect='excel', delimiter="\t", lineterminator="\n", encoding="utf-8")
        csv_writer.writerow([name])
        csv_writer.writerow(["Index", "Lat (+-90)", "Lon (+-180)", "Location", "Lat (D°M.m)", "Lon (D°M.m)",
                             "Flightlevel", "Pressure (hPa)", "Leg dist. (km)", "Leg dist. (nm)",
                             "Cum. dist. (km)", "Cum. dist. (nm)", "Leg time", "Cum. time", "Time (UTC)", "Comments"])
        for i, wp in enumerate(waypoints):
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            loc = str(wp.location)
            lat = "{:.3f}".format(wp.lat)
            lon = "{:.3f}".format(wp.lon)
            lat_dm = f"{lade:02.0f}°{lami:04.1f}' {'S' if wp.lat < 0 else 'N'}"
            lon_dm = f"{lode:03.0f}°{lomi:04.1f}' {'W' if wp.lon < 0 else 'E'}"
            lvl = "{:.0f}".format(wp.flightlevel)
            pre = "{:.1f}".format(wp.pressure / 100.)
            leg = "{:.1f}".format(wp.distance_to_prev)
            leg_nm = f"{wp.distance_to_prev / nm:.1f}"
            cum = "{:.1f}".format(wp.distance_total)
            cum_nm = f"{wp.distance_total / nm:.1f}"
            leg_t = seconds_to_hhmmss(wp.leg_time)
            cum_t = seconds_to_hhmmss(wp.cum_time)
            utc = wp.utc_time
            com = str(wp.comments)
            csv_writer.writerow([f"W{i}", lat, lon, loc, lat_dm, lon_dm, lvl, pre, leg, leg_nm, cum, cum_nm, leg_t,
                                 cum_t, utc, com])


def save_to_csv_polar(filename, name, waypoints):
    if not filename:
        raise ValueError("fileexportname to save flight track cannot be None")
    _dirname, _name = os.path.split(filename)
    _fs = open_fs(_dirname)
    with _fs.open(_name, "wb") as csvfile:
        csv_writer = csv.writer(csvfile, dialect='excel', delimiter=";", lineterminator="\n", encoding="1252")
        csv_writer.writerow([name])
        csv_writer.writerow(["Index", "Lat (D°M.m)", "Lon (D°M.m)",  "Location", "Lat (+-90)", "Lon (+-180)",
                             "Flightlevel", "Pressure (hPa)", "Leg dist. (km)", "Leg dist(nm)", "Cum. dist. (km)",
                             "Cum. dist. (nm)", "Leg time", "Cum. time", "Time (UTC)", "Comments"])
        for i, wp in enumerate(waypoints):
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            loc = str(wp.location)
            lat = "{:.3f}".format(wp.lat)
            lon = "{:.3f}".format(wp.lon)
            lat_dm = f"{lade:02.0f}°{lami:04.1f}' {'S' if wp.lat < 0 else 'N'}"
            lon_dm = f"{lode:03.0f}°{lomi:04.1f}' {'W' if wp.lon < 0 else 'E'}"
            lvl = "{:.0f}".format(wp.flightlevel)
            pre = "{:.1f}".format(wp.pressure / 100.)
            leg = "{:.1f}".format(wp.distance_to_prev)
            leg_nm = f"{wp.distance_to_prev / nm:.1f}"
            cum = "{:.1f}".format(wp.distance_total)
            cum_nm = f"{wp.distance_total / nm:.1f}"
            leg_t = seconds_to_hhmmss(wp.leg_time)
            cum_t = seconds_to_hhmmss(wp.cum_time)
            utc = wp.utc_time
            com = str(wp.comments)
            csv_writer.writerow([f"W{i}", lat_dm, lon_dm, loc, lat, lon, lvl, pre, leg, leg_nm, cum, cum_nm, leg_t,
                                 cum_t, utc, com])


def save_to_txt_polar(filename, name, waypoints):
    if not filename:
        raise ValueError("fileexportname to save flight track cannot be None")
    _dirname, _name = os.path.split(filename)
    _fs = open_fs(_dirname)
    with _fs.open(_name, "wb") as csvfile:
        csv_writer = csv.writer(csvfile, dialect='excel', delimiter="\t", lineterminator="\n", encoding="utf-8")
        csv_writer.writerow([name])
        csv_writer.writerow(["Index", "Lat (D°M.m)", "Lon (D°M.m)",  "Location", "Lat (+-90)", "Lon (+-180)",
                             "Flightlevel", "Pressure (hPa)", "Leg dist. (km)", "Leg dist(nm)", "Cum. dist. (km)",
                             "Cum. dist. (nm)", "Leg time", "Cum. time", "Time (UTC)", "Comments"])
        for i, wp in enumerate(waypoints):
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            loc = str(wp.location)
            lat = "{:.3f}".format(wp.lat)
            lon = "{:.3f}".format(wp.lon)
            lat_dm = f"{lade:02.0f}°{lami:04.1f}' {'S' if wp.lat < 0 else 'N'}"
            lon_dm = f"{lode:03.0f}°{lomi:04.1f}' {'W' if wp.lon < 0 else 'E'}"
            lvl = "{:.0f}".format(wp.flightlevel)
            pre = "{:.1f}".format(wp.pressure / 100.)
            leg = "{:.1f}".format(wp.distance_to_prev)
            leg_nm = f"{wp.distance_to_prev / nm:.1f}"
            cum = "{:.1f}".format(wp.distance_total)
            cum_nm = f"{wp.distance_total / nm:.1f}"
            leg_t = seconds_to_hhmmss(wp.leg_time)
            cum_t = seconds_to_hhmmss(wp.cum_time)
            utc = wp.utc_time
            com = str(wp.comments)
            csv_writer.writerow([f"W{i}", lat_dm, lon_dm, loc, lat, lon, lvl, pre, leg, leg_nm, cum, cum_nm, leg_t,
                                 cum_t, utc, com])


def save_to_planet_csv(filename, name, waypoints):
    if not filename:
        raise ValueError("fileexportname to save flight track cannot be None")
    _dirname, _name = os.path.split(filename)
    _fs = open_fs(_dirname)
    with _fs.open(_name, "wb") as csvfile:
        csv_writer = csv.writer(csvfile, dialect='excel', delimiter=",", lineterminator="\n", encoding="utf-8",
                                quoting=csv.QUOTE_ALL)
        lonlat = list()
        for i, wp in enumerate(waypoints):
            if wp.location == "":
                loc = f"W{i}"
            else:
                loc = str(wp.location)
            lonlat.append(f"{wp.lon:.3f},{wp.lat:.3f}")
            csv_writer.writerow(["Point", loc, None, "red", None, None, lonlat[i]])

        line = ["LineString", None, None, "blue", None, None]
        line.extend(lonlat)
        csv_writer.writerow(line)
