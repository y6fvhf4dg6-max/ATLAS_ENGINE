# CORE/atlas_building_part_hierarchy_profiler.py

"""
ATLAS Engine

Atlas Building Part Hierarchy Profiler v0.1

OSM building=* dış sınırları ile building:part=* geometrileri
arasındaki parent-child ilişkisini belirler.

Bu sınıf yalnızca analiz yapar.
Herhangi bir bina kaydını mesh üretiminden çıkarmaz.
"""

from shapely.geometry import (
    GeometryCollection,
    MultiPolygon,
    Polygon,
)
from shapely.ops import triangulate

from CORE.atlas_minaret_component_profiler import (
    AtlasMinaretComponentProfiler,
)


class AtlasBuildingPartHierarchyProfiler:
    """
    Genel building / building:part hiyerarşi analizcisi.
    """

    CONTAINMENT_RATIO_MINIMUM = 0.999
    BOUNDARY_OVERLAP_RATIO_MINIMUM = 0.50

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

                is_contained = (
                    containment_ratio
                    >= AtlasBuildingPartHierarchyProfiler
                    .CONTAINMENT_RATIO_MINIMUM
                )

                is_boundary_overlap = (
                    containment_ratio
                    >= AtlasBuildingPartHierarchyProfiler
                    .BOUNDARY_OVERLAP_RATIO_MINIMUM
                )

                if not (
                    is_contained
                    or is_boundary_overlap
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

        attached_minaret_component_ids = set()
        minaret_component_to_minaret = {}
        minaret_components_by_minaret = {}

        for parent_data in parents.values():
            minaret_result = (
                AtlasMinaretComponentProfiler.analyze(
                    parent_data["parts"]
                )
            )

            attached_minaret_component_ids.update(
                minaret_result[
                    "attached_component_ids"
                ]
            )

            minaret_component_to_minaret.update(
                minaret_result[
                    "component_to_minaret"
                ]
            )

            for (
                minaret_id,
                component_records,
            ) in minaret_result[
                "components_by_minaret"
            ].items():
                if not component_records:
                    continue

                minaret_components_by_minaret[
                    minaret_id
                ] = list(component_records)

        parent_metrics = {}
        suppression_candidate_ids = set()
        residual_replacement_parent_ids = set()
        residual_parent_records = []

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
            )

            should_create_residual = bool(
                repeated_detail_decomposition
                and not full_decomposition
                and coverage_ratio
                < AtlasBuildingPartHierarchyProfiler
                .FULL_DECOMPOSITION_COVERAGE_MINIMUM
            )

            residual_record_count = 0

            if should_create_residual:
                residual_geometry = (
                    parent_polygon.difference(
                        part_union
                    )
                )

                new_residual_records = (
                    AtlasBuildingPartHierarchyProfiler
                    ._make_residual_parent_records(
                        parent_id=parent_id,
                        parent_record=parent_data["parent"],
                        part_records=parent_data["parts"],
                        residual_geometry=residual_geometry,
                    )
                )

                if new_residual_records:
                    residual_parent_records.extend(
                        new_residual_records
                    )
                    residual_replacement_parent_ids.add(
                        parent_id
                    )
                    residual_record_count = len(
                        new_residual_records
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
                "should_create_residual": (
                    should_create_residual
                ),
                "residual_record_count": (
                    residual_record_count
                ),
                "residual_height_m": (
                    AtlasBuildingPartHierarchyProfiler
                    ._resolve_residual_height(
                        parent_data["parts"]
                    )[0]
                    if should_create_residual
                    else None
                ),
                "residual_height_source": (
                    AtlasBuildingPartHierarchyProfiler
                    ._resolve_residual_height(
                        parent_data["parts"]
                    )[1]
                    if should_create_residual
                    else None
                ),
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
                and (
                    record_id in suppression_candidate_ids
                    or record_id
                    in residual_replacement_parent_ids
                )
            ):
                continue

            if (
                is_building_part
                and record_id
                in attached_minaret_component_ids
            ):
                continue

            mesh_buildings.append(record)

        mesh_buildings.extend(
            residual_parent_records
        )

        return {
            "main_buildings": main_buildings,
            "building_parts": building_parts,
            "mesh_buildings": mesh_buildings,
            "parent_metrics": parent_metrics,
            "suppressed_parent_ids": sorted(
                suppression_candidate_ids
            ),
            "residual_replacement_parent_ids": sorted(
                residual_replacement_parent_ids
            ),
            "residual_parent_records": (
                residual_parent_records
            ),
            "attached_minaret_component_ids": sorted(
                attached_minaret_component_ids
            ),
            "minaret_component_to_minaret": (
                minaret_component_to_minaret
            ),
            "minaret_components_by_minaret": (
                minaret_components_by_minaret
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
                "residual_replacement_parent_count": len(
                    residual_replacement_parent_ids
                ),
                "residual_parent_record_count": len(
                    residual_parent_records
                ),
                "mesh_building_count": len(
                    mesh_buildings
                ),
                "attached_minaret_component_count": len(
                    attached_minaret_component_ids
                ),
                "minaret_with_component_count": len(
                    minaret_components_by_minaret
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
    def _resolve_residual_height(
        part_records,
    ):
        min_heights = []
        heights = []

        for record in part_records or []:
            tags = record.get("tags", {})

            min_height = (
                AtlasBuildingPartHierarchyProfiler
                ._read_positive_float(
                    tags.get("min_height")
                )
            )

            height = (
                AtlasBuildingPartHierarchyProfiler
                ._read_positive_float(
                    tags.get("height")
                )
            )

            if min_height is not None:
                min_heights.append(min_height)

            if height is not None:
                heights.append(height)

        if min_heights:
            return (
                min(min_heights),
                "minimum_part_min_height",
            )

        if heights:
            return (
                min(heights),
                "minimum_part_height",
            )

        return (
            3.0,
            "default_low_base_height",
        )

    @staticmethod
    def _read_positive_float(value):
        if value is None:
            return None

        try:
            parsed = float(
                str(value)
                .replace("m", "")
                .strip()
            )
        except (TypeError, ValueError):
            return None

        if parsed <= 0.0:
            return None

        return parsed

    @staticmethod
    def _make_residual_parent_records(
        parent_id,
        parent_record,
        part_records,
        residual_geometry,
    ):
        polygons = (
            AtlasBuildingPartHierarchyProfiler
            ._extract_residual_polygons(
                residual_geometry
            )
        )

        records = []

        for index, polygon in enumerate(polygons):
            if polygon.is_empty or polygon.area <= 0.0:
                continue

            coordinates = [
                (
                    float(lat),
                    float(lon),
                )
                for lon, lat in list(
                    polygon.exterior.coords
                )[:-1]
            ]

            if len(coordinates) < 3:
                continue

            residual_height_m, residual_height_source = (
                AtlasBuildingPartHierarchyProfiler
                ._resolve_residual_height(
                    part_records
                )
            )

            tags = dict(
                parent_record.get(
                    "tags",
                    {},
                )
            )

            for key in (
                "min_height",
                "building:min_level",
                "building:levels",
                "roof:height",
                "roof:levels",
                "roof:shape",
            ):
                tags.pop(key, None)

            tags["height"] = str(
                float(residual_height_m)
            )
            tags["atlas:residual_parent"] = "yes"
            tags["atlas:residual_height_source"] = (
                residual_height_source
            )

            records.append(
                {
                    **parent_record,
                    "id": (
                        f"atlas_residual_parent_"
                        f"{parent_id}_{index}"
                    ),
                    "geometry": coordinates,
                    "geometry_type": (
                        "residual_parent"
                    ),
                    "source_parent_id": parent_id,
                    "tags": tags,
                }
            )

        return records

    @staticmethod
    def _extract_residual_polygons(
        geometry,
    ):
        if geometry is None or geometry.is_empty:
            return []

        if isinstance(geometry, Polygon):
            if not geometry.interiors:
                return [geometry]

            return (
                AtlasBuildingPartHierarchyProfiler
                ._triangulate_residual_polygon(
                    geometry
                )
            )

        if isinstance(geometry, MultiPolygon):
            polygons = []

            for polygon in geometry.geoms:
                polygons.extend(
                    AtlasBuildingPartHierarchyProfiler
                    ._extract_residual_polygons(
                        polygon
                    )
                )

            return polygons

        if isinstance(geometry, GeometryCollection):
            polygons = []

            for item in geometry.geoms:
                polygons.extend(
                    AtlasBuildingPartHierarchyProfiler
                    ._extract_residual_polygons(
                        item
                    )
                )

            return polygons

        return []

    @staticmethod
    def _triangulate_residual_polygon(
        polygon,
    ):
        result = []

        for triangle in triangulate(polygon):
            clipped = triangle.intersection(
                polygon
            )

            if clipped.is_empty:
                continue

            if isinstance(clipped, Polygon):
                if clipped.area > 0.0:
                    result.append(clipped)

            elif isinstance(clipped, MultiPolygon):
                result.extend(
                    item
                    for item in clipped.geoms
                    if item.area > 0.0
                )

        return result

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
