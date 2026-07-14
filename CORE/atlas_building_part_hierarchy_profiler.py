# CORE/atlas_building_part_hierarchy_profiler.py

"""
ATLAS Engine

Atlas Building Part Hierarchy Profiler v0.1

OSM building=* dış sınırları ile building:part=* geometrileri
arasındaki parent-child ilişkisini belirler.

Bu sınıf yalnızca analiz yapar.
Herhangi bir bina kaydını mesh üretiminden çıkarmaz.
"""

from shapely.geometry import Polygon


class AtlasBuildingPartHierarchyProfiler:
    """
    Genel building / building:part hiyerarşi analizcisi.
    """

    CONTAINMENT_RATIO_MINIMUM = 0.999

    FULL_DECOMPOSITION_COVERAGE_MINIMUM = 0.95
    FULL_DECOMPOSITION_PART_COUNT_MINIMUM = 2

    REPEATED_DETAIL_PART_COUNT_MINIMUM = 8
    REPEATED_SMALL_PART_COUNT_MINIMUM = 8
    SMALL_PART_PARENT_AREA_RATIO_MAXIMUM = 0.01

    @staticmethod
    def analyze(raw_buildings):
        """
        Ham bina kayıtları arasındaki parent-child ilişkilerini döndürür.

        Returns:
            {
                "main_buildings": [...],
                "building_parts": [...],
                "parents": {
                    parent_id: {
                        "parent": raw_parent_record,
                        "parts": [raw_part_record, ...],
                        "part_ids": [...],
                    }
                },
                "part_to_parent": {
                    part_id: parent_id,
                },
                "unassigned_part_ids": [...],
                "summary": {...},
            }
        """

        raw_buildings = list(raw_buildings or [])

        main_buildings = []
        building_parts = []

        for record in raw_buildings:
            tags = record.get("tags", {})

            if tags.get("building:part") is not None:
                building_parts.append(record)

            if (
                tags.get("building") is not None
                and tags.get("building:part") is None
            ):
                main_buildings.append(record)

        main_polygon_items = []

        for record in main_buildings:
            polygon = AtlasBuildingPartHierarchyProfiler._make_polygon(
                record
            )

            if polygon is None:
                continue

            main_polygon_items.append(
                {
                    "record": record,
                    "polygon": polygon,
                }
            )

        parents = {}
        part_to_parent = {}
        unassigned_part_ids = []

        for part_record in building_parts:
            part_id = part_record.get("id")

            part_polygon = (
                AtlasBuildingPartHierarchyProfiler._make_polygon(
                    part_record
                )
            )

            if part_polygon is None:
                unassigned_part_ids.append(part_id)
                continue

            best_parent_item = None
            best_parent_area = None

            for parent_item in main_polygon_items:
                parent_polygon = parent_item["polygon"]

                intersection = parent_polygon.intersection(
                    part_polygon
                )

                if intersection.is_empty:
                    continue

                containment_ratio = (
                    intersection.area / part_polygon.area
                )

                if (
                    containment_ratio
                    < AtlasBuildingPartHierarchyProfiler
                    .CONTAINMENT_RATIO_MINIMUM
                ):
                    continue

                parent_area = parent_polygon.area

                # Birden fazla parent containment varsa en küçük
                # kapsayıcı footprint en yakın parent kabul edilir.
                if (
                    best_parent_item is None
                    or parent_area < best_parent_area
                ):
                    best_parent_item = parent_item
                    best_parent_area = parent_area

            if best_parent_item is None:
                unassigned_part_ids.append(part_id)
                continue

            parent_record = best_parent_item["record"]
            parent_id = parent_record.get("id")

            if parent_id not in parents:
                parents[parent_id] = {
                    "parent": parent_record,
                    "parts": [],
                    "part_ids": [],
                }

            parents[parent_id]["parts"].append(
                part_record
            )
            parents[parent_id]["part_ids"].append(
                part_id
            )

            part_to_parent[part_id] = parent_id

        parent_part_counts = {
            parent_id: len(parent_data["parts"])
            for parent_id, parent_data in parents.items()
        }

        parent_metrics = {}
        suppression_candidate_ids = set()

        for parent_id, parent_data in parents.items():
            parent_polygon = (
                AtlasBuildingPartHierarchyProfiler._make_polygon(
                    parent_data["parent"]
                )
            )

            part_polygons = []

            for part_record in parent_data["parts"]:
                part_polygon = (
                    AtlasBuildingPartHierarchyProfiler._make_polygon(
                        part_record
                    )
                )

                if part_polygon is not None:
                    part_polygons.append(part_polygon)

            if (
                parent_polygon is None
                or not part_polygons
                or parent_polygon.area <= 0.0
            ):
                continue

            part_union = part_polygons[0]

            for part_polygon in part_polygons[1:]:
                part_union = part_union.union(part_polygon)

            coverage_ratio = (
                part_union.area / parent_polygon.area
            )

            small_part_count = sum(
                (
                    part_polygon.area
                    / parent_polygon.area
                )
                <= AtlasBuildingPartHierarchyProfiler
                .SMALL_PART_PARENT_AREA_RATIO_MAXIMUM
                for part_polygon in part_polygons
            )

            part_count = len(part_polygons)

            full_decomposition = (
                part_count
                >= AtlasBuildingPartHierarchyProfiler
                .FULL_DECOMPOSITION_PART_COUNT_MINIMUM
                and coverage_ratio
                >= AtlasBuildingPartHierarchyProfiler
                .FULL_DECOMPOSITION_COVERAGE_MINIMUM
            )

            repeated_detail_decomposition = (
                part_count
                >= AtlasBuildingPartHierarchyProfiler
                .REPEATED_DETAIL_PART_COUNT_MINIMUM
                and small_part_count
                >= AtlasBuildingPartHierarchyProfiler
                .REPEATED_SMALL_PART_COUNT_MINIMUM
            )

            should_suppress = bool(
                full_decomposition
                or repeated_detail_decomposition
            )

            parent_metrics[parent_id] = {
                "part_count": part_count,
                "small_part_count": small_part_count,
                "coverage_ratio": coverage_ratio,
                "full_decomposition": full_decomposition,
                "repeated_detail_decomposition": (
                    repeated_detail_decomposition
                ),
                "should_suppress": should_suppress,
            }

            if should_suppress:
                suppression_candidate_ids.add(
                    parent_id
                )

        mesh_buildings = []

        for record in raw_buildings:
            record_id = record.get("id")
            tags = record.get("tags", {})

            is_building_part = (
                tags.get("building:part") is not None
            )

            if (
                not is_building_part
                and record_id in suppression_candidate_ids
            ):
                continue

            mesh_buildings.append(record)

        return {
            "main_buildings": main_buildings,
            "building_parts": building_parts,
            "mesh_buildings": mesh_buildings,
            "parent_metrics": parent_metrics,
            "suppressed_parent_ids": sorted(
                suppression_candidate_ids
            ),
            "parents": parents,
            "part_to_parent": part_to_parent,
            "unassigned_part_ids": unassigned_part_ids,
            "summary": {
                "raw_building_count": len(raw_buildings),
                "main_building_count": len(main_buildings),
                "building_part_count": len(building_parts),
                "parent_with_parts_count": len(parents),
                "suppressed_parent_count": len(
                    suppression_candidate_ids
                ),
                "mesh_building_count": len(
                    mesh_buildings
                ),
                "assigned_building_part_count": len(
                    part_to_parent
                ),
                "unassigned_building_part_count": len(
                    unassigned_part_ids
                ),
                "parent_part_counts": parent_part_counts,
            },
        }

    @staticmethod
    def _make_polygon(record):
        geometry = record.get(
            "geometry",
            [],
        )

        if len(geometry) < 3:
            return None

        polygon = Polygon(
            [
                (lon, lat)
                for lat, lon in geometry
            ]
        )

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty:
            return None

        if polygon.area <= 0.0:
            return None

        return polygon
