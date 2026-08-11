from __future__ import annotations

from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from CORE.atlas_wall_hanger_profile_builder import (
    AtlasWallHangerProfileBuilder,
)
from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec


class AtlasWallFrameHangerMesher:
    @staticmethod
    def _lift_triangles(
        triangles_2d,
        *,
        z_mm: float,
        reverse: bool = False,
    ):
        triangles_3d = []

        for triangle in triangles_2d:
            points = tuple(
                (float(x), float(y), float(z_mm))
                for x, y in triangle
            )

            if reverse:
                points = (
                    points[0],
                    points[2],
                    points[1],
                )

            triangles_3d.append(points)

        return triangles_3d

    @staticmethod
    def _connect_ring(
        ring,
        *,
        z_bottom_mm: float,
        z_top_mm: float,
        reverse: bool = False,
    ):
        triangles = []

        for index in range(len(ring)):
            next_index = (index + 1) % len(ring)

            x1, y1 = ring[index]
            x2, y2 = ring[next_index]

            bottom_1 = (float(x1), float(y1), float(z_bottom_mm))
            bottom_2 = (float(x2), float(y2), float(z_bottom_mm))
            top_1 = (float(x1), float(y1), float(z_top_mm))
            top_2 = (float(x2), float(y2), float(z_top_mm))

            pair = (
                (bottom_1, bottom_2, top_2),
                (bottom_1, top_2, top_1),
            )

            if reverse:
                pair = tuple(
                    (triangle[0], triangle[2], triangle[1])
                    for triangle in pair
                )

            triangles.extend(pair)

        return triangles

    @classmethod
    def build(
        cls,
        *,
        frame_spec: AtlasWallFrameSpec,
        hanger_spec: AtlasWallHangerSpec,
        frame_depth_mm: float,
        front_recess_ring=None,
        front_recess_depth_mm=None,
    ) -> dict:
        frame_depth_mm = float(frame_depth_mm)

        if (
            front_recess_ring is None
            and front_recess_depth_mm is not None
        ):
            raise ValueError(
                "front_recess_depth_mm requires front_recess_ring"
            )

        if (
            front_recess_ring is not None
            and front_recess_depth_mm is None
        ):
            raise ValueError(
                "front_recess_ring requires front_recess_depth_mm"
            )

        if front_recess_ring is not None:
            front_recess_ring = tuple(
                (
                    float(point[0]),
                    float(point[1]),
                )
                for point in front_recess_ring
            )

            if len(front_recess_ring) < 3:
                raise ValueError(
                    "front_recess_ring must contain at least 3 points"
                )

            front_recess_depth_mm = float(
                front_recess_depth_mm
            )

            if (
                front_recess_depth_mm <= 0.0
                or front_recess_depth_mm >= frame_depth_mm
            ):
                raise ValueError(
                    "front_recess_depth_mm must be positive "
                    "and smaller than frame_depth_mm"
                )

        expected_depth_mm = (
            hanger_spec.recess_depth_mm
            + hanger_spec.front_wall_thickness_mm
        )

        if abs(frame_depth_mm - expected_depth_mm) > 1e-9:
            raise ValueError(
                "frame depth does not match hanger specification"
            )

        outer_half_x = frame_spec.outer_width_mm / 2.0
        outer_half_y = frame_spec.outer_height_mm / 2.0
        inner_half_x = frame_spec.inner_width_mm / 2.0
        inner_half_y = frame_spec.inner_height_mm / 2.0

        outer_ring = [
            (-outer_half_x, -outer_half_y),
            (outer_half_x, -outer_half_y),
            (outer_half_x, outer_half_y),
            (-outer_half_x, outer_half_y),
        ]

        inner_ring = [
            (-inner_half_x, -inner_half_y),
            (-inner_half_x, inner_half_y),
            (inner_half_x, inner_half_y),
            (inner_half_x, -inner_half_y),
        ]

        hanger_profiles = [
            AtlasWallHangerProfileBuilder.build(
                frame_spec=frame_spec,
                hanger_spec=hanger_spec,
                center_x_mm=center_x_mm,
            )
            for center_x_mm in hanger_spec.center_x_positions_mm
        ]

        hanger_rings = [
            profile["ring"]
            for profile in hanger_profiles
        ]

        front_inner_rings = [inner_ring]

        if front_recess_ring is not None:
            front_inner_rings.append(
                front_recess_ring
            )

        front_triangles_2d = (
            AtlasCastleShellTriangulator.triangulate(
                outer_ring=outer_ring,
                inner_rings=front_inner_rings,
            )
        )

        back_triangles_2d = (
            AtlasCastleShellTriangulator.triangulate(
                outer_ring=outer_ring,
                inner_rings=[
                    inner_ring,
                    *hanger_rings,
                ],
            )
        )

        if not front_triangles_2d or not back_triangles_2d:
            raise ValueError(
                "wall frame surface triangulation failed"
            )

        triangles = []

        triangles.extend(
            cls._lift_triangles(
                front_triangles_2d,
                z_mm=frame_depth_mm,
            )
        )

        triangles.extend(
            cls._lift_triangles(
                back_triangles_2d,
                z_mm=0.0,
                reverse=True,
            )
        )

        triangles.extend(
            cls._connect_ring(
                outer_ring,
                z_bottom_mm=0.0,
                z_top_mm=frame_depth_mm,
            )
        )

        triangles.extend(
            cls._connect_ring(
                inner_ring,
                z_bottom_mm=0.0,
                z_top_mm=frame_depth_mm,
                reverse=True,
            )
        )

        if front_recess_ring is not None:
            recess_floor_z_mm = (
                frame_depth_mm
                - front_recess_depth_mm
            )

            recess_floor_triangles_2d = (
                AtlasCastleShellTriangulator.triangulate(
                    outer_ring=front_recess_ring,
                )
            )

            if not recess_floor_triangles_2d:
                raise ValueError(
                    "front recess floor triangulation failed"
                )

            triangles.extend(
                cls._lift_triangles(
                    recess_floor_triangles_2d,
                    z_mm=recess_floor_z_mm,
                )
            )

            triangles.extend(
                cls._connect_ring(
                    front_recess_ring,
                    z_bottom_mm=recess_floor_z_mm,
                    z_top_mm=frame_depth_mm,
                    reverse=True,
                )
            )

        for hanger_ring in hanger_rings:
            floor_triangles_2d = (
                AtlasCastleShellTriangulator.triangulate(
                    outer_ring=hanger_ring,
                )
            )

            if not floor_triangles_2d:
                raise ValueError(
                    "hanger recess floor triangulation failed"
                )

            triangles.extend(
                cls._lift_triangles(
                    floor_triangles_2d,
                    z_mm=hanger_spec.recess_depth_mm,
                    reverse=True,
                )
            )

            triangles.extend(
                cls._connect_ring(
                    hanger_ring,
                    z_bottom_mm=0.0,
                    z_top_mm=hanger_spec.recess_depth_mm,
                    reverse=True,
                )
            )

        return {
            "type": "wall_frame_with_hidden_hangers",
            "outer_width_mm": frame_spec.outer_width_mm,
            "outer_height_mm": frame_spec.outer_height_mm,
            "inner_width_mm": frame_spec.inner_width_mm,
            "inner_height_mm": frame_spec.inner_height_mm,
            "frame_width_mm": frame_spec.frame_width_mm,
            "depth_mm": frame_depth_mm,
            "hanger_count": hanger_spec.hanger_count,
            "hanger_center_x_positions_mm": (
                hanger_spec.center_x_positions_mm
            ),
            "recess_depth_mm": hanger_spec.recess_depth_mm,
            "front_wall_thickness_mm": (
                hanger_spec.front_wall_thickness_mm
            ),
            "front_recess_depth_mm": (
                front_recess_depth_mm
                if front_recess_ring is not None
                else None
            ),
            "front_recess_ring": (
                front_recess_ring
                if front_recess_ring is not None
                else None
            ),
            "triangles": triangles,
        }
