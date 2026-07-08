"""
ATLAS Engine 2.0

Module : Mosque Engine
Version: 0.9

Purpose:
Generate simple printable mosque geometry using reusable architecture primitives.

Scope v0.9:
- main body
- drum
- dome
- finial
- 1 minaret
"""

from atlas_architecture_primitives import (
    make_box,
    make_drum,
    make_dome,
    make_finial,
    make_minaret,
    merge_meshes,
)


def bounds_from_points(model_points):
    xs = [p[0] for p in model_points]
    ys = [p[1] for p in model_points]

    return min(xs), min(ys), max(xs), max(ys)


def generate_mosque_geometry(model_points, base_height_mm, minaret_count=1):
    x1, y1, x2, y2 = bounds_from_points(model_points)

    width = x2 - x1
    depth = y2 - y1

    if width <= 0 or depth <= 0:
        return []

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    meshes = []

    body_height = base_height_mm
    min_side = min(width, depth)

    dome_radius = max(1.2, min(min_side * 0.28, 6.0))
    drum_height = max(0.5, min(dome_radius * 0.35, 2.0))
    dome_height = max(1.0, min(dome_radius * 0.55, 4.0))

    drum_z1 = body_height
    drum_z2 = body_height + drum_height

    dome_z1 = drum_z2
    dome_z2 = dome_z1 + dome_height

    drum = make_drum(
        cx,
        cy,
        dome_radius,
        drum_z1,
        drum_z2,
        segments=24
    )

    dome = make_dome(
        cx,
        cy,
        dome_radius,
        dome_z1,
        dome_z2,
        segments=24,
        rings=6
    )

    finial = make_finial(
        cx,
        cy,
        max(0.18, dome_radius * 0.18),
        dome_z2,
        dome_z2 + max(0.5, dome_radius * 0.35),
        segments=12
    )

    meshes.append(drum)
    meshes.append(dome)
    meshes.append(finial)

    minaret_radius = max(0.35, min(min_side * 0.045, 1.2))
    minaret_height = max(body_height * 1.7, body_height + 10.0)
    minaret_roof_height = max(1.2, min(minaret_height * 0.18, 5.0))

    # İlk sürüm: tek minare ön-sol köşeye yakın
    if minaret_count >= 1:
        mx = x1 + width * 0.12
        my = y1 + depth * 0.12

        minaret = make_minaret(
            mx,
            my,
            minaret_radius,
            0,
            minaret_height,
            minaret_roof_height,
            segments=16
        )

        meshes.append(minaret)

    return meshes