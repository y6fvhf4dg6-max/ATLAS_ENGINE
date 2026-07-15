"""
ATLAS Closed Cylinder Builder v0.1

Genel amaçlı, kapalı ve manifold silindir mesh üretir.

Kullanım alanları:
- klasik sütunlar
- payeler
- kule ve baca detayları
- korkuluk elemanları
- dairesel mimari taşıyıcılar

Bu builder herhangi bir yapı türüne, OSM kimliğine veya
fixture geometrisine bağlı değildir.
"""

from math import cos, pi, sin


class AtlasClosedCylinderBuilder:
    DEFAULT_SEGMENTS = 12
    MIN_SEGMENTS = 6

    @staticmethod
    def build(
        center_x,
        center_y,
        base_z,
        radius,
        height,
        segments=None,
        metadata=None,
    ):
        center_x = float(center_x)
        center_y = float(center_y)
        base_z = float(base_z)
        radius = float(radius)
        height = float(height)

        if radius <= 0.0:
            raise ValueError(
                "radius must be greater than zero"
            )

        if height <= 0.0:
            raise ValueError(
                "height must be greater than zero"
            )

        if segments is None:
            segments = (
                AtlasClosedCylinderBuilder
                .DEFAULT_SEGMENTS
            )

        segments = int(segments)

        if (
            segments
            < AtlasClosedCylinderBuilder
            .MIN_SEGMENTS
        ):
            raise ValueError(
                "segments must be at least "
                f"{AtlasClosedCylinderBuilder.MIN_SEGMENTS}"
            )

        top_z = base_z + height

        bottom_center = (
            center_x,
            center_y,
            base_z,
        )

        top_center = (
            center_x,
            center_y,
            top_z,
        )

        bottom_ring = []
        top_ring = []

        for index in range(segments):
            angle = (
                2.0
                * pi
                * index
                / segments
            )

            x = (
                center_x
                + cos(angle) * radius
            )

            y = (
                center_y
                + sin(angle) * radius
            )

            bottom_ring.append(
                (
                    x,
                    y,
                    base_z,
                )
            )

            top_ring.append(
                (
                    x,
                    y,
                    top_z,
                )
            )

        wall_triangles = []
        bottom_triangles = []
        top_triangles = []

        for index in range(segments):
            next_index = (
                index + 1
            ) % segments

            bottom_1 = bottom_ring[index]
            bottom_2 = bottom_ring[next_index]
            top_1 = top_ring[index]
            top_2 = top_ring[next_index]

            wall_triangles.extend(
                [
                    (
                        bottom_1,
                        bottom_2,
                        top_2,
                    ),
                    (
                        bottom_1,
                        top_2,
                        top_1,
                    ),
                ]
            )

            bottom_triangles.append(
                (
                    bottom_center,
                    bottom_2,
                    bottom_1,
                )
            )

            top_triangles.append(
                (
                    top_center,
                    top_1,
                    top_2,
                )
            )

        triangles = [
            *wall_triangles,
            *bottom_triangles,
            *top_triangles,
        ]

        mesh = {
            "triangles": triangles,
            "walls": wall_triangles,
            "bottom": bottom_triangles,
            "top": top_triangles,
            "bottom_ring": bottom_ring,
            "top_ring": top_ring,
            "center": (
                center_x,
                center_y,
            ),
            "base_z": base_z,
            "top_z": top_z,
            "radius": radius,
            "height": height,
            "segments": segments,
            "triangle_count": len(
                triangles
            ),
            "geometry_type": (
                "closed_cylinder"
            ),
        }

        if metadata:
            mesh.update(
                dict(metadata)
            )

        return mesh
