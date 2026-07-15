"""
ATLAS Polyline Ribbon Prism Builder v0.1

Birbirine karşılık gelen iç ve dış polylineler arasında
kapalı, manifold bir şerit prizma üretir.

Kullanım alanları:
- sütun dizisi üzerindeki arşitrav ve saçak
- kavisli galeri çatısı
- tapınak kornişi
- doğrusal veya kavisli mimari bantlar

Builder herhangi bir yapı adına, OSM kimliğine veya
fixture geometrisine bağlı değildir.
"""


class AtlasPolylineRibbonPrismBuilder:
    @staticmethod
    def build(
        inner_path,
        outer_path,
        base_z,
        height,
        metadata=None,
    ):
        inner_path = (
            AtlasPolylineRibbonPrismBuilder
            ._clean_path(inner_path)
        )

        outer_path = (
            AtlasPolylineRibbonPrismBuilder
            ._clean_path(outer_path)
        )

        if len(inner_path) < 2:
            raise ValueError(
                "inner_path must contain at least "
                "two distinct points"
            )

        if len(inner_path) != len(outer_path):
            raise ValueError(
                "inner_path and outer_path must "
                "have matching point counts"
            )

        base_z = float(base_z)
        height = float(height)

        if height <= 0.0:
            raise ValueError(
                "height must be greater than zero"
            )

        top_z = base_z + height

        bottom_inner = [
            (
                point[0],
                point[1],
                base_z,
            )
            for point in inner_path
        ]

        bottom_outer = [
            (
                point[0],
                point[1],
                base_z,
            )
            for point in outer_path
        ]

        top_inner = [
            (
                point[0],
                point[1],
                top_z,
            )
            for point in inner_path
        ]

        top_outer = [
            (
                point[0],
                point[1],
                top_z,
            )
            for point in outer_path
        ]

        top_triangles = []
        bottom_triangles = []
        inner_wall_triangles = []
        outer_wall_triangles = []
        end_triangles = []

        for index in range(
            len(inner_path) - 1
        ):
            next_index = index + 1

            top_triangles.extend(
                [
                    (
                        top_inner[index],
                        top_outer[index],
                        top_outer[next_index],
                    ),
                    (
                        top_inner[index],
                        top_outer[next_index],
                        top_inner[next_index],
                    ),
                ]
            )

            bottom_triangles.extend(
                [
                    (
                        bottom_inner[index],
                        bottom_outer[next_index],
                        bottom_outer[index],
                    ),
                    (
                        bottom_inner[index],
                        bottom_inner[next_index],
                        bottom_outer[next_index],
                    ),
                ]
            )

            inner_wall_triangles.extend(
                [
                    (
                        bottom_inner[index],
                        top_inner[next_index],
                        top_inner[index],
                    ),
                    (
                        bottom_inner[index],
                        bottom_inner[next_index],
                        top_inner[next_index],
                    ),
                ]
            )

            outer_wall_triangles.extend(
                [
                    (
                        bottom_outer[index],
                        top_outer[index],
                        top_outer[next_index],
                    ),
                    (
                        bottom_outer[index],
                        top_outer[next_index],
                        bottom_outer[next_index],
                    ),
                ]
            )

        end_triangles.extend(
            [
                (
                    bottom_inner[0],
                    top_inner[0],
                    top_outer[0],
                ),
                (
                    bottom_inner[0],
                    top_outer[0],
                    bottom_outer[0],
                ),
                (
                    bottom_inner[-1],
                    top_outer[-1],
                    top_inner[-1],
                ),
                (
                    bottom_inner[-1],
                    bottom_outer[-1],
                    top_outer[-1],
                ),
            ]
        )

        wall_triangles = [
            *inner_wall_triangles,
            *outer_wall_triangles,
            *end_triangles,
        ]

        triangles = [
            *top_triangles,
            *bottom_triangles,
            *wall_triangles,
        ]

        mesh = {
            "triangles": triangles,
            "top_triangles": top_triangles,
            "bottom_triangles": (
                bottom_triangles
            ),
            "wall_triangles": wall_triangles,
            "inner_wall_triangles": (
                inner_wall_triangles
            ),
            "outer_wall_triangles": (
                outer_wall_triangles
            ),
            "end_triangles": end_triangles,
            "inner_path": inner_path,
            "outer_path": outer_path,
            "base_z": base_z,
            "top_z": top_z,
            "height": height,
            "point_count": len(
                inner_path
            ),
            "triangle_count": len(
                triangles
            ),
            "geometry_type": (
                "polyline_ribbon_prism"
            ),
        }

        if metadata:
            mesh.update(
                dict(metadata)
            )

        return mesh

    @staticmethod
    def _clean_path(path):
        cleaned = []

        for point in path or []:
            if len(point) < 2:
                continue

            candidate = (
                float(point[0]),
                float(point[1]),
            )

            if (
                not cleaned
                or candidate != cleaned[-1]
            ):
                cleaned.append(candidate)

        return cleaned
