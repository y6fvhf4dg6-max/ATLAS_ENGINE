from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any


class AtlasCanonicalHeadPhysicalFamilyBuilder:
    """
    Builds representation-specific physical geometry from an
    already physical-coordinate canonical-head triangle mesh.

    Scope:
    - relief: controlled depth compression;
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

    RELIEF_DEPTH_RATIO = 0.30

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
            compressed = cls._compress_depth(
                triangles=triangles,
                bounds=bounds,
                ratio=cls.RELIEF_DEPTH_RATIO,
            )

            physical_depth = (
                canonical_depth
                * cls.RELIEF_DEPTH_RATIO
            )

            return cls._result(
                kind=kind,
                geometry_kind="relief",
                triangles=compressed,
                support_geometry_kind="none",
                canonical_depth_mm=canonical_depth,
                physical_depth_mm=physical_depth,
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
    ) -> dict[str, Any]:
        return {
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
