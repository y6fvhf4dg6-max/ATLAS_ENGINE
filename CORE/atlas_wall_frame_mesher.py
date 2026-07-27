from __future__ import annotations

from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


class AtlasWallFrameMesher:
    @staticmethod
    def build(
        *,
        spec: AtlasWallFrameSpec,
        depth_mm: float,
    ) -> dict:
        depth_mm = float(depth_mm)

        if depth_mm <= 0.0:
            raise ValueError("depth_mm must be positive")

        outer_half_x = spec.outer_width_mm / 2.0
        outer_half_y = spec.outer_height_mm / 2.0
        inner_half_x = spec.inner_width_mm / 2.0
        inner_half_y = spec.inner_height_mm / 2.0

        outer_bottom = (
            (-outer_half_x, -outer_half_y, 0.0),
            (outer_half_x, -outer_half_y, 0.0),
            (outer_half_x, outer_half_y, 0.0),
            (-outer_half_x, outer_half_y, 0.0),
        )
        outer_top = tuple(
            (x, y, depth_mm)
            for x, y, _ in outer_bottom
        )

        inner_bottom = (
            (-inner_half_x, -inner_half_y, 0.0),
            (inner_half_x, -inner_half_y, 0.0),
            (inner_half_x, inner_half_y, 0.0),
            (-inner_half_x, inner_half_y, 0.0),
        )
        inner_top = tuple(
            (x, y, depth_mm)
            for x, y, _ in inner_bottom
        )

        triangles = []

        for index in range(4):
            next_index = (index + 1) % 4

            triangles.extend(
                (
                    (
                        outer_bottom[index],
                        outer_bottom[next_index],
                        outer_top[next_index],
                    ),
                    (
                        outer_bottom[index],
                        outer_top[next_index],
                        outer_top[index],
                    ),
                    (
                        inner_bottom[index],
                        inner_top[next_index],
                        inner_bottom[next_index],
                    ),
                    (
                        inner_bottom[index],
                        inner_top[index],
                        inner_top[next_index],
                    ),
                    (
                        outer_top[index],
                        outer_top[next_index],
                        inner_top[next_index],
                    ),
                    (
                        outer_top[index],
                        inner_top[next_index],
                        inner_top[index],
                    ),
                    (
                        outer_bottom[index],
                        inner_bottom[next_index],
                        outer_bottom[next_index],
                    ),
                    (
                        outer_bottom[index],
                        inner_bottom[index],
                        inner_bottom[next_index],
                    ),
                )
            )

        return {
            "type": "wall_frame",
            "outer_width_mm": spec.outer_width_mm,
            "outer_height_mm": spec.outer_height_mm,
            "inner_width_mm": spec.inner_width_mm,
            "inner_height_mm": spec.inner_height_mm,
            "frame_width_mm": spec.frame_width_mm,
            "depth_mm": depth_mm,
            "triangles": triangles,
        }
