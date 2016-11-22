# -*- coding: utf-8 -*-

u"""
Utilities needed to deal with different geodetic projection systems.

WGS84 (EPSG 4326) projection system

    “OpenStreetMap uses the WGS84 spatial reference system used by the
    Global Positioning System (GPS).  It uses geographic coordinates
    between -180° and 180° longitude and -90° and 90° latitude.  So
    this is the "native" OSM format.

    This is the right choice for you if you need geographical coordinates
    or want to transform the coordinates into some other spatial reference
    system or projection.”

    -- from `Projections/Spatial reference systems: WGS84 (EPSG 4326)
    <http://openstreetmapdata.com/info/projections#wgs84>`_


Mercator (EPSG 3857) projection system

    “Most tiled web maps (such as the standard OSM maps and Google Maps)
    use this Mercator projection.

    The map area of such maps is a square with x and y coordiates both
    between -20,037,508.34 and 20,037,508.34 meters.  As a result data
    north of about 85.1° and south of about -85.1° latitude can not be
    shown and has been cut off. …

    This is the right choice for you if you are creating tiled web maps.”

    -- from `Projections/Spatial reference systems: Mercator (EPSG 3857)
    <http://openstreetmapdata.com/info/projections#mercator>`_

Hint: iOS tracked coordinates come in WGS84 (EPSG 4326) projection and nearly
all geomap-services, like google-maps, utilize Mercator (EPSG 3857) projection.
"""

import math


def _generate_epsg_4326_to_epsg_3857_converter():
    factor1 = 20037508.34 / 180
    factor2 = math.pi / 360
    factor3 = math.pi / 180

    def convert_epsg_4326_to_epsg_3857(latitude, longitude):
        """
        Convert WGS84 (EPSG 4326) to Mercator (EPSG 3857) projection.
        """
        x = longitude * factor1
        y = (math.log(math.tan((90 + latitude) * factor2)) / factor3) * factor1
        return x, y

    return convert_epsg_4326_to_epsg_3857

convert_gps_to_map_coordinates = _generate_epsg_4326_to_epsg_3857_converter()


def _generate_epsg_3857_to_epsg_4326_converter():
    factor1 = 180 / 20037508.34
    factor2 = 360 / math.pi
    factor3 = math.pi / 20037508.34

    def convert_epsg_3857_to_epsg_4326(x, y):
        """
        Convert Mercator (EPSG 3857) to WGS84 (EPSG 4326) projection.
        """
        longitude = x * factor1
        latitude = factor2 * math.atan(math.exp(y * factor3)) - 90
        return latitude, longitude

    return convert_epsg_3857_to_epsg_4326

convert_map_to_gps_coordinates = _generate_epsg_3857_to_epsg_4326_converter()
