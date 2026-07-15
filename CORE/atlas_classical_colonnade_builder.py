"""
ATLAS Classical Colonnade Builder v0.1

Doğrusal veya kavisli taşıyıcı hat üzerinde genel amaçlı
klasik sütun dizisi üretir.

Kullanım alanları:
- antik tiyatro üst galerileri
- tapınak peristilleri
- stoalar
- anıtsal girişler
- sütunlu cepheler

Bu builder herhangi bir yapı adına, OSM kimliğine veya
fixture geometrisine bağlı değildir.
"""

from math import hypot

from CORE.atlas_closed_cylinder_builder import (
    AtlasClosedCylinderBuilder,
)


class AtlasClassicalColonnadeBuilder:
    DEFAULT_COLUMN_RADIUS_MM = 0.45
    DEFAULT_COLUMN_HEIGHT_MM = 2.40
    DEFAULT_TARGET_SPACING_MM = 2.20
    DEFAULT_COLUMN_SEGMENTS = 10
    MIN_COLUMN_COUNT = 2

    @staticmethod
    def build_along_polyline(
        path_points,
        base_z,
        column_radius_mm=None,
        column_height_mm=None,
        target_spacing_mm=None,
        column_segments=None,
        include_endpoints=True,
        metadata=None,
    ):
        cleaned_path = (
            AtlasClassicalColonnadeBuilder
            ._clean_path(path_points)
        )

        if len(cleaned_path) < 2:
            raise ValueError(
                "path_points must contain at least "
                "two distinct points"
            )

        base_z = float(base_z)

        if column_radius_mm is None:
            column_radius_mm = (
                AtlasClassicalColonnadeBuilder
                .DEFAULT_COLUMN_RADIUS_MM
            )

        if column_height_mm is None:
            column_height_mm = (
                AtlasClassicalColonnadeBuilder
                .DEFAULT_COLUMN_HEIGHT_MM
            )

        if target_spacing_mm is None:
            target_spacing_mm = (
                AtlasClassicalColonnadeBuilder
                .DEFAULT_TARGET_SPACING_MM
            )

        if column_segments is None:
            column_segments = (
                AtlasClassicalColonnadeBuilder
                .DEFAULT_COLUMN_SEGMENTS
            )

        column_radius_mm = float(
            column_radius_mm
        )

        column_height_mm = float(
            column_height_mm
        )

        target_spacing_mm = float(
            target_spacing_mm
        )

        if target_spacing_mm <= 0.0:
            raise ValueError(
                "target_spacing_mm must be "
                "greater than zero"
            )

        sampled_points = (
            AtlasClassicalColonnadeBuilder
            ._sample_polyline(
                path_points=cleaned_path,
                target_spacing_mm=(
                    target_spacing_mm
                ),
                include_endpoints=(
                    include_endpoints
                ),
            )
        )

        if (
            len(sampled_points)
            < AtlasClassicalColonnadeBuilder
            .MIN_COLUMN_COUNT
        ):
            raise ValueError(
                "path is too short for a colonnade"
            )

        component_meshes = []
        triangles = []

        for index, point in enumerate(
            sampled_points
        ):
            component_metadata = {
                "component_type": (
                    "classical_column"
                ),
                "component_index": index,
                "source_system": (
                    "classical_colonnade"
                ),
            }

            if metadata:
                component_metadata.update(
                    dict(metadata)
                )

            component_mesh = (
                AtlasClosedCylinderBuilder.build(
                    center_x=point[0],
                    center_y=point[1],
                    base_z=base_z,
                    radius=column_radius_mm,
                    height=column_height_mm,
                    segments=column_segments,
                    metadata=component_metadata,
                )
            )

            component_meshes.append(
                component_mesh
            )

            triangles.extend(
                component_mesh["triangles"]
            )

        actual_spacings = [
            hypot(
                sampled_points[index + 1][0]
                - sampled_points[index][0],
                sampled_points[index + 1][1]
                - sampled_points[index][1],
            )
            for index in range(
                len(sampled_points) - 1
            )
        ]

        mesh = {
            "triangles": triangles,
            "component_meshes": (
                component_meshes
            ),
            "column_centers": sampled_points,
            "column_count": len(
                sampled_points
            ),
            "column_radius_mm": (
                column_radius_mm
            ),
            "column_height_mm": (
                column_height_mm
            ),
            "target_spacing_mm": (
                target_spacing_mm
            ),
            "actual_spacing_min_mm": min(
                actual_spacings
            ),
            "actual_spacing_max_mm": max(
                actual_spacings
            ),
            "base_z": base_z,
            "top_z": (
                base_z
                + column_height_mm
            ),
            "geometry_type": (
                "classical_colonnade"
            ),
        }

        if metadata:
            mesh.update(
                dict(metadata)
            )

        return mesh

    @staticmethod
    def _clean_path(path_points):
        cleaned = []

        for point in path_points or []:
            if len(point) < 2:
                continue

            candidate = (
                float(point[0]),
                float(point[1]),
            )

            if (
                not cleaned
                or candidate != cleaned[-1]
            ):
                cleaned.append(candidate)

        return cleaned

    @staticmethod
    def _sample_polyline(
        path_points,
        target_spacing_mm,
        include_endpoints,
    ):
        segment_lengths = []
        total_length = 0.0

        for index in range(
            len(path_points) - 1
        ):
            start = path_points[index]
            end = path_points[index + 1]

            length = hypot(
                end[0] - start[0],
                end[1] - start[1],
            )

            segment_lengths.append(length)
            total_length += length

        if total_length <= 0.0:
            return []

        interval_count = max(
            1,
            int(
                round(
                    total_length
                    / target_spacing_mm
                )
            ),
        )

        sample_count = (
            interval_count + 1
            if include_endpoints
            else max(
                2,
                interval_count,
            )
        )

        if include_endpoints:
            target_distances = [
                total_length
                * index
                / (sample_count - 1)
                for index in range(
                    sample_count
                )
            ]
        else:
            target_distances = [
                total_length
                * (index + 1)
                / (sample_count + 1)
                for index in range(
                    sample_count
                )
            ]

        sampled_points = []

        for target_distance in target_distances:
            traversed = 0.0

            for index, segment_length in enumerate(
                segment_lengths
            ):
                next_traversed = (
                    traversed
                    + segment_length
                )

                if (
                    target_distance
                    <= next_traversed
                    or index
                    == len(segment_lengths) - 1
                ):
                    start = path_points[index]
                    end = path_points[index + 1]

                    if segment_length <= 0.0:
                        ratio = 0.0
                    else:
                        ratio = (
                            target_distance
                            - traversed
                        ) / segment_length

                    sampled_points.append(
                        (
                            start[0]
                            + (
                                end[0]
                                - start[0]
                            )
                            * ratio,
                            start[1]
                            + (
                                end[1]
                                - start[1]
                            )
                            * ratio,
                        )
                    )
                    break

                traversed = next_traversed

        return sampled_points
