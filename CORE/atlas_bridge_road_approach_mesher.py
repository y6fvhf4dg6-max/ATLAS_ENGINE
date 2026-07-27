import math


class AtlasBridgeRoadApproachMesher:
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
                "Outward axis must have non-zero length"
            )

        return (
            axis_x / length,
            axis_y / length,
        )

    @staticmethod
    def _append_quad(
        triangles,
        first,
        second,
        third,
        fourth,
        reverse=False,
    ):
        if reverse:
            triangles.extend(
                (
                    (first, third, second),
                    (first, fourth, third),
                )
            )
        else:
            triangles.extend(
                (
                    (first, second, third),
                    (first, third, fourth),
                )
            )

    @classmethod
    def build(
        cls,
        start_edge,
        outward_axis,
        profile,
        target_edge=None,
    ):
        if len(start_edge) != 2:
            raise ValueError(
                "Approach start edge must contain two points"
            )

        first_xy = (
            float(start_edge[0][0]),
            float(start_edge[0][1]),
        )
        second_xy = (
            float(start_edge[1][0]),
            float(start_edge[1][1]),
        )

        if (
            abs(first_xy[0] - second_xy[0]) <= 1e-12
            and abs(first_xy[1] - second_xy[1]) <= 1e-12
        ):
            raise ValueError(
                "Approach start edge must have non-zero width"
            )

        axis_x, axis_y = cls._normalize_axis(
            outward_axis
        )

        if target_edge is None:
            end_first_xy = (
                first_xy[0]
                + axis_x * profile.length_mm,
                first_xy[1]
                + axis_y * profile.length_mm,
            )
            end_second_xy = (
                second_xy[0]
                + axis_x * profile.length_mm,
                second_xy[1]
                + axis_y * profile.length_mm,
            )
        else:
            if len(target_edge) != 2:
                raise ValueError(
                    "Approach target edge must contain two points"
                )

            end_first_xy = (
                float(target_edge[0][0]),
                float(target_edge[0][1]),
            )
            end_second_xy = (
                float(target_edge[1][0]),
                float(target_edge[1][1]),
            )

            if (
                abs(
                    end_first_xy[0]
                    - end_second_xy[0]
                ) <= 1e-12
                and abs(
                    end_first_xy[1]
                    - end_second_xy[1]
                ) <= 1e-12
            ):
                raise ValueError(
                    "Approach target edge must have non-zero width"
                )

        top = (
            (
                first_xy[0],
                first_xy[1],
                profile.top_z_at(0.0),
            ),
            (
                second_xy[0],
                second_xy[1],
                profile.top_z_at(0.0),
            ),
            (
                end_first_xy[0],
                end_first_xy[1],
                profile.top_z_at(1.0),
            ),
            (
                end_second_xy[0],
                end_second_xy[1],
                profile.top_z_at(1.0),
            ),
        )

        bottom = (
            (
                first_xy[0],
                first_xy[1],
                profile.bottom_z_at(0.0),
            ),
            (
                second_xy[0],
                second_xy[1],
                profile.bottom_z_at(0.0),
            ),
            (
                end_first_xy[0],
                end_first_xy[1],
                profile.bottom_z_at(1.0),
            ),
            (
                end_second_xy[0],
                end_second_xy[1],
                profile.bottom_z_at(1.0),
            ),
        )

        triangles = []

        cls._append_quad(
            triangles,
            top[0],
            top[2],
            top[3],
            top[1],
        )

        cls._append_quad(
            triangles,
            bottom[0],
            bottom[1],
            bottom[3],
            bottom[2],
            reverse=True,
        )

        cls._append_quad(
            triangles,
            bottom[0],
            top[0],
            top[1],
            bottom[1],
        )

        cls._append_quad(
            triangles,
            bottom[2],
            bottom[3],
            top[3],
            top[2],
        )

        cls._append_quad(
            triangles,
            bottom[0],
            bottom[2],
            top[2],
            top[0],
        )

        cls._append_quad(
            triangles,
            bottom[1],
            top[1],
            top[3],
            bottom[3],
        )

        return {
            "top": top,
            "bottom": bottom,
            "triangles": tuple(triangles),
            "outward_axis": (
                axis_x,
                axis_y,
            ),
            "length_mm": profile.length_mm,
            "bridge_top_z": profile.bridge_top_z,
            "road_top_z": profile.road_top_z,
            "deck_thickness_mm": (
                profile.deck_thickness_mm
            ),
        }
