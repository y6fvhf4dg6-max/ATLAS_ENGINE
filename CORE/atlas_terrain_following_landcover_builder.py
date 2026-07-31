"""
ATLAS Terrain-Following Landcover Builder v0.1

Birleşik land-cover yüzeylerini terrain üst kotunu takip eden,
yalnız üst yüzeyden oluşan ince görsel katmanlara dönüştürür.

Özellikler:
- Dikey yan duvar üretmez.
- Alt yüzey üretmez.
- Ürün sınırına gerçek geometrik kırpma uygular.
- Her köşenin Z değeri terrain örneklemesi + sabit ofsettir.
"""

from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient

from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator


class AtlasTerrainFollowingLandcoverBuilder:
    @staticmethod
    def build(
        surfaces,
        terrain_mesh,
        height_mm,
        coordinate_engine=None,
    ):
        if height_mm <= 0.0:
            raise ValueError(
                "height_mm must be positive"
            )

        if not surfaces:
            return []

        size_x_mm, size_y_mm = (
            AtlasTerrainFollowingLandcoverBuilder
            ._terrain_size(terrain_mesh)
        )

        meshes = []

        for surface in surfaces:
            geometry = surface.get("geometry", [])

            if coordinate_engine is not None:
                geometry = (
                    coordinate_engine
                    .geometry_to_stl_mm(
                        geometry
                    )
                )

            clipped_polygons = (
                AtlasTerrainFollowingLandcoverBuilder
                ._clip_polygon_to_bounds(
                    points=geometry,
                    min_x=0.0,
                    max_x=size_x_mm,
                    min_y=0.0,
                    max_y=size_y_mm,
                )
            )

            for polygon_index, points in enumerate(
                clipped_polygons
            ):
                triangles = (
                    AtlasTerrainFollowingLandcoverBuilder
                    ._build_from_terrain_triangles(
                        landcover_points=points,
                        terrain_mesh=terrain_mesh,
                        height_mm=height_mm,
                    )
                )

                if not triangles:
                    continue

                surface_type = surface.get(
                    "surface_type",
                    "landcover",
                )

                meshes.append(
                    {
                        "type": (
                            "terrain_following_landcover"
                        ),
                        "surface_id": surface.get("id"),
                        "surface_part_index": polygon_index,
                        "surface_type": surface_type,
                        "park_type": surface.get(
                            "park_type",
                            f"worldcover:{surface_type}",
                        ),
                        "source": surface.get(
                            "source",
                            "worldcover",
                        ),
                        "height_mm": height_mm,
                        "bottom": [],
                        "top": [],
                        "walls": [],
                        "triangles": triangles,
                        "placement_mode": (
                            "terrain_following"
                        ),
                    }
                )

        return meshes

    @staticmethod
    def _build_from_terrain_triangles(
        landcover_points,
        terrain_mesh,
        height_mm,
    ):
        top_points = terrain_mesh.get("top_points")

        if not top_points:
            return []

        row_count = len(top_points)

        if row_count < 2:
            return []

        column_count = len(top_points[0])

        if column_count < 2:
            return []

        landcover_polygon = Polygon(
            landcover_points
        )

        if not landcover_polygon.is_valid:
            landcover_polygon = (
                landcover_polygon.buffer(0)
            )

        if landcover_polygon.is_empty:
            return []

        triangles = []

        for row in range(row_count - 1):
            for column in range(column_count - 1):
                p00 = top_points[row][column]
                p10 = top_points[row][column + 1]
                p01 = top_points[row + 1][column]
                p11 = top_points[row + 1][column + 1]

                terrain_triangles = (
                    (p00, p10, p11),
                    (p00, p11, p01),
                )

                for terrain_triangle in terrain_triangles:
                    triangles.extend(
                        AtlasTerrainFollowingLandcoverBuilder
                        ._clip_terrain_triangle(
                            terrain_triangle=terrain_triangle,
                            landcover_polygon=landcover_polygon,
                            height_mm=height_mm,
                        )
                    )

        return triangles

    @staticmethod
    def _clip_terrain_triangle(
        terrain_triangle,
        landcover_polygon,
        height_mm,
    ):
        triangle_xy = [
            (
                float(point[0]),
                float(point[1]),
            )
            for point in terrain_triangle
        ]

        terrain_polygon = Polygon(
            triangle_xy
        )

        intersection = terrain_polygon.intersection(
            landcover_polygon
        )

        if intersection.is_empty:
            return []

        if intersection.geom_type == "Polygon":
            polygons = [intersection]
        elif intersection.geom_type == "MultiPolygon":
            polygons = list(intersection.geoms)
        else:
            polygons = [
                geometry
                for geometry in getattr(
                    intersection,
                    "geoms",
                    [],
                )
                if geometry.geom_type == "Polygon"
            ]

        result = []

        for polygon in polygons:
            if polygon.is_empty:
                continue

            if polygon.area <= 1e-12:
                continue

            if polygon.interiors:
                continue

            polygon = orient(
                polygon,
                sign=1.0,
            )

            coordinates = list(
                polygon.exterior.coords
            )

            if (
                len(coordinates) >= 2
                and coordinates[0] == coordinates[-1]
            ):
                coordinates = coordinates[:-1]

            points = (
                AtlasTerrainFollowingLandcoverBuilder
                ._clean_polygon_points(
                    coordinates
                )
            )

            if len(points) < 3:
                continue

            flat_triangles = (
                AtlasPolygonTriangulator
                .triangulate(points)
            )

            for flat_triangle in flat_triangles:
                lifted_triangle = []

                for x, y in flat_triangle:
                    z = (
                        AtlasTerrainFollowingLandcoverBuilder
                        ._terrain_triangle_z(
                            terrain_triangle=terrain_triangle,
                            x=x,
                            y=y,
                        )
                    )

                    lifted_triangle.append(
                        (
                            float(x),
                            float(y),
                            float(z + height_mm),
                        )
                    )

                result.append(
                    tuple(lifted_triangle)
                )

        return result

    @staticmethod
    def _terrain_triangle_z(
        terrain_triangle,
        x,
        y,
    ):
        point_a, point_b, point_c = (
            terrain_triangle
        )

        ax, ay, az = point_a
        bx, by, bz = point_b
        cx, cy, cz = point_c

        denominator = (
            (by - cy) * (ax - cx)
            + (cx - bx) * (ay - cy)
        )

        if abs(denominator) <= 1e-15:
            return (
                float(az)
                + float(bz)
                + float(cz)
            ) / 3.0

        weight_a = (
            (by - cy) * (x - cx)
            + (cx - bx) * (y - cy)
        ) / denominator

        weight_b = (
            (cy - ay) * (x - cx)
            + (ax - cx) * (y - cy)
        ) / denominator

        weight_c = (
            1.0
            - weight_a
            - weight_b
        )

        return (
            weight_a * az
            + weight_b * bz
            + weight_c * cz
        )

    @staticmethod
    def _terrain_size(terrain_mesh):
        metadata = terrain_mesh.get(
            "metadata",
            {},
        )

        legacy_size = float(
            metadata.get(
                "size_mm",
                200.0,
            )
        )

        size_x_mm = float(
            metadata.get(
                "size_x_mm",
                legacy_size,
            )
        )

        size_y_mm = float(
            metadata.get(
                "size_y_mm",
                legacy_size,
            )
        )

        if size_x_mm <= 0.0:
            size_x_mm = legacy_size

        if size_y_mm <= 0.0:
            size_y_mm = legacy_size

        return size_x_mm, size_y_mm

    @staticmethod
    def _clip_polygon_to_bounds(
        points,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        cleaned_points = (
            AtlasTerrainFollowingLandcoverBuilder
            ._clean_polygon_points(points)
        )

        if len(cleaned_points) < 3:
            return []

        polygon = Polygon(cleaned_points)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty:
            return []

        clipped = polygon.intersection(
            box(
                min_x,
                min_y,
                max_x,
                max_y,
            )
        )

        if clipped.is_empty:
            return []

        if clipped.geom_type == "Polygon":
            polygons = [clipped]
        elif clipped.geom_type == "MultiPolygon":
            polygons = list(clipped.geoms)
        else:
            polygons = [
                geometry
                for geometry in getattr(
                    clipped,
                    "geoms",
                    [],
                )
                if geometry.geom_type == "Polygon"
            ]

        results = []

        for polygon in polygons:
            if polygon.is_empty:
                continue

            if polygon.area <= 1e-12:
                continue

            if polygon.interiors:
                continue

            polygon = orient(
                polygon,
                sign=1.0,
            )

            coordinates = list(
                polygon.exterior.coords
            )

            if (
                len(coordinates) >= 2
                and coordinates[0] == coordinates[-1]
            ):
                coordinates = coordinates[:-1]

            normalized = (
                AtlasTerrainFollowingLandcoverBuilder
                ._clean_polygon_points(
                    coordinates
                )
            )

            normalized = (
                AtlasTerrainFollowingLandcoverBuilder
                ._rotate_to_lowest_point(
                    normalized
                )
            )

            if len(normalized) < 3:
                continue

            results.append(
                {
                    "points": normalized,
                    "area": polygon.area,
                }
            )

        results.sort(
            key=lambda item: (
                -item["area"],
                item["points"],
            )
        )

        return [
            item["points"]
            for item in results
        ]

    @staticmethod
    def _clean_polygon_points(points):
        cleaned = []

        for point in points or []:
            if len(point) < 2:
                continue

            current = (
                round(float(point[0]), 9),
                round(float(point[1]), 9),
            )

            if cleaned and current == cleaned[-1]:
                continue

            cleaned.append(current)

        if (
            len(cleaned) >= 2
            and cleaned[0] == cleaned[-1]
        ):
            cleaned.pop()

        if len(cleaned) <= 3:
            return cleaned

        changed = True

        while changed and len(cleaned) > 3:
            changed = False
            reduced = []
            point_count = len(cleaned)

            for index in range(point_count):
                previous_point = cleaned[
                    (index - 1) % point_count
                ]
                current_point = cleaned[index]
                next_point = cleaned[
                    (index + 1) % point_count
                ]

                cross_product = (
                    (
                        current_point[0]
                        - previous_point[0]
                    )
                    * (
                        next_point[1]
                        - current_point[1]
                    )
                    - (
                        current_point[1]
                        - previous_point[1]
                    )
                    * (
                        next_point[0]
                        - current_point[0]
                    )
                )

                if abs(cross_product) <= 1e-12:
                    changed = True
                    continue

                reduced.append(current_point)

            if len(reduced) < 3:
                break

            cleaned = reduced

        return cleaned

    @staticmethod
    def _rotate_to_lowest_point(points):
        if not points:
            return []

        start_index = min(
            range(len(points)),
            key=lambda index: (
                points[index][1],
                points[index][0],
            ),
        )

        return (
            points[start_index:]
            + points[:start_index]
        )
