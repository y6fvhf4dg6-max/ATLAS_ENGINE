from __future__ import annotations

import math


class AtlasChurchTowerWindowMesher:
    WINDOW_DEPTH_RATIO = 0.08
    WINDOW_WIDTH_RATIO = 0.28
    WINDOW_HEIGHT_RATIO = 0.16
    WINDOW_STAGE_BOTTOM_RATIO = 0.58
    WINDOW_STAGE_TOP_RATIO = 0.78

    @staticmethod
    def _normalize(vector):
        x, y = vector
        length = math.hypot(x, y)

        if length <= 1e-12:
            raise ValueError(
                "Window face direction must have measurable length"
            )

        return (
            x / length,
            y / length,
        )

    @classmethod
    def _window_prism(
        cls,
        *,
        center,
        tangent,
        normal,
        width,
        height,
        depth,
        bottom_z,
    ):
        center_x, center_y = center
        tangent_x, tangent_y = cls._normalize(
            tangent
        )
        normal_x, normal_y = cls._normalize(
            normal
        )

        half_width = float(width) / 2.0
        half_depth = float(depth) / 2.0
        top_z = float(bottom_z) + float(height)

        def point(
            tangent_offset,
            normal_offset,
            z,
        ):
            return (
                center_x
                + tangent_x * tangent_offset
                + normal_x * normal_offset,
                center_y
                + tangent_y * tangent_offset
                + normal_y * normal_offset,
                float(z),
            )

        back_left_bottom = point(
            -half_width,
            -half_depth,
            bottom_z,
        )
        back_right_bottom = point(
            half_width,
            -half_depth,
            bottom_z,
        )
        front_right_bottom = point(
            half_width,
            half_depth,
            bottom_z,
        )
        front_left_bottom = point(
            -half_width,
            half_depth,
            bottom_z,
        )

        back_left_top = point(
            -half_width,
            -half_depth,
            top_z,
        )
        back_right_top = point(
            half_width,
            -half_depth,
            top_z,
        )
        front_right_top = point(
            half_width,
            half_depth,
            top_z,
        )
        front_left_top = point(
            -half_width,
            half_depth,
            top_z,
        )

        triangles = [
            (
                back_left_bottom,
                back_right_bottom,
                front_right_bottom,
            ),
            (
                back_left_bottom,
                front_right_bottom,
                front_left_bottom,
            ),
            (
                back_left_top,
                front_right_top,
                back_right_top,
            ),
            (
                back_left_top,
                front_left_top,
                front_right_top,
            ),
            (
                back_left_bottom,
                back_left_top,
                back_right_top,
            ),
            (
                back_left_bottom,
                back_right_top,
                back_right_bottom,
            ),
            (
                back_right_bottom,
                back_right_top,
                front_right_top,
            ),
            (
                back_right_bottom,
                front_right_top,
                front_right_bottom,
            ),
            (
                front_right_bottom,
                front_right_top,
                front_left_top,
            ),
            (
                front_right_bottom,
                front_left_top,
                front_left_bottom,
            ),
            (
                front_left_bottom,
                front_left_top,
                back_left_top,
            ),
            (
                front_left_bottom,
                back_left_top,
                back_left_bottom,
            ),
        ]

        return {
            "type": "church_tower_window",
            "triangles": triangles,
            "bottom_z": float(bottom_z),
            "top_z": float(top_z),
            "width": float(width),
            "height": float(height),
            "depth": float(depth),
        }

    @classmethod
    def _build_face_windows(
        cls,
        *,
        tower,
    ):
        ring = tuple(
            tower["body_top_ring"]
        )

        if len(ring) < 4:
            return []

        body_top_z = float(
            tower["body_top_z"]
        )
        stage_bottom_z = (
            body_top_z
            * cls.WINDOW_STAGE_BOTTOM_RATIO
        )
        stage_top_z = (
            body_top_z
            * cls.WINDOW_STAGE_TOP_RATIO
        )
        stage_height = max(
            stage_top_z - stage_bottom_z,
            body_top_z * 0.08,
        )

        minimum_span = min(
            float(tower["longitudinal_span"]),
            float(tower["lateral_span"]),
        )

        window_width = max(
            minimum_span
            * cls.WINDOW_WIDTH_RATIO,
            minimum_span * 0.12,
        )
        window_depth = max(
            minimum_span
            * cls.WINDOW_DEPTH_RATIO,
            minimum_span * 0.04,
        )
        window_height = max(
            body_top_z
            * cls.WINDOW_HEIGHT_RATIO,
            stage_height,
        )

        center_x = sum(
            point[0]
            for point in ring
        ) / len(ring)
        center_y = sum(
            point[1]
            for point in ring
        ) / len(ring)

        windows = []

        for index, first in enumerate(ring):
            second = ring[
                (index + 1) % len(ring)
            ]

            face_center_x = (
                float(first[0])
                + float(second[0])
            ) / 2.0
            face_center_y = (
                float(first[1])
                + float(second[1])
            ) / 2.0

            tangent = (
                float(second[0])
                - float(first[0]),
                float(second[1])
                - float(first[1]),
            )
            outward = (
                face_center_x - center_x,
                face_center_y - center_y,
            )

            windows.append(
                cls._window_prism(
                    center=(
                        face_center_x,
                        face_center_y,
                    ),
                    tangent=tangent,
                    normal=outward,
                    width=window_width,
                    height=window_height,
                    depth=window_depth,
                    bottom_z=stage_bottom_z,
                )
            )

        return windows

    @classmethod
    def apply(
        cls,
        tower_system,
    ):
        if not isinstance(
            tower_system,
            dict,
        ):
            raise TypeError(
                "tower_system must be a dictionary"
            )

        if (
            tower_system.get("type")
            != "church_tower_system"
        ):
            raise ValueError(
                "tower_system must be church_tower_system"
            )

        towers = []

        for source_tower in tower_system.get(
            "towers",
            (),
        ):
            tower = dict(
                source_tower
            )

            window_meshes = (
                cls._build_face_windows(
                    tower=tower,
                )
            )

            tower["window_stage"] = {
                "type": "bell_stage",
                "window_count": len(
                    window_meshes
                ),
            }
            tower["window_meshes"] = (
                window_meshes
            )
            tower["window_triangles"] = [
                triangle
                for window in window_meshes
                for triangle in window["triangles"]
            ]
            tower["triangles"] = [
                *tower.get("triangles", ()),
                *tower["window_triangles"],
            ]

            towers.append(
                tower
            )

        return {
            **tower_system,
            "towers": towers,
            "window_meshes": [
                window
                for tower in towers
                for window in tower[
                    "window_meshes"
                ]
            ],
            "window_triangles": [
                triangle
                for tower in towers
                for triangle in tower[
                    "window_triangles"
                ]
            ],
            "triangles": [
                triangle
                for tower in towers
                for triangle in tower[
                    "triangles"
                ]
            ],
        }
