from __future__ import annotations

import math

from shapely.geometry import Point, Polygon

from CORE.atlas_mosque_landmark_builder import (
    AtlasMosqueLandmarkGeometry,
)
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasMosqueLandmarkMesher:
    RADIAL_SEGMENTS = 16
    DOME_RING_LEVELS = 5

    @staticmethod
    def _signed_area(footprint):
        return sum(
            (
                footprint[index][0]
                * footprint[
                    (index + 1) % len(footprint)
                ][1]
                - footprint[
                    (index + 1) % len(footprint)
                ][0]
                * footprint[index][1]
            )
            for index in range(len(footprint))
        ) / 2.0

    @classmethod
    def _extrude_footprint(
        cls,
        *,
        footprint,
        bottom_z,
        top_z,
        mesh_type,
        **metadata,
    ):
        footprint = tuple(
            (
                float(x),
                float(y),
            )
            for x, y in footprint
        )

        minimum_x = min(
            x
            for x, _ in footprint
        )
        minimum_y = min(
            y
            for _, y in footprint
        )

        span_x = (
            max(x for x, _ in footprint)
            - minimum_x
        )
        span_y = (
            max(y for _, y in footprint)
            - minimum_y
        )
        normalization_scale = max(
            span_x,
            span_y,
        )

        if normalization_scale <= 1e-15:
            raise ValueError(
                "Mosque footprint has no span"
            )

        normalized = tuple(
            (
                (x - minimum_x)
                / normalization_scale,
                (y - minimum_y)
                / normalization_scale,
            )
            for x, y in footprint
        )

        surface_triangles = tuple(
            tuple(
                (
                    minimum_x
                    + normalized_x
                    * normalization_scale,
                    minimum_y
                    + normalized_y
                    * normalization_scale,
                )
                for normalized_x, normalized_y
                in triangle
            )
            for triangle in (
                AtlasPolygonTriangulator.triangulate(
                    normalized
                )
            )
        )

        if not surface_triangles:
            raise ValueError(
                "Mosque footprint triangulation "
                "produced no surface"
            )

        bottom = tuple(
            (
                x,
                y,
                float(bottom_z),
            )
            for x, y in footprint
        )
        top = tuple(
            (
                x,
                y,
                float(top_z),
            )
            for x, y in footprint
        )

        triangles = []

        for triangle in surface_triangles:
            lower = tuple(
                (
                    x,
                    y,
                    float(bottom_z),
                )
                for x, y in triangle
            )
            upper = tuple(
                (
                    x,
                    y,
                    float(top_z),
                )
                for x, y in triangle
            )

            triangles.append(
                (
                    lower[0],
                    lower[2],
                    lower[1],
                )
            )
            triangles.append(
                (
                    upper[0],
                    upper[1],
                    upper[2],
                )
            )

        counterclockwise = (
            cls._signed_area(footprint) > 0.0
        )
        walls = []

        for index in range(len(footprint)):
            next_index = (
                index + 1
            ) % len(footprint)

            first_bottom = bottom[index]
            second_bottom = bottom[next_index]
            first_top = top[index]
            second_top = top[next_index]

            walls.append(
                (
                    first_bottom,
                    second_bottom,
                    second_top,
                    first_top,
                )
            )

            if counterclockwise:
                triangles.extend(
                    (
                        (
                            first_bottom,
                            second_bottom,
                            second_top,
                        ),
                        (
                            first_bottom,
                            second_top,
                            first_top,
                        ),
                    )
                )
            else:
                triangles.extend(
                    (
                        (
                            first_bottom,
                            second_top,
                            second_bottom,
                        ),
                        (
                            first_bottom,
                            first_top,
                            second_top,
                        ),
                    )
                )

        return {
            "type": mesh_type,
            "uses_real_footprint": True,
            "footprint": footprint,
            "bottom": bottom,
            "top": top,
            "bottom_z": float(bottom_z),
            "top_z": float(top_z),
            "walls": walls,
            "triangles": triangles,
            **metadata,
        }

    @staticmethod
    def _resolve_dome_system(
        *,
        footprint,
        desired_dome_radius,
        drum_radius_ratio,
        minimum_radius,
    ):
        polygon = Polygon(
            footprint
        )

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.area <= 1e-12
        ):
            raise ValueError(
                "Mosque footprint must define "
                "a valid polygon"
            )

        minimum_x, minimum_y, maximum_x, maximum_y = (
            polygon.bounds
        )

        candidates = [
            polygon.representative_point(),
            polygon.centroid,
        ]

        grid_steps = 30

        for x_index in range(grid_steps + 1):
            x = (
                minimum_x
                + (maximum_x - minimum_x)
                * x_index
                / grid_steps
            )

            for y_index in range(grid_steps + 1):
                y = (
                    minimum_y
                    + (maximum_y - minimum_y)
                    * y_index
                    / grid_steps
                )

                point = Point(
                    x,
                    y,
                )

                if polygon.covers(point):
                    candidates.append(point)

        valid_candidates = [
            point
            for point in candidates
            if polygon.covers(point)
        ]

        if not valid_candidates:
            raise ValueError(
                "Mosque footprint has no valid "
                "interior dome center"
            )

        center_point = max(
            valid_candidates,
            key=lambda point: point.distance(
                polygon.boundary
            ),
        )

        maximum_safe_radius = (
            center_point.distance(
                polygon.boundary
            )
            * 0.98
        )

        minimum_radius = float(
            minimum_radius
        )

        if maximum_safe_radius < minimum_radius:
            raise ValueError(
                "Mosque footprint cannot contain "
                "a printable dome system"
            )

        dome_radius = min(
            float(desired_dome_radius),
            maximum_safe_radius,
        )

        drum_radius = min(
            dome_radius
            * float(drum_radius_ratio),
            maximum_safe_radius,
        )

        return {
            "center_x": float(center_point.x),
            "center_y": float(center_point.y),
            "dome_radius": dome_radius,
            "drum_radius": drum_radius,
            "maximum_safe_radius": (
                maximum_safe_radius
            ),
        }

    @staticmethod
    def _resolve_minaret_center(
        *,
        footprint,
        target_x,
        target_y,
        clearance_radius,
    ):
        polygon = Polygon(
            footprint
        )

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.area <= 1e-12
        ):
            raise ValueError(
                "Mosque footprint must define "
                "a valid polygon"
            )

        clearance_radius = float(
            clearance_radius
        )

        if clearance_radius <= 0.0:
            raise ValueError(
                "clearance_radius must be positive"
            )

        safe_polygon = polygon.buffer(
            -clearance_radius
        )

        if (
            safe_polygon.is_empty
            or safe_polygon.area <= 1e-12
        ):
            safe_polygon = polygon

        safe_point = (
            safe_polygon.representative_point()
        )

        safe_x = float(
            safe_point.x
        )
        safe_y = float(
            safe_point.y
        )

        target_x = float(
            target_x
        )
        target_y = float(
            target_y
        )

        # Güvenli iç noktadan hedef mimari köşeye doğru
        # ilerleyerek polygon içinde kalan en dış merkezi seç.
        for step in range(95, -1, -1):
            progress = (
                step / 100.0
            )

            candidate_x = (
                safe_x
                + (target_x - safe_x)
                * progress
            )
            candidate_y = (
                safe_y
                + (target_y - safe_y)
                * progress
            )

            if safe_polygon.covers(
                Point(
                    candidate_x,
                    candidate_y,
                )
            ):
                return (
                    candidate_x,
                    candidate_y,
                )

        return (
            safe_x,
            safe_y,
        )

    @staticmethod
    def _ring(
        *,
        center_x,
        center_y,
        radius,
        z,
        segment_count,
    ):
        return tuple(
            (
                float(center_x)
                + float(radius)
                * math.cos(
                    2.0
                    * math.pi
                    * index
                    / segment_count
                ),
                float(center_y)
                + float(radius)
                * math.sin(
                    2.0
                    * math.pi
                    * index
                    / segment_count
                ),
                float(z),
            )
            for index in range(segment_count)
        )

    @staticmethod
    def _connect_rings(
        lower,
        upper,
    ):
        if len(lower) != len(upper):
            raise ValueError(
                "Connected rings must have equal point count"
            )

        triangles = []

        for index in range(len(lower)):
            next_index = (
                index + 1
            ) % len(lower)

            triangles.extend(
                (
                    (
                        lower[index],
                        lower[next_index],
                        upper[next_index],
                    ),
                    (
                        lower[index],
                        upper[next_index],
                        upper[index],
                    ),
                )
            )

        return triangles

    @staticmethod
    def _cap_ring(
        ring,
        *,
        reverse,
    ):
        center = (
            sum(point[0] for point in ring)
            / len(ring),
            sum(point[1] for point in ring)
            / len(ring),
            ring[0][2],
        )

        triangles = []

        for index in range(len(ring)):
            next_index = (
                index + 1
            ) % len(ring)

            if reverse:
                triangles.append(
                    (
                        center,
                        ring[next_index],
                        ring[index],
                    )
                )
            else:
                triangles.append(
                    (
                        center,
                        ring[index],
                        ring[next_index],
                    )
                )

        return triangles

    @classmethod
    def _closed_cylinder(
        cls,
        *,
        center_x,
        center_y,
        radius,
        bottom_z,
        top_z,
        mesh_type,
        **metadata,
    ):
        bottom = cls._ring(
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            z=bottom_z,
            segment_count=cls.RADIAL_SEGMENTS,
        )
        top = cls._ring(
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            z=top_z,
            segment_count=cls.RADIAL_SEGMENTS,
        )

        triangles = [
            *cls._cap_ring(
                bottom,
                reverse=True,
            ),
            *cls._connect_rings(
                bottom,
                top,
            ),
            *cls._cap_ring(
                top,
                reverse=False,
            ),
        ]

        return {
            "type": mesh_type,
            "center_x": float(center_x),
            "center_y": float(center_y),
            "radius": float(radius),
            "bottom": bottom,
            "top": top,
            "bottom_z": float(bottom_z),
            "top_z": float(top_z),
            "triangles": triangles,
            **metadata,
        }

    @classmethod
    def _closed_dome(
        cls,
        *,
        center_x,
        center_y,
        radius,
        base_z,
        top_z,
    ):
        base_ring = cls._ring(
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            z=base_z,
            segment_count=cls.RADIAL_SEGMENTS,
        )

        rings = [
            base_ring,
        ]

        dome_height = (
            float(top_z) - float(base_z)
        )

        for level_index in range(
            1,
            cls.DOME_RING_LEVELS,
        ):
            progress = (
                level_index
                / cls.DOME_RING_LEVELS
            )
            angle = (
                progress
                * math.pi
                / 2.0
            )

            ring_radius = (
                float(radius)
                * math.cos(angle)
            )
            ring_z = (
                float(base_z)
                + dome_height
                * math.sin(angle)
            )

            rings.append(
                cls._ring(
                    center_x=center_x,
                    center_y=center_y,
                    radius=ring_radius,
                    z=ring_z,
                    segment_count=(
                        cls.RADIAL_SEGMENTS
                    ),
                )
            )

        triangles = [
            *cls._cap_ring(
                base_ring,
                reverse=True,
            ),
        ]

        for lower, upper in zip(
            rings,
            rings[1:],
        ):
            triangles.extend(
                cls._connect_rings(
                    lower,
                    upper,
                )
            )

        apex = (
            float(center_x),
            float(center_y),
            float(top_z),
        )
        final_ring = rings[-1]

        for index in range(len(final_ring)):
            next_index = (
                index + 1
            ) % len(final_ring)

            triangles.append(
                (
                    final_ring[index],
                    final_ring[next_index],
                    apex,
                )
            )

        return {
            "type": "mosque_main_dome",
            "center_x": float(center_x),
            "center_y": float(center_y),
            "radius": float(radius),
            "base_z": float(base_z),
            "top_z": float(top_z),
            "base_ring": base_ring,
            "rings": tuple(rings),
            "apex": apex,
            "triangles": triangles,
        }

    @classmethod
    def _closed_cone(
        cls,
        *,
        center_x,
        center_y,
        radius,
        base_z,
        top_z,
        mesh_type,
        **metadata,
    ):
        base_ring = cls._ring(
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            z=base_z,
            segment_count=cls.RADIAL_SEGMENTS,
        )
        apex = (
            float(center_x),
            float(center_y),
            float(top_z),
        )

        triangles = [
            *cls._cap_ring(
                base_ring,
                reverse=True,
            ),
        ]

        for index in range(len(base_ring)):
            next_index = (
                index + 1
            ) % len(base_ring)

            triangles.append(
                (
                    base_ring[index],
                    base_ring[next_index],
                    apex,
                )
            )

        return {
            "type": mesh_type,
            "center_x": float(center_x),
            "center_y": float(center_y),
            "radius": float(radius),
            "base_z": float(base_z),
            "top_z": float(top_z),
            "base_ring": base_ring,
            "apex": apex,
            "triangles": triangles,
            **metadata,
        }

    @classmethod
    def build(
        cls,
        geometry,
    ):
        if not isinstance(
            geometry,
            AtlasMosqueLandmarkGeometry,
        ):
            raise TypeError(
                "geometry must be "
                "AtlasMosqueLandmarkGeometry"
            )

        footprint = tuple(
            (
                float(x),
                float(y),
            )
            for x, y in geometry.footprint
        )

        minimum_x = min(
            x
            for x, _ in footprint
        )
        maximum_x = max(
            x
            for x, _ in footprint
        )
        minimum_y = min(
            y
            for _, y in footprint
        )
        maximum_y = max(
            y
            for _, y in footprint
        )

        span_x = maximum_x - minimum_x
        span_y = maximum_y - minimum_y
        short_span = min(
            span_x,
            span_y,
        )

        if short_span <= 0.0:
            raise ValueError(
                "Mosque footprint must have positive area"
            )

        total_height = float(
            geometry.height_m
        )

        minimum_vertical_feature_mm = float(
            geometry.profile.nozzle_diameter_mm
        )

        prayer_hall_top_z = (
            total_height * 0.48
        )

        drum_height = max(
            total_height * 0.10,
            minimum_vertical_feature_mm,
        )
        drum_top_z = (
            prayer_hall_top_z
            + drum_height
        )

        dome_top_z = max(
            total_height * 0.76,
            drum_top_z
            + minimum_vertical_feature_mm,
        )

        minaret_body_top_z = min(
            total_height * 0.86,
            total_height
            - minimum_vertical_feature_mm,
        )
        minaret_cap_top_z = total_height

        dome_system = cls._resolve_dome_system(
            footprint=footprint,
            desired_dome_radius=(
                short_span * 0.28
            ),
            drum_radius_ratio=0.88,
            minimum_radius=(
                geometry.profile.nozzle_diameter_mm
            ),
        )

        center_x = dome_system[
            "center_x"
        ]
        center_y = dome_system[
            "center_y"
        ]
        dome_radius = dome_system[
            "dome_radius"
        ]
        drum_radius = dome_system[
            "drum_radius"
        ]

        minaret_radius = max(
            short_span * 0.045,
            geometry.profile.nozzle_diameter_mm,
        )
        balcony_radius = (
            minaret_radius * 1.45
        )
        balcony_thickness = max(
            total_height * 0.018,
            geometry.profile.nozzle_diameter_mm,
        )

        target_minaret_x = (
            maximum_x
            - short_span * 0.10
        )
        target_minaret_y = (
            minimum_y
            + short_span * 0.10
        )

        (
            minaret_center_x,
            minaret_center_y,
        ) = cls._resolve_minaret_center(
            footprint=footprint,
            target_x=target_minaret_x,
            target_y=target_minaret_y,
            clearance_radius=balcony_radius,
        )

        balcony_center_z = (
            minaret_body_top_z
            - total_height * 0.16
        )
        balcony_bottom_z = (
            balcony_center_z
            - balcony_thickness / 2.0
        )
        balcony_top_z = (
            balcony_center_z
            + balcony_thickness / 2.0
        )

        prayer_hall = cls._extrude_footprint(
            footprint=footprint,
            bottom_z=0.0,
            top_z=prayer_hall_top_z,
            mesh_type="mosque_prayer_hall",
        )

        dome_drum = cls._closed_cylinder(
            center_x=center_x,
            center_y=center_y,
            radius=drum_radius,
            bottom_z=prayer_hall_top_z,
            top_z=drum_top_z,
            mesh_type="mosque_dome_drum",
        )

        dome = cls._closed_dome(
            center_x=center_x,
            center_y=center_y,
            radius=dome_radius,
            base_z=drum_top_z,
            top_z=dome_top_z,
        )

        minaret = cls._closed_cylinder(
            center_x=minaret_center_x,
            center_y=minaret_center_y,
            radius=minaret_radius,
            bottom_z=0.0,
            top_z=minaret_body_top_z,
            mesh_type="mosque_minaret_body",
        )

        balcony = cls._closed_cylinder(
            center_x=minaret_center_x,
            center_y=minaret_center_y,
            radius=balcony_radius,
            bottom_z=balcony_bottom_z,
            top_z=balcony_top_z,
            mesh_type="mosque_minaret_balcony",
        )

        minaret_cap = cls._closed_cone(
            center_x=minaret_center_x,
            center_y=minaret_center_y,
            radius=minaret_radius,
            base_z=minaret_body_top_z,
            top_z=minaret_cap_top_z,
            mesh_type="mosque_minaret_cap",
        )

        component_meshes = (
            prayer_hall,
            dome_drum,
            dome,
            minaret,
            balcony,
            minaret_cap,
        )

        minaret_triangles = tuple(
            minaret["triangles"]
        )
        minaret_cap_triangles = tuple(
            minaret_cap["triangles"]
        )

        radial_segments = cls.RADIAL_SEGMENTS

        combined_minaret_triangles = (
            minaret_triangles[
                :-radial_segments
            ]
        )
        combined_minaret_cap_triangles = (
            minaret_cap_triangles[
                radial_segments:
            ]
        )

        triangles = [
            *prayer_hall["triangles"],
            *dome_drum["triangles"],
            *dome["triangles"],
            *combined_minaret_triangles,
            *balcony["triangles"],
            *combined_minaret_cap_triangles,
        ]

        return {
            "type": "mosque_landmark",
            "landmark_id": geometry.landmark_id,
            "worship_profile": "mosque",
            "worship_grammar": (
                geometry.grammar_name
            ),
            "special_architecture_applied": True,
            "uses_real_footprint": True,
            "footprint": footprint,
            "height_m": total_height,
            "dome_system": dome_system,
            "prayer_hall_meshes": [
                prayer_hall,
            ],
            "dome_drum_meshes": [
                dome_drum,
            ],
            "dome_meshes": [
                dome,
            ],
            "minaret_meshes": [
                minaret,
            ],
            "minaret_balcony_meshes": [
                balcony,
            ],
            "minaret_cap_meshes": [
                minaret_cap,
            ],
            "triangles": triangles,
        }
