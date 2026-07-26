import math

from CORE.atlas_bridge_builder import AtlasBridgeGeometry
from CORE.atlas_lighthouse_builder import AtlasLighthouseGeometry
from CORE.atlas_tower_builder import AtlasTowerGeometry


class AtlasLandmarkGeometryMesher:
    @classmethod
    def build(cls, geometry):
        if isinstance(geometry, AtlasBridgeGeometry):
            return cls._build_bridge_mesh(geometry)

        if isinstance(geometry, AtlasLighthouseGeometry):
            return cls._build_lighthouse_mesh(geometry)

        if isinstance(geometry, AtlasTowerGeometry):
            return cls._build_tower_mesh(geometry)

        raise TypeError(
            f"Unsupported landmark geometry: {type(geometry).__name__}"
        )

    @staticmethod
    def _fan_triangulate(ring, reverse=False):
        triangles = []
        if len(ring) < 3:
            return triangles

        anchor = ring[0]
        for index in range(1, len(ring) - 1):
            triangle = (
                anchor,
                ring[index],
                ring[index + 1],
            )
            if reverse:
                triangle = (
                    triangle[0],
                    triangle[2],
                    triangle[1],
                )
            triangles.append(triangle)

        return triangles

    @staticmethod
    def _center_fan_triangulate(ring, reverse=False):
        if len(ring) < 3:
            return []

        center = (
            sum(point[0] for point in ring) / len(ring),
            sum(point[1] for point in ring) / len(ring),
            sum(point[2] for point in ring) / len(ring),
        )

        triangles = []

        for index in range(len(ring)):
            next_index = (index + 1) % len(ring)

            triangle = (
                center,
                ring[index],
                ring[next_index],
            )

            if reverse:
                triangle = (
                    triangle[0],
                    triangle[2],
                    triangle[1],
                )

            triangles.append(triangle)

        return triangles

    @staticmethod
    def _connect_rings(lower, upper):
        triangles = []
        count = len(lower)

        for index in range(count):
            next_index = (index + 1) % count

            a = lower[index]
            b = lower[next_index]
            c = upper[next_index]
            d = upper[index]

            triangles.append((a, b, c))
            triangles.append((a, c, d))

        return triangles

    @classmethod
    def _build_bridge_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError("Bridge footprint requires at least 3 points")

        deck_thickness_m = float(
            geometry.metadata.get(
                "bridge_deck_thickness_m",
                geometry.height_m,
            )
        )
        top_z = float(geometry.height_m)
        bottom_z = max(0.0, top_z - deck_thickness_m)

        bottom = tuple(
            (x, y, bottom_z)
            for x, y in footprint
        )
        top = tuple(
            (x, y, top_z)
            for x, y in footprint
        )

        walls = []
        triangles = []

        triangles.extend(
            cls._fan_triangulate(bottom, reverse=True)
        )
        triangles.extend(
            cls._fan_triangulate(top)
        )

        for index in range(len(bottom)):
            next_index = (index + 1) % len(bottom)

            wall = (
                bottom[index],
                bottom[next_index],
                top[next_index],
                top[index],
            )
            walls.append(wall)

            triangles.append(
                (
                    bottom[index],
                    bottom[next_index],
                    top[next_index],
                )
            )
            triangles.append(
                (
                    bottom[index],
                    top[next_index],
                    top[index],
                )
            )

        piers = []
        pier_positions = tuple(
            geometry.metadata.get("bridge_pier_positions", ())
        )

        if pier_positions:
            edge_dx = footprint[1][0] - footprint[0][0]
            edge_dy = footprint[1][1] - footprint[0][1]
            edge_length = math.hypot(edge_dx, edge_dy)

            if edge_length <= 0.0:
                raise ValueError("Bridge footprint has a zero-length axis")

            axis_x = edge_dx / edge_length
            axis_y = edge_dy / edge_length
            normal_x = -axis_y
            normal_y = axis_x

            pier_width_m = float(
                geometry.metadata.get("bridge_pier_width_m", 2.0)
            )
            pier_depth_m = float(
                geometry.metadata.get("bridge_pier_depth_m", 1.0)
            )
            pier_base_m = float(
                geometry.metadata.get("bridge_pier_base_m", 0.0)
            )
            pier_top_m = float(
                geometry.metadata.get("bridge_pier_top_m", bottom_z)
            )

            half_width = pier_width_m / 2.0
            half_depth = pier_depth_m / 2.0

            for center_x, center_y in pier_positions:
                center_x = float(center_x)
                center_y = float(center_y)

                pier_footprint = (
                    (
                        center_x - axis_x * half_depth - normal_x * half_width,
                        center_y - axis_y * half_depth - normal_y * half_width,
                    ),
                    (
                        center_x + axis_x * half_depth - normal_x * half_width,
                        center_y + axis_y * half_depth - normal_y * half_width,
                    ),
                    (
                        center_x + axis_x * half_depth + normal_x * half_width,
                        center_y + axis_y * half_depth + normal_y * half_width,
                    ),
                    (
                        center_x - axis_x * half_depth + normal_x * half_width,
                        center_y - axis_y * half_depth + normal_y * half_width,
                    ),
                )

                pier_bottom = tuple(
                    (x, y, pier_base_m)
                    for x, y in pier_footprint
                )
                pier_top = tuple(
                    (x, y, pier_top_m)
                    for x, y in pier_footprint
                )

                pier_triangles = []
                pier_triangles.extend(
                    cls._fan_triangulate(pier_bottom, reverse=True)
                )
                pier_triangles.extend(
                    cls._fan_triangulate(pier_top)
                )
                pier_triangles.extend(
                    cls._connect_rings(pier_bottom, pier_top)
                )

                piers.append(
                    {
                        "bottom": pier_bottom,
                        "top": pier_top,
                        "triangles": pier_triangles,
                    }
                )
                triangles.extend(pier_triangles)

        return {
            "type": "bridge",
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "piers": piers,
            "triangles": triangles,
            "metadata": dict(geometry.metadata),
        }

    @classmethod
    def _build_tower_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError("Tower footprint requires at least 3 points")

        if geometry.profile == "observation":
            return cls._build_observation_tower_mesh(geometry)

        bottom = tuple(
            (x, y, 0.0)
            for x, y in footprint
        )
        top = tuple(
            (x, y, float(geometry.height_m))
            for x, y in footprint
        )

        walls = []
        triangles = []

        triangles.extend(
            cls._fan_triangulate(bottom, reverse=True)
        )
        triangles.extend(
            cls._fan_triangulate(top)
        )

        for index in range(len(bottom)):
            next_index = (index + 1) % len(bottom)

            wall = (
                bottom[index],
                bottom[next_index],
                top[next_index],
                top[index],
            )
            walls.append(wall)

            triangles.append(
                (
                    bottom[index],
                    bottom[next_index],
                    top[next_index],
                )
            )
            triangles.append(
                (
                    bottom[index],
                    top[next_index],
                    top[index],
                )
            )

        return {
            "type": "tower",
            "profile": geometry.profile,
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
        }

    @classmethod
    def _build_observation_tower_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        center_x = sum(x for x, _ in footprint) / len(footprint)
        center_y = sum(y for _, y in footprint) / len(footprint)

        base_radius = max(
            math.hypot(x - center_x, y - center_y)
            for x, y in footprint
        )

        levels = (
            (0.00, 1.00, "prismatic"),
            (0.58, 1.00, "prismatic"),
            (0.62, 1.20, "radial"),
            (0.66, 1.45, "radial"),
            (0.70, 1.45, "radial"),
            (0.73, 1.62, "radial"),
            (0.77, 1.62, "radial"),
            (0.80, 2.05, "radial"),
            (0.88, 2.05, "radial"),
            (0.92, 1.88, "radial"),
            (0.97, 1.35, "radial"),
            (1.00, 0.55, "radial"),
        )

        rings = []
        segments = 16

        min_x = min(x for x, _ in footprint)
        max_x = max(x for x, _ in footprint)
        min_y = min(y for _, y in footprint)
        max_y = max(y for _, y in footprint)

        half_width = (max_x - min_x) / 2.0
        half_height = (max_y - min_y) / 2.0

        prismatic_xy = []

        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            direction_x = math.cos(angle)
            direction_y = math.sin(angle)

            scale_candidates = []

            if abs(direction_x) > 1e-12:
                scale_candidates.append(
                    half_width / abs(direction_x)
                )

            if abs(direction_y) > 1e-12:
                scale_candidates.append(
                    half_height / abs(direction_y)
                )

            distance = min(scale_candidates)

            prismatic_xy.append(
                (
                    center_x + direction_x * distance,
                    center_y + direction_y * distance,
                )
            )

        body_scale = 0.78

        prismatic_xy = tuple(
            (
                center_x + (x - center_x) * body_scale,
                center_y + (y - center_y) * body_scale,
            )
            for x, y in prismatic_xy
        )

        for height_ratio, radius_ratio, ring_kind in levels:
            z = float(geometry.height_m) * height_ratio

            if ring_kind == "prismatic":
                ring = tuple(
                    (x, y, z)
                    for x, y in prismatic_xy
                )
            else:
                radius = base_radius * radius_ratio
                ring = tuple(
                    (
                        center_x + radius * math.cos(
                            2.0 * math.pi * index / segments
                        ),
                        center_y + radius * math.sin(
                            2.0 * math.pi * index / segments
                        ),
                        z,
                    )
                    for index in range(segments)
                )

            rings.append(ring)

        triangles = []
        walls = []

        triangles.extend(
            cls._center_fan_triangulate(rings[0], reverse=True)
        )

        for lower, upper in zip(rings, rings[1:]):
            triangles.extend(
                cls._connect_rings(lower, upper)
            )

            for index in range(segments):
                next_index = (index + 1) % segments
                walls.append(
                    (
                        lower[index],
                        lower[next_index],
                        upper[next_index],
                        upper[index],
                    )
                )

        triangles.extend(
            cls._center_fan_triangulate(rings[-1])
        )

        return {
            "type": "tower",
            "profile": "observation",
            "bottom": rings[0],
            "top": rings[-1],
            "rings": tuple(rings),
            "walls": walls,
            "triangles": triangles,
        }

    @classmethod
    def _build_lighthouse_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError(
                "Lighthouse footprint requires at least 3 points"
            )

        center_x = sum(x for x, _ in footprint) / len(footprint)
        center_y = sum(y for _, y in footprint) / len(footprint)

        base_radius = max(
            math.hypot(x - center_x, y - center_y)
            for x, y in footprint
        )

        levels = (
            (0.00, 1.00),
            (0.62, 0.72),
            (0.72, 1.00),
            (0.80, 1.00),
            (0.88, 0.72),
            (0.95, 0.72),
            (1.00, 0.18),
        )

        segments = 16
        rings = []

        for height_ratio, radius_ratio in levels:
            z = float(geometry.height_m) * height_ratio
            radius = base_radius * radius_ratio

            ring = tuple(
                (
                    center_x + radius * math.cos(
                        2.0 * math.pi * index / segments
                    ),
                    center_y + radius * math.sin(
                        2.0 * math.pi * index / segments
                    ),
                    z,
                )
                for index in range(segments)
            )
            rings.append(ring)

        triangles = []
        triangles.extend(
            cls._fan_triangulate(rings[0], reverse=True)
        )

        for lower, upper in zip(rings, rings[1:]):
            triangles.extend(
                cls._connect_rings(lower, upper)
            )

        triangles.extend(
            cls._fan_triangulate(rings[-1])
        )

        return {
            "type": "lighthouse",
            "profile": "multistage",
            "bottom": rings[0],
            "top": rings[-1],
            "rings": tuple(rings),
            "walls": [],
            "triangles": triangles,
        }
