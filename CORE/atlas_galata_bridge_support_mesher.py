import math


class AtlasGalataBridgeSupportMesher:
    """Galata taşıyıcı merkezlerinden kapalı ayak meshleri üretir."""

    @staticmethod
    def _normalize_axis(axis):
        axis_x = float(axis[0])
        axis_y = float(axis[1])

        length = math.hypot(
            axis_x,
            axis_y,
        )

        if length <= 1e-12:
            raise ValueError(
                "Bridge axis must have non-zero length"
            )

        return (
            axis_x / length,
            axis_y / length,
        )

    @staticmethod
    def _build_footprint(
        center,
        axis,
        support_width,
        support_depth,
    ):
        center_x = float(center[0])
        center_y = float(center[1])

        axis_x, axis_y = axis
        normal_x = -axis_y
        normal_y = axis_x

        half_depth = (
            float(support_depth) * 0.5
        )
        half_width = (
            float(support_width) * 0.5
        )

        return (
            (
                center_x
                - axis_x * half_depth
                - normal_x * half_width,
                center_y
                - axis_y * half_depth
                - normal_y * half_width,
            ),
            (
                center_x
                + axis_x * half_depth
                - normal_x * half_width,
                center_y
                + axis_y * half_depth
                - normal_y * half_width,
            ),
            (
                center_x
                + axis_x * half_depth
                + normal_x * half_width,
                center_y
                + axis_y * half_depth
                + normal_y * half_width,
            ),
            (
                center_x
                - axis_x * half_depth
                + normal_x * half_width,
                center_y
                - axis_y * half_depth
                + normal_y * half_width,
            ),
        )

    @staticmethod
    def _build_triangles(
        bottom,
        top,
    ):
        return (
            (
                bottom[0],
                bottom[2],
                bottom[1],
            ),
            (
                bottom[0],
                bottom[3],
                bottom[2],
            ),
            (
                top[0],
                top[1],
                top[2],
            ),
            (
                top[0],
                top[2],
                top[3],
            ),
            (
                bottom[0],
                bottom[1],
                top[1],
            ),
            (
                bottom[0],
                top[1],
                top[0],
            ),
            (
                bottom[1],
                bottom[2],
                top[2],
            ),
            (
                bottom[1],
                top[2],
                top[1],
            ),
            (
                bottom[2],
                bottom[3],
                top[3],
            ),
            (
                bottom[2],
                top[3],
                top[2],
            ),
            (
                bottom[3],
                bottom[0],
                top[0],
            ),
            (
                bottom[3],
                top[0],
                top[3],
            ),
        )

    @classmethod
    def build(
        cls,
        supports,
        axis,
        base_z,
        top_z,
    ):
        base_z = float(base_z)
        top_z = float(top_z)

        if top_z <= base_z:
            raise ValueError(
                "Support top_z must be greater than base_z"
            )

        normalized_axis = (
            cls._normalize_axis(axis)
        )

        meshes = []

        for support in supports:
            footprint = cls._build_footprint(
                center=support["center"],
                axis=normalized_axis,
                support_width=(
                    support["support_width"]
                ),
                support_depth=(
                    support["support_depth"]
                ),
            )

            bottom = tuple(
                (
                    x,
                    y,
                    base_z,
                )
                for x, y in footprint
            )

            top = tuple(
                (
                    x,
                    y,
                    top_z,
                )
                for x, y in footprint
            )

            meshes.append(
                {
                    "side": support["side"],
                    "center": support["center"],
                    "longitudinal_position": (
                        support[
                            "longitudinal_position"
                        ]
                    ),
                    "footprint": footprint,
                    "bottom": bottom,
                    "top": top,
                    "triangles": (
                        cls._build_triangles(
                            bottom=bottom,
                            top=top,
                        )
                    ),
                }
            )

        return tuple(meshes)
