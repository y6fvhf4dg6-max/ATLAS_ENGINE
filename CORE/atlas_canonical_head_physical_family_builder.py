from __future__ import annotations

import math

import numpy as np
from collections.abc import Mapping, Sequence
from typing import Any


class AtlasCanonicalHeadPhysicalFamilyBuilder:
    """
    Builds representation-specific physical geometry from an
    already physical-coordinate canonical-head triangle mesh.

    Scope:
    - relief: controlled depth compression with an integral
      planar backing surface;
    - bust: full head plus pedestal support;
    - figurine_head: full head plus attachment interface;
    - story_kit_component: full head plus kit mount.

    This builder does not claim manufacturability, physical
    identity preservation, slicer success, or production approval.
    """

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    FAMILY_BUILDER_PROVENANCE = (
        "atlas_canonical_head_physical_family_builder:v1"
    )

    RELIEF_HEIGHT_MM = 2.00
    RELIEF_BASE_THICKNESS_MM = 0.80
    RELIEF_SAMPLE_PITCH_MM = 0.25

    BUST_SUPPORT_WIDTH_RATIO = 0.56
    BUST_SUPPORT_DEPTH_RATIO = 0.52
    BUST_SUPPORT_HEIGHT_RATIO = 0.22

    FIGURINE_ATTACHMENT_WIDTH_RATIO = 0.28
    FIGURINE_ATTACHMENT_DEPTH_RATIO = 0.28
    FIGURINE_ATTACHMENT_HEIGHT_RATIO = 0.12

    KIT_MOUNT_WIDTH_RATIO = 0.44
    KIT_MOUNT_DEPTH_RATIO = 0.34
    KIT_MOUNT_HEIGHT_RATIO = 0.10

    @classmethod
    def build(
        cls,
        *,
        physical_head_mesh: Mapping[str, Any],
        representation_kind: str,
        target_head_height_mm: float,
        relief_region_masks: Mapping[str, Any] | None = None,
        minimum_printable_separation_mm: float | None = None,
    ) -> dict[str, Any]:
        triangles = cls._triangles(
            physical_head_mesh
        )

        kind = cls._representation_kind(
            representation_kind
        )

        target_height = cls._positive_finite(
            target_head_height_mm,
            name="target_head_height_mm",
        )

        has_relief_regions = (
            relief_region_masks is not None
        )
        has_minimum_separation = (
            minimum_printable_separation_mm is not None
        )

        if (
            kind != "relief"
            and (
                has_relief_regions
                or has_minimum_separation
            )
        ):
            raise ValueError(
                "relief_region_masks and "
                "minimum_printable_separation_mm "
                "are valid only for relief"
            )

        if (
            has_relief_regions
            != has_minimum_separation
        ):
            raise ValueError(
                "relief_region_masks and "
                "minimum_printable_separation_mm "
                "must be supplied together"
            )

        minimum_separation = (
            cls._positive_finite(
                minimum_printable_separation_mm,
                name="minimum_printable_separation_mm",
            )
            if has_minimum_separation
            else None
        )

        bounds = cls._bounds(triangles)

        observed_height = (
            bounds["max_y"]
            - bounds["min_y"]
        )

        if not math.isclose(
            observed_height,
            target_height,
            rel_tol=1e-6,
            abs_tol=1e-6,
        ):
            raise ValueError(
                "physical_head_mesh Y extent must match "
                "target_head_height_mm"
            )

        canonical_depth = (
            bounds["max_z"]
            - bounds["min_z"]
        )

        if canonical_depth <= 0.0:
            raise ValueError(
                "physical_head_mesh must have positive depth"
            )

        if kind == "relief":
            projection_source = (
                physical_head_mesh.get(
                    "frontal_projection_triangles"
                )
            )

            if not projection_source:
                projection_triangles = triangles
            else:
                projection_triangles = cls._triangles(
                    {
                        "triangles": projection_source,
                    }
                )

            (
                relief_geometry,
                relief_depth_metadata,
            ) = cls._frontal_visible_surface_relief(
                triangles=projection_triangles,
                projection_vertices=physical_head_mesh.get(
                    "frontal_projection_vertices"
                ),
                projection_faces=physical_head_mesh.get(
                    "frontal_projection_faces"
                ),
                bounds=bounds,
                relief_height_mm=(
                    cls.RELIEF_HEIGHT_MM
                ),
                sample_pitch_mm=(
                    cls.RELIEF_SAMPLE_PITCH_MM
                ),
                region_masks=relief_region_masks,
                minimum_printable_separation_mm=(
                    minimum_separation
                ),
            )

            return cls._result(
                kind=kind,
                geometry_kind="relief",
                triangles=relief_geometry,
                support_geometry_kind="planar_backing",
                canonical_depth_mm=canonical_depth,
                physical_depth_mm=(
                    cls.RELIEF_HEIGHT_MM
                ),
                extra_metadata=relief_depth_metadata,
            )

        attachment_boundary = (
            physical_head_mesh.get(
                "support_attachment_boundary"
            )
        )

        if kind == "bust":
            integral = cls._integral_carrier(
                triangles=triangles,
                attachment_boundary=attachment_boundary,
                width_ratio=cls.BUST_SUPPORT_WIDTH_RATIO,
                depth_ratio=cls.BUST_SUPPORT_DEPTH_RATIO,
                height_ratio=cls.BUST_SUPPORT_HEIGHT_RATIO,
                target_head_height_mm=target_height,
            )

            return cls._result(
                kind=kind,
                geometry_kind="bust",
                triangles=integral,
                support_geometry_kind="pedestal",
                canonical_depth_mm=canonical_depth,
                physical_depth_mm=canonical_depth,
            )

        if kind == "figurine_head":
            integral = cls._integral_carrier(
                triangles=triangles,
                attachment_boundary=attachment_boundary,
                width_ratio=(
                    cls.FIGURINE_ATTACHMENT_WIDTH_RATIO
                ),
                depth_ratio=(
                    cls.FIGURINE_ATTACHMENT_DEPTH_RATIO
                ),
                height_ratio=(
                    cls.FIGURINE_ATTACHMENT_HEIGHT_RATIO
                ),
                target_head_height_mm=target_height,
            )

            return cls._result(
                kind=kind,
                geometry_kind="figurine_head",
                triangles=integral,
                support_geometry_kind=(
                    "attachment_interface"
                ),
                canonical_depth_mm=canonical_depth,
                physical_depth_mm=canonical_depth,
            )

        integral = cls._integral_carrier(
            triangles=triangles,
            attachment_boundary=attachment_boundary,
            width_ratio=cls.KIT_MOUNT_WIDTH_RATIO,
            depth_ratio=cls.KIT_MOUNT_DEPTH_RATIO,
            height_ratio=cls.KIT_MOUNT_HEIGHT_RATIO,
            target_head_height_mm=target_height,
        )

        return cls._result(
            kind=kind,
            geometry_kind="story_kit_component",
            triangles=integral,
            support_geometry_kind="kit_mount",
            canonical_depth_mm=canonical_depth,
            physical_depth_mm=canonical_depth,
        )

    @classmethod
    def _result(
        cls,
        *,
        kind: str,
        geometry_kind: str,
        triangles: Sequence,
        support_geometry_kind: str,
        canonical_depth_mm: float,
        physical_depth_mm: float,
        extra_metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = {
            "representation_kind": kind,
            "physical_unit": "mm",
            "family_geometry_kind": geometry_kind,
            "support_geometry_kind": (
                support_geometry_kind
            ),
            "canonical_depth_mm": float(
                canonical_depth_mm
            ),
            "physical_depth_mm": float(
                physical_depth_mm
            ),
            "family_geometry": {
                "triangles": tuple(triangles),
                "type": (
                    "canonical_head_physical_family_geometry"
                ),
                "representation_kind": kind,
            },
            "family_builder_provenance": (
                cls.FAMILY_BUILDER_PROVENANCE
            ),
            "manufacturability_status": "UNRESOLVED",
        }

        if extra_metadata:
            result.update(
                extra_metadata
            )

        return result

    @staticmethod
    def _triangles(
        physical_head_mesh: Mapping[str, Any],
    ) -> tuple:
        if not isinstance(
            physical_head_mesh,
            Mapping,
        ):
            raise TypeError(
                "physical_head_mesh must be a mapping"
            )

        raw_triangles = physical_head_mesh.get(
            "triangles"
        )

        if raw_triangles is None:
            raise ValueError(
                "physical_head_mesh must contain triangles"
            )

        try:
            raw_triangles = tuple(
                raw_triangles
            )
        except TypeError as exc:
            raise TypeError(
                "physical_head_mesh triangles must be iterable"
            ) from exc

        if not raw_triangles:
            raise ValueError(
                "physical_head_mesh triangles must not be empty"
            )

        resolved = []

        for triangle in raw_triangles:
            try:
                points = tuple(triangle)
            except TypeError as exc:
                raise TypeError(
                    "each triangle must be iterable"
                ) from exc

            if len(points) != 3:
                raise ValueError(
                    "each triangle must contain three points"
                )

            resolved_points = []

            for point in points:
                try:
                    coordinates = tuple(point)
                except TypeError as exc:
                    raise TypeError(
                        "each triangle point must be iterable"
                    ) from exc

                if len(coordinates) != 3:
                    raise ValueError(
                        "each triangle point must contain "
                        "three coordinates"
                    )

                numeric = tuple(
                    float(value)
                    for value in coordinates
                )

                if not all(
                    math.isfinite(value)
                    for value in numeric
                ):
                    raise ValueError(
                        "triangle coordinates must be finite"
                    )

                resolved_points.append(
                    numeric
                )

            p1, p2, p3 = resolved_points

            ux = p2[0] - p1[0]
            uy = p2[1] - p1[1]
            uz = p2[2] - p1[2]

            vx = p3[0] - p1[0]
            vy = p3[1] - p1[1]
            vz = p3[2] - p1[2]

            cross = (
                uy * vz - uz * vy,
                uz * vx - ux * vz,
                ux * vy - uy * vx,
            )

            area_twice = math.sqrt(
                cross[0] ** 2
                + cross[1] ** 2
                + cross[2] ** 2
            )

            if area_twice <= 1e-12:
                raise ValueError(
                    "physical_head_mesh contains "
                    "degenerate triangles"
                )

            resolved.append(
                tuple(resolved_points)
            )

        return tuple(resolved)

    @staticmethod
    def _bounds(
        triangles: Sequence,
    ) -> dict[str, float]:
        points = [
            point
            for triangle in triangles
            for point in triangle
        ]

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        zs = [point[2] for point in points]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
            "min_z": min(zs),
            "max_z": max(zs),
        }

    @classmethod
    def _frontal_visible_surface_relief(
        cls,
        *,
        triangles: Sequence,
        projection_vertices: Sequence | None = None,
        projection_faces: Sequence | None = None,
        bounds: Mapping[str, float],
        relief_height_mm: float,
        sample_pitch_mm: float,
        region_masks: Mapping[str, Any] | None = None,
        minimum_printable_separation_mm: float | None = None,
    ) -> tuple:
        """
        Convert the frontal visible surface of the canonical
        head into a silhouette-bounded closed 2.5D relief.

        FLAME physical coordinates:
        - X: frontal horizontal
        - Y: frontal vertical
        - Z: frontal depth

        At each frontal sample only the greatest Z value is
        retained. Geometry hidden behind that visible surface
        therefore cannot influence the relief.
        """

        from CORE.atlas_projected_semantic_mesh_depth_rasterizer import (
            AtlasProjectedSemanticMeshDepthRasterizer,
        )

        width = (
            float(bounds["max_x"])
            - float(bounds["min_x"])
        )
        height = (
            float(bounds["max_y"])
            - float(bounds["min_y"])
        )

        if width <= 0.0 or height <= 0.0:
            raise ValueError(
                "relief frontal extent must be positive"
            )

        row_count = max(
            3,
            int(math.ceil(
                height / sample_pitch_mm
            )) + 1,
        )
        column_count = max(
            3,
            int(math.ceil(
                width / sample_pitch_mm
            )) + 1,
        )

        min_x = float(bounds["min_x"])
        min_y = float(bounds["min_y"])

        local_triangles = tuple(
            tuple(
                (
                    float(point[0]) - min_x,
                    float(point[1]) - min_y,
                    float(point[2]),
                )
                for point in triangle
            )
            for triangle in triangles
        )

        has_vertices = bool(projection_vertices)
        has_faces = bool(projection_faces)

        if has_vertices != has_faces:
            raise ValueError(
                "indexed relief projection requires both "
                "projection_vertices and projection_faces"
            )

        indexed_projection = has_vertices and has_faces
        raster_mesh = {
            "triangles": local_triangles,
        }

        if indexed_projection:
            from CORE.atlas_canonical_head_vertex_normal_evaluator import (
                AtlasCanonicalHeadVertexNormalEvaluator,
            )

            local_vertices = tuple(
                (
                    float(point[0]) - min_x,
                    float(point[1]) - min_y,
                    float(point[2]),
                )
                for point in projection_vertices
            )
            indexed_faces = tuple(
                tuple(face)
                for face in projection_faces
            )

            vertex_normals = (
                AtlasCanonicalHeadVertexNormalEvaluator
                .evaluate_indexed_surface(
                    vertices=local_vertices,
                    faces=indexed_faces,
                )
            )

            raster_mesh.update(
                {
                    "vertex_normals": vertex_normals,
                    "face_vertex_indices": indexed_faces,
                }
            )

        raster = (
            AtlasProjectedSemanticMeshDepthRasterizer
            .rasterize(
                mesh=raster_mesh,
                width_mm=width,
                depth_mm=height,
                rows=row_count,
                columns=column_count,
            )
        )

        coverage = np.asarray(
            raster["coverage_map"],
            dtype=np.bool_,
        )
        visible_depth = np.asarray(
            raster["depth_map"],
            dtype=np.float64,
        )

        if not np.any(coverage):
            raise ValueError(
                "frontal visible surface has no coverage"
            )

        active_cells = np.zeros(
            (
                row_count - 1,
                column_count - 1,
            ),
            dtype=np.bool_,
        )

        for row in range(row_count - 1):
            for column in range(
                column_count - 1
            ):
                active_cells[
                    row,
                    column,
                ] = bool(
                    coverage[row, column]
                    and coverage[
                        row,
                        column + 1,
                    ]
                    and coverage[
                        row + 1,
                        column,
                    ]
                    and coverage[
                        row + 1,
                        column + 1,
                    ]
                )

        active_vertex_coverage = np.zeros_like(
            coverage,
            dtype=np.bool_,
        )

        active_rows, active_columns = np.nonzero(
            active_cells
        )

        for row_offset, column_offset in (
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
        ):
            active_vertex_coverage[
                active_rows + row_offset,
                active_columns + column_offset,
            ] = True

        active_vertex_coverage &= coverage

        if indexed_projection:
            from CORE.atlas_relief_normal_structure_detail_decomposer import (
                AtlasReliefNormalStructureDetailDecomposer,
            )
            from CORE.atlas_relief_normal_gradient_limiter import (
                AtlasReliefNormalGradientLimiter,
            )
            from CORE.atlas_relief_normal_height_integrator import (
                AtlasReliefNormalHeightIntegrator,
            )

            normal_map = np.asarray(
                raster["normal_map"],
                dtype=np.float64,
            )

            structure_normals, detail_normals = (
                AtlasReliefNormalStructureDetailDecomposer.decompose(
                    normal_map,
                    mask=active_vertex_coverage,
                )
            )

            limited_detail_normals = (
                AtlasReliefNormalGradientLimiter.limit(
                    detail_normals,
                    mask=active_vertex_coverage,
                )
            )

            reconstructed_normals = (
                AtlasReliefNormalStructureDetailDecomposer.recombine(
                    structure_normals,
                    limited_detail_normals,
                )
            )

            normalized = (
                AtlasReliefNormalHeightIntegrator.integrate(
                    reconstructed_normals,
                    mask=active_vertex_coverage,
                    sample_spacing_mm=sample_pitch_mm,
                    normalize_output=True,
                )
            )

            relief_depth_mm = (
                normalized
                * relief_height_mm
            )

            relief_depth_metadata = {
                "relief_depth_transfer_kind": (
                    "visible_normal_gradient_reconstruction"
                ),
                "relief_semantic_support": (
                    "constraint_only"
                    if region_masks is not None
                    else "not_used"
                ),
                "relief_depth_policy_provenance": (
                    "not_geometry_owner"
                    if region_masks is not None
                    else "not_used"
                ),
                "relief_geometry_owner": (
                    "visible_normal_gradient_reconstruction"
                ),
                "relief_reconstruction_sample_pitch_mm": (
                    float(sample_pitch_mm)
                ),
                "relief_reconstruction_height_mm": (
                    float(relief_height_mm)
                ),
            }

        elif region_masks is None:
            normalized = np.zeros_like(
                visible_depth,
                dtype=np.float64,
            )

            covered_depth = visible_depth[
                coverage
            ]

            minimum_visible = float(
                covered_depth.min()
            )
            maximum_visible = float(
                covered_depth.max()
            )
            visible_range = (
                maximum_visible
                - minimum_visible
            )

            if visible_range > 1e-12:
                normalized[coverage] = (
                    covered_depth
                    - minimum_visible
                ) / visible_range

            relief_depth_mm = (
                normalized
                * relief_height_mm
            )

            relief_depth_metadata = {
                "relief_depth_transfer_kind": (
                    "covered_global_linear"
                ),
                "relief_semantic_support": (
                    "not_used"
                ),
                "relief_depth_policy_provenance": (
                    "not_used"
                ),
            }
        else:
            from CORE.atlas_canonical_head_region_aware_relief_depth_policy import (
                AtlasCanonicalHeadRegionAwareReliefDepthPolicy,
            )

            policy_result = (
                AtlasCanonicalHeadRegionAwareReliefDepthPolicy
                .transfer(
                    source_depth_map=visible_depth,
                    coverage_map=active_vertex_coverage,
                    region_masks=region_masks,
                    relief_height_mm=relief_height_mm,
                    minimum_printable_separation_mm=(
                        minimum_printable_separation_mm
                    ),
                )
            )

            relief_depth_mm = np.asarray(
                policy_result.depth_map_mm,
                dtype=np.float64,
            )

            relief_depth_metadata = {
                "relief_depth_transfer_kind": (
                    policy_result.metadata[
                        "transfer_kind"
                    ]
                ),
                "relief_semantic_support": (
                    policy_result.metadata[
                        "semantic_support"
                    ]
                ),
                "relief_depth_policy_provenance": (
                    policy_result.metadata[
                        "policy_provenance"
                    ]
                ),
                "relief_depth_policy_metadata": dict(
                    policy_result.metadata
                ),
            }

        relief_depth_metadata[
            "relief_projection_correspondence"
        ] = (
            "indexed_visible_surface"
            if indexed_projection
            else "triangle_only"
        )

        x_coordinates = np.linspace(
            min_x,
            float(bounds["max_x"]),
            column_count,
            dtype=np.float64,
        )
        y_coordinates = np.linspace(
            min_y,
            float(bounds["max_y"]),
            row_count,
            dtype=np.float64,
        )

        bottom_z = 0.0
        relief_base_z = (
            bottom_z
            + cls.RELIEF_BASE_THICKNESS_MM
        )
        triangles_out = []

        def top(row, column):
            return (
                float(x_coordinates[column]),
                float(y_coordinates[row]),
                float(
                    relief_base_z
                    + relief_depth_mm[
                        row,
                        column,
                    ]
                ),
            )

        def bottom(row, column):
            return (
                float(x_coordinates[column]),
                float(y_coordinates[row]),
                float(bottom_z),
            )

        def add_wall(
            bottom_a,
            bottom_b,
            top_b,
            top_a,
        ):
            triangles_out.append(
                (
                    bottom_a,
                    bottom_b,
                    top_b,
                )
            )
            triangles_out.append(
                (
                    bottom_a,
                    top_b,
                    top_a,
                )
            )

        for row in range(row_count - 1):
            for column in range(
                column_count - 1
            ):
                if not active_cells[
                    row,
                    column,
                ]:
                    continue

                t00 = top(row, column)
                t10 = top(
                    row,
                    column + 1,
                )
                t01 = top(
                    row + 1,
                    column,
                )
                t11 = top(
                    row + 1,
                    column + 1,
                )

                b00 = bottom(row, column)
                b10 = bottom(
                    row,
                    column + 1,
                )
                b01 = bottom(
                    row + 1,
                    column,
                )
                b11 = bottom(
                    row + 1,
                    column + 1,
                )

                triangles_out.extend(
                    (
                        (
                            t00,
                            t10,
                            t11,
                        ),
                        (
                            t00,
                            t11,
                            t01,
                        ),
                        (
                            b00,
                            b11,
                            b10,
                        ),
                        (
                            b00,
                            b01,
                            b11,
                        ),
                    )
                )

                if (
                    row == 0
                    or not active_cells[
                        row - 1,
                        column,
                    ]
                ):
                    add_wall(
                        b00,
                        b10,
                        t10,
                        t00,
                    )

                if (
                    column
                    == column_count - 2
                    or not active_cells[
                        row,
                        column + 1,
                    ]
                ):
                    add_wall(
                        b10,
                        b11,
                        t11,
                        t10,
                    )

                if (
                    row == row_count - 2
                    or not active_cells[
                        row + 1,
                        column,
                    ]
                ):
                    add_wall(
                        b11,
                        b01,
                        t01,
                        t11,
                    )

                if (
                    column == 0
                    or not active_cells[
                        row,
                        column - 1,
                    ]
                ):
                    add_wall(
                        b01,
                        b00,
                        t00,
                        t01,
                    )

        if not triangles_out:
            raise ValueError(
                "frontal coverage produced no relief cells"
            )

        return (
            tuple(
                triangles_out
            ),
            relief_depth_metadata,
        )

    @staticmethod
    def _compress_depth(
        *,
        triangles: Sequence,
        bounds: Mapping[str, float],
        ratio: float,
    ) -> tuple:
        center_z = (
            bounds["min_z"]
            + bounds["max_z"]
        ) / 2.0

        return tuple(
            tuple(
                (
                    point[0],
                    point[1],
                    center_z
                    + (
                        point[2]
                        - center_z
                    )
                    * ratio,
                )
                for point in triangle
            )
            for triangle in triangles
        )

    @staticmethod
    def _compress_depth_with_planar_backing(
        *,
        triangles: Sequence,
        bounds: Mapping[str, float],
        ratio: float,
    ) -> tuple:
        """
        Compress canonical-head depth while converting the
        rear half of the existing closed topology into one
        integral planar backing surface.

        No secondary solid or boolean union is introduced.
        The front half retains relative depth variation.
        """

        if not (
            math.isfinite(ratio)
            and 0.0 < ratio <= 1.0
        ):
            raise ValueError(
                "relief depth ratio must be finite and "
                "within (0, 1]"
            )

        min_z = float(
            bounds["min_z"]
        )
        max_z = float(
            bounds["max_z"]
        )

        center_z = (
            min_z + max_z
        ) / 2.0

        compressed_min_z = (
            center_z
            + (
                min_z - center_z
            )
            * ratio
        )

        def transform(point):
            x, y, z = point

            if z <= center_z:
                transformed_z = compressed_min_z
            else:
                transformed_z = (
                    center_z
                    + (
                        z - center_z
                    )
                    * ratio
                )

            return (
                float(x),
                float(y),
                float(transformed_z),
            )

        transformed = tuple(
            tuple(
                transform(point)
                for point in triangle
            )
            for triangle in triangles
        )

        return (
            AtlasCanonicalHeadPhysicalFamilyBuilder
            ._normalize_closed_mesh_orientation(
                transformed
            )
        )

    @classmethod
    def _integral_carrier(
        cls,
        *,
        triangles: Sequence,
        attachment_boundary: Any,
        width_ratio: float,
        depth_ratio: float,
        height_ratio: float,
        target_head_height_mm: float,
    ) -> tuple:
        if not isinstance(
            attachment_boundary,
            Mapping,
        ):
            raise ValueError(
                "3D family geometry requires explicit "
                "support_attachment_boundary metadata"
            )

        try:
            ring = tuple(
                tuple(float(value) for value in point)
                for point in attachment_boundary[
                    "physical_points"
                ]
            )
            centroid = tuple(
                float(value)
                for value in attachment_boundary[
                    "centroid"
                ]
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "support_attachment_boundary metadata "
                "is invalid"
            ) from exc

        if len(ring) < 3 or len(centroid) != 3:
            raise ValueError(
                "support_attachment_boundary must contain "
                "at least three points and one 3D centroid"
            )

        if not all(
            len(point) == 3
            and all(
                math.isfinite(value)
                for value in point
            )
            for point in ring
        ):
            raise ValueError(
                "support_attachment_boundary points "
                "must be finite 3D coordinates"
            )

        if not all(
            math.isfinite(value)
            for value in centroid
        ):
            raise ValueError(
                "support_attachment_boundary centroid "
                "must be finite"
            )

        if not (
            0.0 < width_ratio <= 1.0
            and 0.0 < depth_ratio <= 1.0
            and height_ratio > 0.0
        ):
            raise ValueError(
                "carrier ratios must be positive and "
                "width/depth ratios must not exceed 1"
            )

        def point_key(point):
            return tuple(
                round(float(value), 9)
                for value in point
            )

        ring_keys = {
            point_key(point)
            for point in ring
        }
        centroid_key = point_key(
            centroid
        )

        retained = []
        removed_cap_count = 0

        for triangle in triangles:
            keys = {
                point_key(point)
                for point in triangle
            }

            if (
                centroid_key in keys
                and len(keys & ring_keys) == 2
            ):
                removed_cap_count += 1
                continue

            retained.append(
                tuple(triangle)
            )

        if removed_cap_count != len(ring):
            raise ValueError(
                "support attachment closure cap could "
                "not be identified exactly"
            )

        carrier_height = (
            target_head_height_mm
            * height_ratio
        )

        lower_y = (
            min(point[1] for point in ring)
            - carrier_height
        )

        center_x = centroid[0]
        center_z = centroid[2]

        lower_ring = tuple(
            (
                center_x
                + (
                    point[0] - center_x
                )
                * width_ratio,
                lower_y,
                center_z
                + (
                    point[2] - center_z
                )
                * depth_ratio,
            )
            for point in ring
        )

        side_triangles = []

        for index, current in enumerate(
            ring
        ):
            next_index = (
                index + 1
            ) % len(ring)

            next_point = ring[
                next_index
            ]
            lower_current = lower_ring[
                index
            ]
            lower_next = lower_ring[
                next_index
            ]

            # The adapter metadata ring follows the
            # final head boundary direction. The carrier
            # therefore consumes the exposed head edge in
            # the opposite direction.
            side_triangles.extend(
                (
                    (
                        next_point,
                        current,
                        lower_current,
                    ),
                    (
                        next_point,
                        lower_current,
                        lower_next,
                    ),
                )
            )

        lower_center = (
            sum(
                point[0]
                for point in lower_ring
            ) / len(lower_ring),
            lower_y,
            sum(
                point[2]
                for point in lower_ring
            ) / len(lower_ring),
        )

        bottom_triangles = []

        for index, current in enumerate(
            lower_ring
        ):
            next_point = lower_ring[
                (index + 1)
                % len(lower_ring)
            ]

            bottom_triangles.append(
                (
                    next_point,
                    current,
                    lower_center,
                )
            )

        combined = tuple(
            (
                *retained,
                *side_triangles,
                *bottom_triangles,
            )
        )

        return cls._normalize_closed_mesh_orientation(
            combined
        )

    @staticmethod
    def _normalize_closed_mesh_orientation(
        triangles: Sequence,
    ) -> tuple:
        resolved = tuple(
            tuple(
                tuple(float(value) for value in point)
                for point in triangle
            )
            for triangle in triangles
        )

        if not resolved:
            return resolved

        edge_counts = {}
        signed_volume = 0.0

        for p1, p2, p3 in resolved:
            keys = tuple(
                tuple(
                    round(float(value), 9)
                    for value in point
                )
                for point in (
                    p1,
                    p2,
                    p3,
                )
            )

            for start, end in (
                (keys[0], keys[1]),
                (keys[1], keys[2]),
                (keys[2], keys[0]),
            ):
                edge = tuple(
                    sorted(
                        (start, end)
                    )
                )
                edge_counts[edge] = (
                    edge_counts.get(
                        edge,
                        0,
                    )
                    + 1
                )

            signed_volume += (
                p1[0] * (
                    p2[1] * p3[2]
                    - p2[2] * p3[1]
                )
                - p1[1] * (
                    p2[0] * p3[2]
                    - p2[2] * p3[0]
                )
                + p1[2] * (
                    p2[0] * p3[1]
                    - p2[1] * p3[0]
                )
            ) / 6.0

        if (
            edge_counts
            and all(
                count == 2
                for count in edge_counts.values()
            )
            and signed_volume < 0.0
        ):
            return tuple(
                (p1, p3, p2)
                for p1, p2, p3 in resolved
            )

        return resolved

    @classmethod
    def _representation_kind(
        cls,
        value: Any,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if normalized not in (
            cls.SUPPORTED_REPRESENTATION_KINDS
        ):
            raise ValueError(
                "representation_kind must be one of: "
                + ", ".join(
                    cls.SUPPORTED_REPRESENTATION_KINDS
                )
            )

        return normalized

    @staticmethod
    def _positive_finite(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be numeric"
            ) from exc

        if (
            not math.isfinite(numeric)
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be finite and positive"
            )

        return numeric
