import math


class AtlasBridgeRoadApproachTargetResolver:
    DEFAULT_MAX_SEARCH_DISTANCE_MM = 10.0

    @staticmethod
    def _normalize(axis):
        axis_x = float(axis[0])
        axis_y = float(axis[1])

        length = math.hypot(axis_x, axis_y)

        if length <= 1e-12:
            raise ValueError(
                "Outward axis must have non-zero length"
            )

        return (
            axis_x / length,
            axis_y / length,
        )

    @staticmethod
    def _segment_nearest_point(
        point,
        first,
        second,
    ):
        point_x, point_y = point
        first_x, first_y = first[0], first[1]
        second_x, second_y = second[0], second[1]

        delta_x = second_x - first_x
        delta_y = second_y - first_y

        length_squared = (
            delta_x * delta_x
            + delta_y * delta_y
        )

        if length_squared <= 1e-18:
            ratio = 0.0
        else:
            ratio = (
                (point_x - first_x) * delta_x
                + (point_y - first_y) * delta_y
            ) / length_squared

            ratio = max(
                0.0,
                min(1.0, ratio),
            )

        return (
            first_x + ratio * delta_x,
            first_y + ratio * delta_y,
            first[2] + ratio * (
                second[2] - first[2]
            ),
        )

    @classmethod
    def _nearest_road_point(
        cls,
        point,
        road_meshes,
    ):
        best = None

        for mesh_index, mesh in enumerate(
            road_meshes
        ):
            for triangle in mesh.get(
                "triangles",
                (),
            ):
                for first, second in (
                    (triangle[0], triangle[1]),
                    (triangle[1], triangle[2]),
                    (triangle[2], triangle[0]),
                ):
                    nearest = cls._segment_nearest_point(
                        point,
                        first,
                        second,
                    )

                    distance = math.hypot(
                        nearest[0] - point[0],
                        nearest[1] - point[1],
                    )

                    if (
                        best is None
                        or distance < best["distance"]
                    ):
                        best = {
                            "distance": distance,
                            "point": nearest,
                            "mesh_index": mesh_index,
                        }

        return best

    @classmethod
    def resolve(
        cls,
        start_edge,
        outward_axis,
        road_meshes,
        max_search_distance_mm=None,
    ):
        road_meshes = tuple(road_meshes)

        if not road_meshes:
            raise ValueError(
                "At least one road mesh is required"
            )

        if len(start_edge) != 2:
            raise ValueError(
                "Start edge must contain two points"
            )

        first = (
            float(start_edge[0][0]),
            float(start_edge[0][1]),
        )
        second = (
            float(start_edge[1][0]),
            float(start_edge[1][1]),
        )

        edge_x = second[0] - first[0]
        edge_y = second[1] - first[1]
        width = math.hypot(edge_x, edge_y)

        if width <= 1e-12:
            raise ValueError(
                "Start edge must have non-zero width"
            )

        axis_x, axis_y = cls._normalize(
            outward_axis
        )

        center = (
            (first[0] + second[0]) / 2.0,
            (first[1] + second[1]) / 2.0,
        )

        nearest = cls._nearest_road_point(
            center,
            road_meshes,
        )

        if nearest is None:
            raise ValueError(
                "Could not resolve a road target"
            )

        max_search_distance_mm = (
            cls.DEFAULT_MAX_SEARCH_DISTANCE_MM
            if max_search_distance_mm is None
            else float(max_search_distance_mm)
        )

        if nearest["distance"] > max_search_distance_mm:
            raise ValueError(
                "Nearest road is outside search distance"
            )

        offset_x = (
            nearest["point"][0]
            - center[0]
        )
        offset_y = (
            nearest["point"][1]
            - center[1]
        )

        projected_length = (
            offset_x * axis_x
            + offset_y * axis_y
        )

        if projected_length <= 1e-9:
            projected_length = nearest["distance"]

        target_center = (
            center[0]
            + axis_x * projected_length,
            center[1]
            + axis_y * projected_length,
        )

        half_edge_x = edge_x / 2.0
        half_edge_y = edge_y / 2.0

        target_edge = (
            (
                target_center[0] - half_edge_x,
                target_center[1] - half_edge_y,
            ),
            (
                target_center[0] + half_edge_x,
                target_center[1] + half_edge_y,
            ),
        )

        return {
            "target_edge": target_edge,
            "length_mm": projected_length,
            "road_top_z": float(
                nearest["point"][2]
            ),
            "target_center": target_center,
            "road_mesh_index": nearest[
                "mesh_index"
            ],
            "source_distance_mm": nearest[
                "distance"
            ],
        }
