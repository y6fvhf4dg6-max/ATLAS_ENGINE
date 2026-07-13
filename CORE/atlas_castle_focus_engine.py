# CORE/atlas_castle_focus_engine.py

import math

from CORE.atlas_castle_building_profiler import (
    AtlasCastleBuildingProfiler,
)
from CORE.atlas_castle_footprint_regularizer import (
    AtlasCastleFootprintRegularizer,
)
from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)


class AtlasCastleFocusEngine:
    """
    ATLAS Castle Focus Engine v0.1

    Kale modelinin gerçek coğrafi sınırlarını hesaplar.

    Odak alanına dahil edilen geometriler:
    - Kale içinde sınıflandırılan kullanılabilir binalar
    - Bağımsız ve inferred kale surları
    - Relation kale kabuklarının dış geometrileri

    Bbox, kaynak okuma bbox'ının dışına taşamaz.
    X ve Y ölçeği burada değiştirilmez.
    """

    DEFAULT_PADDING_M = 10.0

    @staticmethod
    def calculate_focus_bbox(
        raw_buildings,
        castles,
        independent_castle_walls,
        shell_castles,
        source_bbox,
        min_points=4,
        max_points=300,
        padding_m=DEFAULT_PADDING_M,
        debug=True,
    ):
        geometries = []

        accepted_building_count = 0
        wall_geometry_count = 0
        shell_geometry_count = 0

        for raw_building in raw_buildings:
            if not AtlasCastleFocusEngine._is_building_usable(
                raw_building=raw_building,
                min_points=min_points,
                max_points=max_points,
            ):
                continue

            prepared_building = AtlasCastleFootprintRegularizer.prepare(
                raw_building=raw_building,
                castles=castles,
            )

            profile = AtlasCastleBuildingProfiler.profile(
                raw_building=prepared_building,
                castles=castles,
            )

            if not profile.get(
                "inside_castle",
                False,
            ):
                continue

            geometry = prepared_building.get(
                "geometry",
                [],
            )

            if len(geometry) < 3:
                continue

            geometries.append(geometry)
            accepted_building_count += 1

        for wall in independent_castle_walls:
            geometry = wall.get(
                "geometry",
                [],
            )

            if len(geometry) < 2:
                continue

            geometries.append(geometry)
            wall_geometry_count += 1

        for castle in shell_castles:
            outer_geometries = castle.get(
                "outer_geometries",
                [],
            )

            if not outer_geometries:
                geometry = castle.get(
                    "geometry",
                    [],
                )

                if geometry:
                    outer_geometries = [geometry]

            inner_geometries = castle.get(
                "inner_geometries",
                [],
            )

            if not outer_geometries:
                continue

            normalized = AtlasCastleShellTriangulator.normalize_rings(
                outer_ring=outer_geometries[0],
                inner_rings=[
                    *outer_geometries[1:],
                    *inner_geometries,
                ],
            )

            real_outer_ring = normalized.get(
                "outer_ring",
                [],
            )

            if len(real_outer_ring) < 3:
                continue

            geometries.append(real_outer_ring)
            shell_geometry_count += 1

        raw_focus_bbox = AtlasCastleFocusEngine._bbox_from_geometries(geometries)

        if raw_focus_bbox is None:
            if debug:
                AtlasCastleFocusEngine._print_fallback_report(
                    source_bbox=source_bbox,
                )

            return {
                "bbox": source_bbox,
                "raw_bbox": None,
                "used_fallback": True,
                "accepted_buildings": accepted_building_count,
                "wall_geometries": wall_geometry_count,
                "shell_geometries": shell_geometry_count,
                "geometry_count": len(geometries),
                "padding_m": padding_m,
            }

        padded_bbox = AtlasCastleFocusEngine._add_padding_m(
            bbox=raw_focus_bbox,
            padding_m=padding_m,
        )

        clipped_bbox = AtlasCastleFocusEngine._clip_bbox(
            bbox=padded_bbox,
            source_bbox=source_bbox,
        )

        result = {
            "bbox": clipped_bbox,
            "raw_bbox": raw_focus_bbox,
            "used_fallback": False,
            "accepted_buildings": accepted_building_count,
            "wall_geometries": wall_geometry_count,
            "shell_geometries": shell_geometry_count,
            "geometry_count": len(geometries),
            "padding_m": padding_m,
        }

        if debug:
            AtlasCastleFocusEngine._print_report(
                result=result,
            )

        return result

    @staticmethod
    def _is_building_usable(
        raw_building,
        min_points,
        max_points,
    ):
        geometry = raw_building.get(
            "geometry",
            [],
        )

        point_count = len(geometry)

        if point_count < min_points:
            return False

        if max_points is not None and point_count > max_points:
            return False

        return True

    @staticmethod
    def _bbox_from_geometries(
        geometries,
    ):
        latitudes = []
        longitudes = []

        for geometry in geometries:
            for point in geometry:
                if not point or len(point) < 2:
                    continue

                latitude = float(point[0])
                longitude = float(point[1])

                latitudes.append(latitude)
                longitudes.append(longitude)

        if not latitudes or not longitudes:
            return None

        return (
            min(latitudes),
            min(longitudes),
            max(latitudes),
            max(longitudes),
        )

    @staticmethod
    def _add_padding_m(
        bbox,
        padding_m,
    ):
        if padding_m is None:
            padding_m = 0.0

        padding_m = max(
            0.0,
            float(padding_m),
        )

        if padding_m == 0.0:
            return bbox

        south, west, north, east = bbox

        mean_latitude_rad = math.radians((south + north) / 2.0)

        latitude_padding = padding_m / 111_320.0

        longitude_divisor = 111_320.0 * max(
            math.cos(mean_latitude_rad),
            0.000001,
        )

        longitude_padding = padding_m / longitude_divisor

        return (
            south - latitude_padding,
            west - longitude_padding,
            north + latitude_padding,
            east + longitude_padding,
        )

    @staticmethod
    def _clip_bbox(
        bbox,
        source_bbox,
    ):
        south, west, north, east = bbox

        source_south = source_bbox[0]
        source_west = source_bbox[1]
        source_north = source_bbox[2]
        source_east = source_bbox[3]

        clipped_south = max(
            source_south,
            south,
        )

        clipped_west = max(
            source_west,
            west,
        )

        clipped_north = min(
            source_north,
            north,
        )

        clipped_east = min(
            source_east,
            east,
        )

        if clipped_south >= clipped_north or clipped_west >= clipped_east:
            return source_bbox

        return (
            clipped_south,
            clipped_west,
            clipped_north,
            clipped_east,
        )

    @staticmethod
    def _print_report(
        result,
    ):
        bbox = result["bbox"]
        raw_bbox = result["raw_bbox"]

        print("")
        print("=" * 70)
        print("ATLAS CASTLE FOCUS ENGINE REPORT")
        print("=" * 70)
        print(f"Accepted buildings : " f"{result['accepted_buildings']}")
        print(f"Wall geometries    : " f"{result['wall_geometries']}")
        print(f"Shell geometries   : " f"{result['shell_geometries']}")
        print(f"Total geometries   : " f"{result['geometry_count']}")
        print(f"Padding            : " f"{result['padding_m']:.2f} m")
        print(f"Raw south          : " f"{raw_bbox[0]:.8f}")
        print(f"Raw west           : " f"{raw_bbox[1]:.8f}")
        print(f"Raw north          : " f"{raw_bbox[2]:.8f}")
        print(f"Raw east           : " f"{raw_bbox[3]:.8f}")
        print(f"Focus south        : " f"{bbox[0]:.8f}")
        print(f"Focus west         : " f"{bbox[1]:.8f}")
        print(f"Focus north        : " f"{bbox[2]:.8f}")
        print(f"Focus east         : " f"{bbox[3]:.8f}")
        print("=" * 70)
        print("")

    @staticmethod
    def _print_fallback_report(
        source_bbox,
    ):
        print("")
        print("=" * 70)
        print("ATLAS CASTLE FOCUS ENGINE REPORT")
        print("=" * 70)
        print("Castle-focus geometrisi bulunamadı.")
        print("Kaynak bbox kullanılacak.")
        print(f"South              : " f"{source_bbox[0]:.8f}")
        print(f"West               : " f"{source_bbox[1]:.8f}")
        print(f"North              : " f"{source_bbox[2]:.8f}")
        print(f"East               : " f"{source_bbox[3]:.8f}")
        print("=" * 70)
        print("")
