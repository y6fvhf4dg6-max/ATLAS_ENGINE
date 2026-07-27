from __future__ import annotations

from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec


class AtlasLabelPlateMesher:
    @staticmethod
    def build(
        *,
        spec: AtlasLabelPlateSpec,
    ) -> dict:
        half_width = spec.width_mm / 2.0
        half_height = spec.height_mm / 2.0
        depth = spec.depth_mm

        bottom = (
            (-half_width, -half_height, 0.0),
            (half_width, -half_height, 0.0),
            (half_width, half_height, 0.0),
            (-half_width, half_height, 0.0),
        )
        top = tuple(
            (x, y, depth)
            for x, y, _ in bottom
        )

        triangles = [
            (bottom[0], bottom[2], bottom[1]),
            (bottom[0], bottom[3], bottom[2]),
            (top[0], top[1], top[2]),
            (top[0], top[2], top[3]),
        ]

        for index in range(4):
            next_index = (index + 1) % 4
            triangles.extend(
                (
                    (
                        bottom[index],
                        bottom[next_index],
                        top[next_index],
                    ),
                    (
                        bottom[index],
                        top[next_index],
                        top[index],
                    ),
                )
            )

        return {
            "type": "label_plate",
            "width_mm": spec.width_mm,
            "height_mm": spec.height_mm,
            "depth_mm": spec.depth_mm,
            "triangles": triangles,
        }
