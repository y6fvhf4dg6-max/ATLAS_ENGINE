from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median

from shapely.geometry import LineString, MultiLineString, Point, Polygon

from CORE.atlas_lod_level_catalog import AtlasLoDLevel
from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricElement,
    AtlasUrbanFabricRelationship,
    AtlasUrbanFabricScene,
)
from shapely.ops import linemerge, polygonize, unary_union




@dataclass(frozen=True, slots=True)
class AtlasUrbanBlockProfile:
    block_id: str
    member_element_ids: tuple[str, ...]
    density_ratio: float = 0.0
    median_height_m: float | None = None
    nearest_landmark_distance: float | None = None
    composition_lod_level: AtlasLoDLevel | None = None
    shared_boundary_length: float = 0.0
    courtyard_count: int = 0

    def __post_init__(self):
        block_id = "_".join(
            str(self.block_id).strip().lower().split()
        )

        if not block_id:
            raise ValueError(
                "block_id must not be empty"
            )

        member_element_ids = tuple(
            "_".join(
                str(value).strip().lower().split()
            )
            for value in self.member_element_ids
        )

        if any(not value for value in member_element_ids):
            raise ValueError(
                "member_element_ids must not contain empty values"
            )

        if len(member_element_ids) != len(set(member_element_ids)):
            raise ValueError(
                "member_element_ids must contain unique values"
            )

        density_ratio = float(self.density_ratio)

        if not 0.0 <= density_ratio <= 1.0:
            raise ValueError(
                "density_ratio must be within 0.0..1.0"
            )

        median_height_m = self.median_height_m

        if median_height_m is not None:
            median_height_m = float(median_height_m)

            if not math.isfinite(median_height_m):
                raise ValueError(
                    "median_height_m must be finite"
                )

            if median_height_m < 0.0:
                raise ValueError(
                    "median_height_m must not be negative"
                )

        object.__setattr__(self, "block_id", block_id)
        object.__setattr__(
            self,
            "median_height_m",
            median_height_m,
        )

        nearest_landmark_distance = self.nearest_landmark_distance

        if nearest_landmark_distance is not None:
            nearest_landmark_distance = float(
                nearest_landmark_distance
            )

            if not math.isfinite(nearest_landmark_distance):
                raise ValueError(
                    "nearest_landmark_distance must be finite"
                )

            if nearest_landmark_distance < 0.0:
                raise ValueError(
                    "nearest_landmark_distance must not be negative"
                )

        object.__setattr__(
            self,
            "nearest_landmark_distance",
            nearest_landmark_distance,
        )

        if (
            self.composition_lod_level is not None
            and not isinstance(
                self.composition_lod_level,
                AtlasLoDLevel,
            )
        ):
            raise TypeError(
                "composition_lod_level must be an AtlasLoDLevel"
            )

        shared_boundary_length = float(
            self.shared_boundary_length
        )

        if (
            not math.isfinite(shared_boundary_length)
            or shared_boundary_length < 0.0
        ):
            raise ValueError(
                "shared_boundary_length must be finite and non-negative"
            )

        object.__setattr__(
            self,
            "shared_boundary_length",
            shared_boundary_length,
        )

        courtyard_count = self.courtyard_count

        if (
            isinstance(courtyard_count, bool)
            or not isinstance(courtyard_count, int)
            or courtyard_count < 0
        ):
            raise ValueError(
                "courtyard_count must be a non-negative integer"
            )

        object.__setattr__(
            self,
            "courtyard_count",
            courtyard_count,
        )
        object.__setattr__(self, "density_ratio", density_ratio)
        object.__setattr__(
            self,
            "member_element_ids",
            member_element_ids,
        )


class AtlasUrbanBlockResolver:

    @classmethod
    def integrate_profiles_into_scene(
        cls,
        *,
        scene,
        profiles,
    ) -> AtlasUrbanFabricScene:
        result = scene

        for profile in profiles:
            result = cls.integrate_profile_into_scene(
                scene=result,
                profile=profile,
            )

        return result

    @classmethod
    def integrate_profile_into_scene(
        cls,
        *,
        scene,
        profile,
    ) -> AtlasUrbanFabricScene:
        if not isinstance(scene, AtlasUrbanFabricScene):
            raise TypeError(
                "scene must be an AtlasUrbanFabricScene"
            )

        if not isinstance(profile, AtlasUrbanBlockProfile):
            raise TypeError(
                "profile must be an AtlasUrbanBlockProfile"
            )

        block_element = AtlasUrbanFabricElement(
            element_id=profile.block_id,
            semantic_class="urban_block",
            related_element_ids=profile.member_element_ids,
        )

        relationships = list(scene.relationships)

        for member_element_id in profile.member_element_ids:
            relationships.append(
                AtlasUrbanFabricRelationship(
                    relationship_id=(
                        f"{profile.block_id}_contains_{member_element_id}"
                    ),
                    relation_type="contains_building",
                    source_element_id=profile.block_id,
                    target_element_id=member_element_id,
                )
            )

        return AtlasUrbanFabricScene(
            elements=(
                *scene.elements,
                block_element,
            ),
            relationships=tuple(relationships),
        )

    @classmethod
    def resolve_road_defined_blocks(
        cls,
        *,
        road_segments,
    ) -> tuple[dict, ...]:
        lines = []

        for segment in road_segments:
            centerline = segment.get("centerline", ())

            if len(centerline) != 2:
                continue

            lines.append(
                LineString(centerline)
            )

        if not lines:
            return ()

        unioned = unary_union(lines)

        if isinstance(unioned, LineString):
            merged_lines = [unioned]
        else:
            merged = linemerge(
                unioned
            )

            if isinstance(merged, LineString):
                merged_lines = [merged]
            elif isinstance(merged, MultiLineString):
                merged_lines = list(merged.geoms)
            else:
                merged_lines = lines

        polygons = list(
            polygonize(merged_lines)
        )

        blocks = []

        for index, polygon in enumerate(polygons, start=1):
            coordinates = list(
                polygon.exterior.coords
            )

            if (
                len(coordinates) >= 2
                and coordinates[0] == coordinates[-1]
            ):
                coordinates.pop()

            if len(coordinates) < 3:
                continue

            blocks.append(
                {
                    "block_id": f"road_block_{index}",
                    "polygon": tuple(
                        (
                            float(x),
                            float(y),
                        )
                        for x, y in coordinates
                    ),
                }
            )

        return tuple(blocks)

    @staticmethod
    def _point_inside_polygon(
        point,
        polygon,
    ) -> bool:
        lat, lon = point

        inside = False
        previous_index = len(polygon) - 1

        for current_index in range(len(polygon)):
            current_lat, current_lon = polygon[current_index]
            previous_lat, previous_lon = polygon[previous_index]

            crosses_latitude = (
                (current_lat > lat)
                != (previous_lat > lat)
            )

            if crosses_latitude:
                intersection_lon = (
                    (previous_lon - current_lon)
                    * (lat - current_lat)
                    / (previous_lat - current_lat)
                    + current_lon
                )

                if lon < intersection_lon:
                    inside = not inside

            previous_index = current_index

        return inside

    @classmethod
    def resolve_exclusive_block_profiles(
        cls,
        *,
        blocks,
        buildings,
        landmarks=(),
        composition_lod_level=None,
    ) -> tuple[AtlasUrbanBlockProfile, ...]:
        assignments = {
            "_".join(
                str(block["block_id"]).strip().lower().split()
            ): []
            for block in blocks
        }

        block_shapes = {
            "_".join(
                str(block["block_id"]).strip().lower().split()
            ): Polygon(block["polygon"])
            for block in blocks
        }

        for building in buildings:
            if building.get("semantic_class") != "generic_building":
                continue

            footprint = building.get("footprint")
            candidates = []

            if footprint is not None and len(footprint) >= 3:
                footprint_shape = Polygon(footprint)

                if footprint_shape.is_valid and footprint_shape.area > 0.0:
                    for block_id, block_shape in block_shapes.items():
                        overlap_area = block_shape.intersection(
                            footprint_shape
                        ).area

                        if overlap_area > 0.0:
                            candidates.append(
                                (
                                    overlap_area,
                                    block_id,
                                )
                            )

            if not candidates:
                centroid = building.get("centroid")

                if centroid is None or len(centroid) != 2:
                    continue

                for block_id, block_shape in block_shapes.items():
                    if block_shape.contains(
                        Point(centroid)
                    ):
                        candidates.append(
                            (
                                0.0,
                                block_id,
                            )
                        )

            if not candidates:
                continue

            _, winning_block_id = sorted(
                candidates,
                key=lambda item: (
                    -item[0],
                    item[1],
                ),
            )[0]

            assignments[winning_block_id].append(
                building
            )

        profiles = []

        for block in blocks:
            block_id = "_".join(
                str(block["block_id"]).strip().lower().split()
            )

            profiles.append(
                cls.resolve_block_profile(
                    block_id=block["block_id"],
                    block_polygon=block["polygon"],
                    buildings=tuple(
                        assignments[block_id]
                    ),
                    landmarks=landmarks,
                    composition_lod_level=composition_lod_level,
                )
            )

        return tuple(profiles)

    @classmethod
    def resolve_block_profiles(
        cls,
        *,
        blocks,
        buildings,
        landmarks=(),
        composition_lod_level=None,
    ) -> tuple[AtlasUrbanBlockProfile, ...]:
        profiles = []
        normalized_block_ids = set()

        for block in blocks:
            normalized_block_id = "_".join(
                str(block["block_id"]).strip().lower().split()
            )

            if normalized_block_id in normalized_block_ids:
                raise ValueError(
                    "blocks must have unique block_id values"
                )

            normalized_block_ids.add(
                normalized_block_id
            )
            profiles.append(
                cls.resolve_block_profile(
                    block_id=block["block_id"],
                    block_polygon=block["polygon"],
                    buildings=buildings,
                    landmarks=landmarks,
                    composition_lod_level=composition_lod_level,
                )
            )

        return tuple(profiles)

    @classmethod
    def resolve_block_profile(
        cls,
        *,
        block_id,
        block_polygon,
        buildings,
        landmarks=(),
        composition_lod_level=None,
    ) -> AtlasUrbanBlockProfile:
        members = cls.resolve_block_members(
            block_id=block_id,
            block_polygon=block_polygon,
            buildings=buildings,
        )

        block_shape = Polygon(block_polygon)
        member_set = set(members)
        footprint_shapes = []

        for building in buildings:
            if building.get("element_id") not in member_set:
                continue

            footprint = building.get("footprint")
            if footprint is None or len(footprint) < 3:
                continue

            inner_geometries = building.get(
                "inner_geometries",
                (),
            )

            shape = Polygon(
                footprint,
                holes=inner_geometries,
            )

            if shape.is_valid and shape.area > 0.0:
                footprint_shapes.append(
                    shape.intersection(block_shape)
                )

        covered_area = (
            unary_union(footprint_shapes).area
            if footprint_shapes
            else 0.0
        )

        member_heights = []

        for building in buildings:
            if building.get("element_id") not in member_set:
                continue

            value = building.get("estimated_height_m")
            if value is None:
                continue

            try:
                value = float(value)
            except (TypeError, ValueError):
                continue

            if not math.isfinite(value):
                continue

            if value > 0.0:
                member_heights.append(value)

        block_centroid = block_shape.centroid
        landmark_distances = []

        for landmark in landmarks:
            centroid = landmark.get("centroid")
            if centroid is None or len(centroid) != 2:
                continue

            try:
                x = float(centroid[0])
                y = float(centroid[1])
            except (TypeError, ValueError):
                continue

            if not math.isfinite(x) or not math.isfinite(y):
                continue

            distance = math.hypot(
                x - block_centroid.x,
                y - block_centroid.y,
            )
            landmark_distances.append(distance)

        member_footprints = []

        for building in buildings:
            if building.get("element_id") not in member_set:
                continue

            footprint = building.get("footprint")
            if footprint is None or len(footprint) < 3:
                continue

            shape = Polygon(footprint)

            if shape.is_valid and shape.area > 0.0:
                member_footprints.append(shape)

        shared_boundary_length = 0.0

        for first_index, first_shape in enumerate(member_footprints):
            for second_shape in member_footprints[first_index + 1:]:
                shared = first_shape.boundary.intersection(
                    second_shape.boundary
                )

                if not shared.is_empty and shared.length > 0.0:
                    shared_boundary_length += shared.length

        courtyard_count = 0

        for building in buildings:
            if building.get("element_id") not in member_set:
                continue

            for inner_geometry in building.get(
                "inner_geometries",
                (),
            ):
                if len(inner_geometry) < 3:
                    continue

                courtyard_shape = Polygon(inner_geometry)

                if (
                    courtyard_shape.is_valid
                    and courtyard_shape.area > 0.0
                ):
                    courtyard_count += 1

        return AtlasUrbanBlockProfile(
            block_id=block_id,
            member_element_ids=members,
            density_ratio=covered_area / block_shape.area,
            median_height_m=(
                median(member_heights)
                if member_heights
                else None
            ),
            nearest_landmark_distance=(
                min(landmark_distances)
                if landmark_distances
                else None
            ),
            composition_lod_level=composition_lod_level,
            shared_boundary_length=shared_boundary_length,
            courtyard_count=courtyard_count,
        )

    @classmethod
    def resolve_block_members(
        cls,
        *,
        block_id,
        block_polygon,
        buildings,
    ) -> tuple[str, ...]:
        del block_id

        if len(block_polygon) < 3:
            raise ValueError(
                "block_polygon must contain at least 3 points"
            )

        block_shape = Polygon(block_polygon)

        if not block_shape.is_valid or block_shape.area <= 0.0:
            raise ValueError(
                "block_polygon must define a valid positive-area polygon"
            )

        members = []

        for building in buildings:
            if building.get("semantic_class") != "generic_building":
                continue

            centroid = building.get("centroid")
            if centroid is None:
                continue

            centroid_inside = cls._point_inside_polygon(
                centroid,
                block_polygon,
            )

            footprint_overlap = False
            footprint = building.get("footprint")

            if footprint is not None and len(footprint) >= 3:
                footprint_shape = Polygon(footprint)

                if footprint_shape.is_valid:
                    footprint_overlap = (
                        block_shape.intersection(
                            footprint_shape
                        ).area > 0.0
                    )

            if centroid_inside or footprint_overlap:
                members.append(
                    building["element_id"]
                )

        return tuple(members)
