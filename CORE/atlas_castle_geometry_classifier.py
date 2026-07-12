"""
ATLAS Castle Geometry Classifier v0.1

OSM kale kayıtlarını üretim rollerine ayırır.

Amaç:
- relation kaleleri delikli/delikli olmayan shell olarak sınıflandırmak
- açıkça tanımlanmış bağımsız surları korumak
- relation kaynaklı sur kayıtlarını ayrı tutmak
- bina olmayan kapalı historic=castle way kayıtlarını dolu shell
  yapmak yerine gerektiğinde çevre suru olarak yorumlamak
"""

import math


class AtlasCastleGeometryClassifier:
    VERSION = "0.2"

    MAX_CLOSURE_GAP_M = 5.0

    @staticmethod
    def classify(
        castles,
        castle_walls,
        debug=True,
    ):
        castles = castles or []
        castle_walls = castle_walls or []

        shell_castles = AtlasCastleGeometryClassifier._find_shell_castles(castles)

        shell_castle_ids = {
            castle.get("id") for castle in shell_castles if castle.get("id") is not None
        }

        independent_castle_walls = (
            AtlasCastleGeometryClassifier._find_independent_walls(
                castle_walls=castle_walls,
                shell_castle_ids=shell_castle_ids,
            )
        )

        relation_castle_walls = AtlasCastleGeometryClassifier._find_relation_walls(
            castle_walls
        )

        inferred_perimeter_walls = AtlasCastleGeometryClassifier._infer_perimeter_walls(
            castles=castles,
            explicit_independent_walls=independent_castle_walls,
        )

        independent_castle_walls.extend(inferred_perimeter_walls)

        unknown_castles = AtlasCastleGeometryClassifier._find_unknown_castles(
            castles=castles,
            shell_castles=shell_castles,
            inferred_perimeter_walls=inferred_perimeter_walls,
        )

        result = {
            "shell_castles": shell_castles,
            "independent_castle_walls": (independent_castle_walls),
            "relation_castle_walls": (relation_castle_walls),
            "inferred_perimeter_walls": (inferred_perimeter_walls),
            "unknown_castles": unknown_castles,
        }

        if debug:
            AtlasCastleGeometryClassifier._print_report(
                castles=castles,
                castle_walls=castle_walls,
                result=result,
            )

        return result

    @staticmethod
    def _find_shell_castles(castles):
        return [
            castle for castle in castles if castle.get("geometry_type") == "relation"
        ]

    @staticmethod
    def _find_independent_walls(
        castle_walls,
        shell_castle_ids,
    ):
        return [
            wall
            for wall in castle_walls
            if (
                not wall.get("source_relation_id")
                and wall.get("id") not in shell_castle_ids
            )
        ]

    @staticmethod
    def _find_relation_walls(castle_walls):
        return [wall for wall in castle_walls if wall.get("source_relation_id")]

    @staticmethod
    def _infer_perimeter_walls(
        castles,
        explicit_independent_walls,
    ):
        inferred_walls = []

        explicit_wall_castle_ids = {
            wall.get("source_castle_id")
            for wall in explicit_independent_walls
            if wall.get("source_castle_id") is not None
        }

        for castle in castles:
            if not (AtlasCastleGeometryClassifier._is_inferable_site_boundary(castle)):
                continue

            castle_id = castle.get("id")

            if castle_id in explicit_wall_castle_ids:
                continue

            perimeter_wall = dict(castle)
            perimeter_wall["tags"] = dict(castle.get("tags", {}))
            perimeter_wall["wall_type"] = "inferred_castle_perimeter"
            perimeter_wall["inferred"] = True
            perimeter_wall["source_castle_id"] = castle_id

            inferred_walls.append(perimeter_wall)

        return inferred_walls

    @staticmethod
    def _is_inferable_site_boundary(castle):
        tags = castle.get("tags", {})
        geometry = castle.get("geometry", [])

        return (
            castle.get("geometry_type") == "way"
            and tags.get("historic") == "castle"
            and not tags.get("building")
            and not tags.get("barrier")
            and len(geometry) >= 3
            and AtlasCastleGeometryClassifier._is_closed_geometry(geometry)
        )

    @staticmethod
    def _is_closed_geometry(geometry):
        if len(geometry) < 3:
            return False

        first = geometry[0]
        last = geometry[-1]

        if first == last:
            return True

        gap_m = AtlasCastleGeometryClassifier._distance_meters(
            first,
            last,
        )

        return gap_m <= AtlasCastleGeometryClassifier.MAX_CLOSURE_GAP_M

    @staticmethod
    def _distance_meters(point_a, point_b):
        lat_a, lon_a = point_a
        lat_b, lon_b = point_b

        earth_radius_m = 6371000.0

        lat_a_rad = math.radians(lat_a)
        lat_b_rad = math.radians(lat_b)

        delta_lat = math.radians(lat_b - lat_a)
        delta_lon = math.radians(lon_b - lon_a)

        haversine_value = (
            math.sin(delta_lat / 2.0) ** 2
            + math.cos(lat_a_rad) * math.cos(lat_b_rad) * math.sin(delta_lon / 2.0) ** 2
        )

        central_angle = 2.0 * math.atan2(
            math.sqrt(haversine_value),
            math.sqrt(1.0 - haversine_value),
        )

        return earth_radius_m * central_angle

    @staticmethod
    def _find_unknown_castles(
        castles,
        shell_castles,
        inferred_perimeter_walls,
    ):
        recognized_ids = {
            castle.get("id") for castle in shell_castles if castle.get("id") is not None
        }

        recognized_ids.update(
            wall.get("source_castle_id")
            for wall in inferred_perimeter_walls
            if wall.get("source_castle_id") is not None
        )

        return [
            castle
            for castle in castles
            if (castle.get("id") is not None and castle.get("id") not in recognized_ids)
        ]

    @staticmethod
    def _print_report(
        castles,
        castle_walls,
        result,
    ):
        print("")
        print("=" * 70)
        print(
            "ATLAS CASTLE GEOMETRY CLASSIFIER "
            f"v{AtlasCastleGeometryClassifier.VERSION}"
        )
        print("=" * 70)
        print(f"Input castles             : " f"{len(castles)}")
        print(f"Input wall records        : " f"{len(castle_walls)}")
        print(f"Shell relations           : " f"{len(result['shell_castles'])}")
        print(
            f"Independent wall records  : " f"{len(result['independent_castle_walls'])}"
        )
        print(f"Relation wall records     : " f"{len(result['relation_castle_walls'])}")
        print(
            f"Inferred perimeter walls  : " f"{len(result['inferred_perimeter_walls'])}"
        )
        print(f"Unknown castle records    : " f"{len(result['unknown_castles'])}")
        print("=" * 70)
        print("")
