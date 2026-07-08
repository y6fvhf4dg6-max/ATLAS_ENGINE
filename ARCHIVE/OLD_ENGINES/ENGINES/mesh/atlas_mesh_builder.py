"""
ATLAS Engine

Module : Mesh Builder
Version: 0.1
Status : Development

Purpose:
Creates a triangle mesh from 2D model-space polygon points.

Input:
- [(x, y), (x, y), ...]

Output:
- Shapely Polygon
- Triangle index list
"""

import numpy as np
import mapbox_earcut as earcut
from shapely.geometry import Polygon


def create_polygon(model_points):
    polygon = Polygon(model_points)

    if not polygon.is_valid:
        raise ValueError("Geçersiz polygon.")

    if polygon.area <= 0:
        raise ValueError("Polygon alanı sıfır veya negatif.")

    return polygon


def triangulate_polygon(model_points):
    polygon = create_polygon(model_points)

    # Shapely kapalı polygon döndürür; son nokta ilk noktayla aynı olabilir.
    # Earcut için tekrar eden son noktayı çıkarıyoruz.
    points = list(polygon.exterior.coords)

    if points[0] == points[-1]:
        points = points[:-1]

    vertices = np.array(points, dtype=np.float32)
    ring_end_indices = np.array([len(vertices)], dtype=np.uint32)

    triangles = earcut.triangulate_float32(
        vertices,
        ring_end_indices
    )

    return polygon, vertices, triangles


def mesh_info(model_points):
    polygon, vertices, triangles = triangulate_polygon(model_points)

    print("ATLAS Mesh Builder v0.1")
    print("Polygon geçerli:", polygon.is_valid)
    print("Polygon alanı:", round(polygon.area, 2), "mm²")
    print("Vertex sayısı:", len(vertices))
    print("Triangle index sayısı:", len(triangles))
    print("Triangle sayısı:", len(triangles) // 3)

    return polygon, vertices, triangles


if __name__ == "__main__":
    sample_model_points = [
        (20, 20),
        (180, 20),
        (180, 180),
        (20, 180),
        (20, 20),
    ]

    mesh_info(sample_model_points)