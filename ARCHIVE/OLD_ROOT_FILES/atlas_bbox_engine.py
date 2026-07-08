"""
ATLAS Engine 2.0

Module : BBox Engine
Version: 1.0

Purpose:
Create geographic bounding boxes around a center coordinate.
Used for local OSM extraction from PBF files.
"""

import math


def meters_to_lat_degrees(meters):
    return meters / 111_320


def meters_to_lon_degrees(meters, latitude):
    return meters / (111_320 * math.cos(math.radians(latitude)))


def create_bbox(latitude, longitude, size_m):
    half_size = size_m / 2

    lat_delta = meters_to_lat_degrees(half_size)
    lon_delta = meters_to_lon_degrees(half_size, latitude)

    return {
        "south": latitude - lat_delta,
        "west": longitude - lon_delta,
        "north": latitude + lat_delta,
        "east": longitude + lon_delta,
    }


def print_bbox(bbox):
    print("South:", bbox["south"])
    print("West :", bbox["west"])
    print("North:", bbox["north"])
    print("East :", bbox["east"])


def main():
    print("=" * 60)
    print("ATLAS BBOX ENGINE v1.0")
    print("=" * 60)

    latitude = 50.1104684
    longitude = 8.6816587
    size_m = 1000

    bbox = create_bbox(latitude, longitude, size_m)

    print("Center:", latitude, longitude)
    print("Size  :", size_m, "m")
    print()
    print_bbox(bbox)

    print("=" * 60)


if __name__ == "__main__":
    main()