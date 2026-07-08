from math import cos, radians


def calculate_area_bounds(center_latitude, center_longitude, real_size_m):
    half_size_m = real_size_m / 2

    meters_per_degree_latitude = 111_320
    meters_per_degree_longitude = 111_320 * cos(radians(center_latitude))

    delta_latitude = half_size_m / meters_per_degree_latitude
    delta_longitude = half_size_m / meters_per_degree_longitude

    north = center_latitude + delta_latitude
    south = center_latitude - delta_latitude
    east = center_longitude + delta_longitude
    west = center_longitude - delta_longitude

    return {
        "north": north,
        "south": south,
        "east": east,
        "west": west,
    }


if __name__ == "__main__":
    center_latitude = 50.1104684
    center_longitude = 8.6816587
    real_size_m = 1000

    bounds = calculate_area_bounds(
        center_latitude,
        center_longitude,
        real_size_m
    )

    print("ATLAS Area Bounds")
    print("North:", bounds["north"])
    print("South:", bounds["south"])
    print("East :", bounds["east"])
    print("West :", bounds["west"])