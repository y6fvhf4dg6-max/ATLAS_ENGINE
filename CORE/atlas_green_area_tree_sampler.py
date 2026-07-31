"""
ATLAS Green Area Tree Sampler v0.1

OSM yeşil alan poligonlarından baskıya uygun temsili ağaç
noktaları üretir.

Temel ilkeler:
- Aynı girdi her zaman aynı sonucu verir.
- Noktalar poligon sınırlarının kesinlikle içinde kalır.
- Açık çim ve rekreasyon alanları otomatik ağaçlandırılmaz.
- Mevcut ağaçların çok yakınına yeni örnek eklenmez.
- Toplam çıktı sayısı global üst sınırı aşmaz.
"""

import hashlib
import math


class AtlasGreenAreaTreeSampler:
    SUPPORTED_PARK_TYPES = {
        "landuse:forest",
        "natural:wood",
        "natural:scrub",
        "leisure:park",
        "leisure:garden",
    }

    TARGET_COUNTS = {
        "landuse:forest": 24,
        "natural:wood": 20,
        "natural:scrub": 8,
        "leisure:park": 6,
        "leisure:garden": 4,
    }

    MIN_EXISTING_TREE_DISTANCE_M = 4.0

    @staticmethod
    def sample(
        parks,
        existing_trees,
        max_trees,
        bbox=None,
    ):
        if max_trees <= 0:
            return []

        parks = parks or []
        existing_trees = existing_trees or []

        sampled_trees = []
        occupied_positions = (
            AtlasGreenAreaTreeSampler
            ._valid_tree_positions(existing_trees)
        )

        ordered_parks = sorted(
            parks,
            key=AtlasGreenAreaTreeSampler._park_sort_key,
        )

        for park in ordered_parks:
            if len(sampled_trees) >= max_trees:
                break

            park_type = park.get("park_type")

            if park_type not in (
                AtlasGreenAreaTreeSampler
                .SUPPORTED_PARK_TYPES
            ):
                continue

            geometry = (
                AtlasGreenAreaTreeSampler
                ._normalized_geometry(
                    park.get("geometry", []),
                )
            )

            if len(geometry) < 3:
                continue

            target_count = (
                AtlasGreenAreaTreeSampler
                .TARGET_COUNTS[park_type]
            )

            candidates = (
                AtlasGreenAreaTreeSampler
                ._candidate_points(
                    geometry=geometry,
                    park_id=park.get("id"),
                    park_type=park_type,
                    target_count=target_count,
                )
            )

            park_sample_index = 0

            for lat, lon in candidates:
                if len(sampled_trees) >= max_trees:
                    break

                if (
                    bbox is not None
                    and not (
                        AtlasGreenAreaTreeSampler
                        ._point_inside_bbox(
                            lat=lat,
                            lon=lon,
                            bbox=bbox,
                        )
                    )
                ):
                    continue

                if (
                    AtlasGreenAreaTreeSampler
                    ._is_too_close_to_positions(
                        lat=lat,
                        lon=lon,
                        positions=occupied_positions,
                        minimum_distance_m=(
                            AtlasGreenAreaTreeSampler
                            .MIN_EXISTING_TREE_DISTANCE_M
                        ),
                    )
                ):
                    continue

                park_id = park.get("id")

                sampled_trees.append(
                    {
                        "id": (
                            "osm_green_area_fill_"
                            f"{park_id}_"
                            f"{park_sample_index}"
                        ),
                        "lat": lat,
                        "lon": lon,
                        "tree_type": "tree",
                        "tags": {
                            "source": "osm_green_area_fill",
                            "park_id": park_id,
                            "park_type": park_type,
                        },
                    }
                )

                occupied_positions.append((lat, lon))
                park_sample_index += 1

        return sampled_trees

    @staticmethod
    def _park_sort_key(park):
        park_id = park.get("id")

        return (
            str(park_id),
            str(park.get("park_type", "")),
        )

    @staticmethod
    def _normalized_geometry(geometry):
        points = []

        for point in geometry or []:
            if not isinstance(point, (tuple, list)):
                continue

            if len(point) < 2:
                continue

            try:
                lat = float(point[0])
                lon = float(point[1])
            except (TypeError, ValueError):
                continue

            if not (
                math.isfinite(lat)
                and math.isfinite(lon)
            ):
                continue

            points.append((lat, lon))

        if (
            len(points) >= 2
            and points[0] == points[-1]
        ):
            points.pop()

        return points

    @staticmethod
    def _candidate_points(
        geometry,
        park_id,
        park_type,
        target_count,
    ):
        min_lat = min(point[0] for point in geometry)
        max_lat = max(point[0] for point in geometry)
        min_lon = min(point[1] for point in geometry)
        max_lon = max(point[1] for point in geometry)

        if min_lat >= max_lat or min_lon >= max_lon:
            return []

        grid_size = max(
            3,
            math.ceil(math.sqrt(target_count * 4)),
        )

        jitter_lat, jitter_lon = (
            AtlasGreenAreaTreeSampler
            ._deterministic_jitter(
                park_id=park_id,
                park_type=park_type,
                grid_size=grid_size,
            )
        )

        candidates = []

        for row in range(grid_size):
            row_fraction = (
                row + 0.5 + jitter_lat
            ) / grid_size

            if not 0.0 < row_fraction < 1.0:
                continue

            lat = min_lat + (
                max_lat - min_lat
            ) * row_fraction

            for column in range(grid_size):
                column_fraction = (
                    column + 0.5 + jitter_lon
                ) / grid_size

                if not 0.0 < column_fraction < 1.0:
                    continue

                lon = min_lon + (
                    max_lon - min_lon
                ) * column_fraction

                if (
                    AtlasGreenAreaTreeSampler
                    ._point_inside_polygon(
                        lat=lat,
                        lon=lon,
                        geometry=geometry,
                    )
                ):
                    candidates.append((lat, lon))

        candidates.sort(
            key=lambda point: (
                AtlasGreenAreaTreeSampler
                ._stable_point_rank(
                    park_id=park_id,
                    park_type=park_type,
                    lat=point[0],
                    lon=point[1],
                )
            )
        )

        return candidates[:target_count]

    @staticmethod
    def _deterministic_jitter(
        park_id,
        park_type,
        grid_size,
    ):
        key = (
            f"{park_id}|{park_type}|{grid_size}"
        ).encode("utf-8")

        digest = hashlib.sha256(key).digest()

        lat_value = int.from_bytes(
            digest[0:4],
            byteorder="big",
        )

        lon_value = int.from_bytes(
            digest[4:8],
            byteorder="big",
        )

        lat_jitter = (
            (lat_value / 0xFFFFFFFF) - 0.5
        ) * 0.30

        lon_jitter = (
            (lon_value / 0xFFFFFFFF) - 0.5
        ) * 0.30

        return lat_jitter, lon_jitter

    @staticmethod
    def _stable_point_rank(
        park_id,
        park_type,
        lat,
        lon,
    ):
        key = (
            f"{park_id}|{park_type}|"
            f"{lat:.12f}|{lon:.12f}"
        ).encode("utf-8")

        return hashlib.sha256(key).hexdigest()

    @staticmethod
    def _point_inside_polygon(
        lat,
        lon,
        geometry,
    ):
        inside = False
        previous_index = len(geometry) - 1

        for current_index in range(len(geometry)):
            current_lat, current_lon = (
                geometry[current_index]
            )
            previous_lat, previous_lon = (
                geometry[previous_index]
            )

            crosses_latitude = (
                (current_lat > lat)
                != (previous_lat > lat)
            )

            if crosses_latitude:
                denominator = (
                    previous_lat - current_lat
                )

                if denominator == 0.0:
                    previous_index = current_index
                    continue

                intersection_lon = (
                    current_lon
                    + (
                        lat - current_lat
                    )
                    * (
                        previous_lon - current_lon
                    )
                    / denominator
                )

                if lon < intersection_lon:
                    inside = not inside

            previous_index = current_index

        return inside

    @staticmethod
    def _point_inside_bbox(
        lat,
        lon,
        bbox,
    ):
        if bbox is None or len(bbox) != 4:
            return True

        south, west, north, east = bbox

        return (
            float(south) <= lat <= float(north)
            and float(west) <= lon <= float(east)
        )

    @staticmethod
    def _valid_tree_positions(trees):
        positions = []

        for tree in trees:
            try:
                lat = float(tree.get("lat"))
                lon = float(tree.get("lon"))
            except (TypeError, ValueError):
                continue

            if (
                math.isfinite(lat)
                and math.isfinite(lon)
            ):
                positions.append((lat, lon))

        return positions

    @staticmethod
    def _is_too_close_to_positions(
        lat,
        lon,
        positions,
        minimum_distance_m,
    ):
        for other_lat, other_lon in positions:
            distance_m = (
                AtlasGreenAreaTreeSampler
                ._approximate_distance_m(
                    lat_a=lat,
                    lon_a=lon,
                    lat_b=other_lat,
                    lon_b=other_lon,
                )
            )

            if distance_m < minimum_distance_m:
                return True

        return False

    @staticmethod
    def _approximate_distance_m(
        lat_a,
        lon_a,
        lat_b,
        lon_b,
    ):
        mean_lat_rad = math.radians(
            (lat_a + lat_b) / 2.0
        )

        north_m = (
            lat_b - lat_a
        ) * 111_320.0

        east_m = (
            lon_b - lon_a
        ) * 111_320.0 * math.cos(mean_lat_rad)

        return math.hypot(
            north_m,
            east_m,
        )
