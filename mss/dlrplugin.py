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


def save_to_csv(filename, name, waypoints):
    if not filename:
        raise ValueError("fileexportname to save flight track cannot be None")
    _dirname, _name = os.path.split(filename)
    _fs = open_fs(_dirname)
    with _fs.open(_name, "wb") as csvfile:
        csv_writer = csv.writer(csvfile, dialect='excel', delimiter=";", lineterminator="\n", encoding="1252")
        csv_writer.writerow([name])
        csv_writer.writerow(["Index", "Location", "Lat (+-90)", "Lon (+-180)", "Lat (D°M.m)", "Lon (D°M.m)",
                             "Flightlevel", "Pressure (hPa)", "Leg dist. (km)", "Cum. dist. (km)", "Leg time",
                             "Cum. time", "Time (UTC)", "Comments"])
        for i, wp in enumerate(waypoints):
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            loc = str(wp.location)
            lat = "{:.3f}".format(wp.lat)
            lon = "{:.3f}".format(wp.lon)
            lat_dm = f"{lade:02.0f}°{lami:04.1f}' {'S' if wp.lat < 0 else 'N'}"
            lon_dm = f"{lode:03.0f}°{lomi:04.1f}' {'W' if wp.lon < 0 else 'E'}"
            lvl = "{:.3f}".format(wp.flightlevel)
            pre = "{:.3f}".format(wp.pressure / 100.)
            leg = "{:.3f}".format(wp.distance_to_prev)
            cum = "{:.3f}".format(wp.distance_total)
            leg_t = seconds_to_hhmmss(wp.leg_time)
            cum_t = seconds_to_hhmmss(wp.cum_time)
            utc = wp.utc_time
            com = str(wp.comments)
            csv_writer.writerow([i, loc, lat, lon, lat_dm, lon_dm, lvl, pre, leg, cum, leg_t, cum_t, utc, com])

    for i, wp in enumerate(waypoints):
        if wp.lon <= -180:
            wp.lon = wp.lon + 360
        if wp.lon >= 180:
            wp.lon = wp.lon - 360

    with _fs.open(_name, "a") as csvfile:
        csvfile.write("\n")
        csvfile.write("format D.d\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            coord += f"{abs(wp.lat):06.3f}{'S' if wp.lat < 0 else 'N'}".replace(".", "")
            coord += f"{abs(wp.lon):07.3f}{'W' if wp.lon < 0 else 'E'}".replace(".", "")
            csvfile.write(coord)

        # 2. im Format D-M.m mit S/N/W/E. ....    3450.0S06500.0W
        csvfile.write("\n")
        csvfile.write("format D-M.m\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            coord += f"{lade:02.0f}{lami:04.1f}{'S' if wp.lat < 0 else 'N'}"
            coord += f"{lode:03.0f}{lomi:04.1f}{'W' if wp.lon < 0 else 'E'}"
            csvfile.write(coord)

        # 3.im Format D-M mit S/N/W/E. ....    3450S06500W
        csvfile.write("\n")
        csvfile.write("format D-M\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            coord += f"{lade:02.0f}{lami:02.0f}{'S' if wp.lat < 0 else 'N'}"
            coord += f"{lode:03.0f}{lomi:02.0f}{'W' if wp.lon < 0 else 'E'}"
            csvfile.write(coord)

        # 4.im Format D-Mm mit S/N/W/E. ....    S34500W065000
        csvfile.write("\n")
        csvfile.write("form D-M\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            coord += f"{'S' if wp.lat < 0 else 'N'}{lade:02.0f}{lami:02.0f}".replace(".", "")
            coord += f"{'W' if wp.lon < 0 else 'E'}{lode:03.0f}{lomi:02.0f}".replace(".", "")

            csvfile.write(coord)

    for i, wp in enumerate(waypoints):
        wp.lon = round(wp.lon * 6) / 6
        wp.lat = round(wp.lat * 6) / 6

    with _fs.open(_name, "a") as csvfile:
        csvfile.write("\n\n")
        csvfile.write("rounded\n")
        csvfile.write("format D.d\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            coord += f"{abs(wp.lat):06.3f}{'S' if wp.lat < 0 else 'N'}".replace(".", "")
            coord += f"{abs(wp.lon):07.3f}{'W' if wp.lon < 0 else 'E'}".replace(".", "")
            csvfile.write(coord)

        # 2. im Format D-M.m mit S/N/W/E. ....    3450.0S06500.0W
        csvfile.write("\n")
        csvfile.write("format D-M.m\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            coord += f"{lade:02.0f}{lami:04.1f}{'S' if wp.lat < 0 else 'N'}"
            coord += f"{lode:03.0f}{lomi:04.1f}{'W' if wp.lon < 0 else 'E'}"
            csvfile.write(coord)

        # 3.im Format D-M mit S/N/W/E. ....    3450S06500W
        csvfile.write("\n")
        csvfile.write("format D-M\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            coord += f"{lade:02.0f}{lami:02.0f}{'S' if wp.lat < 0 else 'N'}"
            coord += f"{lode:03.0f}{lomi:02.0f}{'W' if wp.lon < 0 else 'E'}"
            csvfile.write(coord)

        # 4.im Format D-Mm mit S/N/W/E. ....    S34500W065000
        csvfile.write("\n")
        csvfile.write("form D-M\n")
        for i, wp in enumerate(waypoints):
            coord = ""
            if i > 0:
                coord = " "
            lade, lami = get_deg_min(abs(wp.lat))
            lode, lomi = get_deg_min(abs(wp.lon))
            coord += f"{'S' if wp.lat < 0 else 'N'}{lade:02.0f}{lami:02.0f}".replace(".", "")
            coord += f"{'W' if wp.lon < 0 else 'E'}{lode:03.0f}{lomi:02.0f}".replace(".", "")

            csvfile.write(coord)
