"""
ATLAS Minaret Component Profiler v0.1

Aynı parent yapı içindeki minare gövdeleri ile yükseltilmiş
şerefe/parapet halkalarını ilişkilendirir.

Bu sınıf yalnızca analiz yapar.
Mesh üretmez.
"""

from math import cos, hypot, radians


class AtlasMinaretComponentProfiler:
    MAX_CENTER_DISTANCE_M = 2.0
    MAX_VERTICAL_THICKNESS_M = 4.0

    @staticmethod
    def analyze(records):
        records = list(records or [])

        minarets = [
            record
            for record in records
            if (
                record.get("tags", {})
                .get("tower:type")
                == "minaret"
            )
        ]

        component_candidates = [
            record
            for record in records
            if (
                AtlasMinaretComponentProfiler
                ._is_component_candidate(
                    record
                )
            )
        ]

        component_to_minaret = {}
        components_by_minaret = {
            record.get("id"): []
            for record in minarets
        }
        attached_component_ids = []
        unassigned_component_ids = []

        for component in component_candidates:
            component_center = (
                AtlasMinaretComponentProfiler
                ._centroid(
                    component
                )
            )

            best_minaret = None
            best_distance_m = None

            for minaret in minarets:
                minaret_center = (
                    AtlasMinaretComponentProfiler
                    ._centroid(
                        minaret
                    )
                )

                distance_m = (
                    AtlasMinaretComponentProfiler
                    ._distance_m(
                        component_center,
                        minaret_center,
                    )
                )

                if (
                    best_minaret is None
                    or distance_m < best_distance_m
                ):
                    best_minaret = minaret
                    best_distance_m = distance_m

            component_id = component.get("id")

            if (
                best_minaret is None
                or best_distance_m
                > AtlasMinaretComponentProfiler
                .MAX_CENTER_DISTANCE_M
            ):
                unassigned_component_ids.append(
                    component_id
                )
                continue

            minaret_id = best_minaret.get("id")

            height_m = (
                AtlasMinaretComponentProfiler
                ._read_float(
                    component.get(
                        "tags",
                        {},
                    ).get("height")
                )
            )

            min_height_m = (
                AtlasMinaretComponentProfiler
                ._read_float(
                    component.get(
                        "tags",
                        {},
                    ).get("min_height")
                )
            )

            vertical_thickness_m = (
                height_m - min_height_m
            )

            component_info = {
                **component,
                "component_type": "balcony_ring",
                "center_distance_m": best_distance_m,
                "vertical_thickness_m": (
                    vertical_thickness_m
                ),
                "minaret_id": minaret_id,
            }

            component_to_minaret[
                component_id
            ] = minaret_id

            components_by_minaret[
                minaret_id
            ].append(
                component_info
            )

            attached_component_ids.append(
                component_id
            )

        return {
            "minaret_ids": sorted(
                record.get("id")
                for record in minarets
            ),
            "component_to_minaret": (
                component_to_minaret
            ),
            "components_by_minaret": (
                components_by_minaret
            ),
            "attached_component_ids": sorted(
                attached_component_ids
            ),
            "unassigned_component_ids": sorted(
                unassigned_component_ids
            ),
        }

    @staticmethod
    def _is_component_candidate(
        record,
    ):
        tags = record.get("tags", {})

        if tags.get("building:part") is None:
            return False

        if tags.get("barrier") != "wall":
            return False

        height_m = (
            AtlasMinaretComponentProfiler
            ._read_float(
                tags.get("height")
            )
        )

        min_height_m = (
            AtlasMinaretComponentProfiler
            ._read_float(
                tags.get("min_height")
            )
        )

        if (
            height_m is None
            or min_height_m is None
            or min_height_m <= 0.0
            or height_m <= min_height_m
        ):
            return False

        vertical_thickness_m = (
            height_m - min_height_m
        )

        return (
            vertical_thickness_m
            <= AtlasMinaretComponentProfiler
            .MAX_VERTICAL_THICKNESS_M
        )

    @staticmethod
    def _centroid(record):
        geometry = record.get(
            "geometry",
            [],
        )

        if not geometry:
            return (
                0.0,
                0.0,
            )

        return (
            sum(
                float(point[0])
                for point in geometry
            )
            / len(geometry),
            sum(
                float(point[1])
                for point in geometry
            )
            / len(geometry),
        )

    @staticmethod
    def _distance_m(
        first,
        second,
    ):
        mean_lat = (
            float(first[0])
            + float(second[0])
        ) / 2.0

        dy = (
            float(first[0])
            - float(second[0])
        ) * 111_320.0

        dx = (
            float(first[1])
            - float(second[1])
        ) * 111_320.0 * cos(
            radians(mean_lat)
        )

        return hypot(
            dx,
            dy,
        )

    @staticmethod
    def _read_float(value):
        if value is None:
            return None

        try:
            return float(
                str(value)
                .replace("m", "")
                .strip()
            )
        except (
            TypeError,
            ValueError,
        ):
            return None
