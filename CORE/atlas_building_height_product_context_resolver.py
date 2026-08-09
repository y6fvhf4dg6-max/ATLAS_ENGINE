from __future__ import annotations

import math

from CORE.atlas_scene_builder import (
    AtlasSceneBuilder,
)
from CORE.atlas_urban_block_resolver import (
    AtlasUrbanBlockResolver,
)


class AtlasBuildingHeightProductContextResolver:
    @staticmethod
    def _centroid(points):
        if not points:
            return None

        return (
            sum(point[0] for point in points)
            / len(points),
            sum(point[1] for point in points)
            / len(points),
        )

    @staticmethod
    def _semantic_importance(source):
        value = source.get(
            "semantic_importance",
            source.get(
                "product_priority",
                0.0,
            ),
        )

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                "building semantic importance must be numeric"
            )

        if (
            not math.isfinite(value)
            or not 0.0 <= value <= 1.0
        ):
            raise ValueError(
                "building semantic importance must be "
                "finite and within 0..1"
            )

        return value

    @staticmethod
    def _to_meter_geometry(
        geometry,
        coordinate_engine,
    ):
        return tuple(
            coordinate_engine.latlon_to_local_meters(
                lat,
                lon,
            )
            for lat, lon in geometry or ()
        )

    @classmethod
    def _prepare_buildings(
        cls,
        *,
        buildings,
        coordinate_engine,
    ):
        prepared = []
        source_height_by_id = {}

        for source in buildings or ():
            source_id = source.get("id")

            if source_id is None:
                continue

            atlas_building = (
                AtlasSceneBuilder._to_atlas_building(
                    source
                )
            )

            source_height_m = float(
                atlas_building.estimated_height
            )

            geometry_m = cls._to_meter_geometry(
                source.get(
                    "geometry",
                    (),
                ),
                coordinate_engine,
            )

            if len(geometry_m) < 3:
                continue

            centroid_m = cls._centroid(
                geometry_m
            )

            element_id = (
                f"building_{source_id}"
            )

            prepared.append(
                {
                    "element_id": element_id,
                    "source_id": source_id,
                    "centroid": centroid_m,
                    "footprint": geometry_m,
                    "semantic_class": (
                        "generic_building"
                    ),
                    "estimated_height_m": (
                        source_height_m
                    ),
                }
            )

            source_height_by_id[source_id] = (
                source_height_m
            )

        return (
            tuple(prepared),
            source_height_by_id,
        )

    @classmethod
    def _prepare_roads(
        cls,
        *,
        roads,
        coordinate_engine,
    ):
        prepared = []

        for road in roads or ():
            geometry_m = cls._to_meter_geometry(
                road.get(
                    "geometry",
                    (),
                ),
                coordinate_engine,
            )

            for index in range(
                len(geometry_m) - 1
            ):
                prepared.append(
                    {
                        "centerline": (
                            geometry_m[index],
                            geometry_m[
                                index + 1
                            ],
                        ),
                    }
                )

        return tuple(prepared)

    @classmethod
    def _prepare_landmarks(
        cls,
        *,
        landmarks,
        coordinate_engine,
    ):
        prepared = []

        for source in landmarks or ():
            geometry_m = cls._to_meter_geometry(
                source.get(
                    "geometry",
                    (),
                ),
                coordinate_engine,
            )

            centroid_m = cls._centroid(
                geometry_m
            )

            if centroid_m is None:
                continue

            prepared.append(
                {
                    "element_id": (
                        f"landmark_"
                        f"{source.get('id', len(prepared))}"
                    ),
                    "centroid": centroid_m,
                }
            )

        return tuple(prepared)

    @staticmethod
    def _nearest_landmark_distance(
        *,
        centroid,
        landmarks,
    ):
        if centroid is None:
            return None

        distances = [
            math.hypot(
                centroid[0]
                - landmark["centroid"][0],
                centroid[1]
                - landmark["centroid"][1],
            )
            for landmark in landmarks
            if landmark.get(
                "centroid"
            ) is not None
        ]

        return (
            min(distances)
            if distances
            else None
        )

    @classmethod
    def resolve(
        cls,
        *,
        buildings,
        roads,
        landmarks,
        coordinate_engine,
    ):
        if coordinate_engine is None:
            raise TypeError(
                "coordinate_engine is required"
            )

        (
            prepared_buildings,
            source_height_by_id,
        ) = cls._prepare_buildings(
            buildings=buildings,
            coordinate_engine=(
                coordinate_engine
            ),
        )

        prepared_landmarks = (
            cls._prepare_landmarks(
                landmarks=landmarks,
                coordinate_engine=(
                    coordinate_engine
                ),
            )
        )

        road_segments = cls._prepare_roads(
            roads=roads,
            coordinate_engine=(
                coordinate_engine
            ),
        )

        blocks = (
            AtlasUrbanBlockResolver
            .resolve_road_defined_blocks(
                road_segments=road_segments,
            )
        )

        profiles = (
            AtlasUrbanBlockResolver
            .resolve_exclusive_block_profiles(
                blocks=blocks,
                buildings=prepared_buildings,
                landmarks=prepared_landmarks,
            )
            if blocks
            else ()
        )

        profile_by_element_id = {}

        for profile in profiles:
            for element_id in (
                profile.member_element_ids
            ):
                profile_by_element_id[
                    element_id
                ] = profile

        source_by_id = {
            source.get("id"): source
            for source in buildings or ()
            if source.get("id") is not None
        }

        context = {}

        for building in prepared_buildings:
            source_id = building[
                "source_id"
            ]
            element_id = building[
                "element_id"
            ]
            source = source_by_id[
                source_id
            ]

            profile = (
                profile_by_element_id.get(
                    element_id
                )
            )

            landmark_distance_m = (
                cls._nearest_landmark_distance(
                    centroid=building.get(
                        "centroid"
                    ),
                    landmarks=prepared_landmarks,
                )
            )

            context[source_id] = {
                "source_height_m": (
                    source_height_by_id[
                        source_id
                    ]
                ),
                "block_median_height_m": (
                    None
                    if profile is None
                    else profile.median_height_m
                ),
                "landmark_distance_m": (
                    landmark_distance_m
                ),
                "semantic_importance": (
                    cls._semantic_importance(
                        source
                    )
                ),
            }

        return context
