"""
ATLAS Engine 2.0

Module : Landmark Geometry
Version: 1.0

Purpose:
Add simple procedural geometry details to landmark buildings.
First target: churches and cathedrals.
"""

from atlas_architecture_primitives import (

    make_box,
    make_pyramid_roof,
    make_stepped_tower,
    make_wide_tower,
)    

from atlas_mosque_engine import generate_mosque_geometry

def make_box(x1, y1, x2, y2, z1, z2):
    points = [
        (x1, y1, z1),
        (x2, y1, z1),
        (x2, y2, z1),
        (x1, y2, z1),

        (x1, y1, z2),
        (x2, y1, z2),
        (x2, y2, z2),
        (x1, y2, z2),
    ]

    faces = [
        (0, 1, 2), (0, 2, 3),
        (4, 6, 5), (4, 7, 6),

        (0, 4, 5), (0, 5, 1),
        (1, 5, 6), (1, 6, 2),
        (2, 6, 7), (2, 7, 3),
        (3, 7, 4), (3, 4, 0),
    ]

    return points, faces

def make_pyramid_roof(x1, y1, x2, y2, z1, z2):
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    points = [
        (x1, y1, z1),
        (x2, y1, z1),
        (x2, y2, z1),
        (x1, y2, z1),
        (cx, cy, z2),
    ]

    faces = [
        (0, 1, 4),
        (1, 2, 4),
        (2, 3, 4),
        (3, 0, 4),
        (0, 2, 1),
        (0, 3, 2),
    ]

    return points, faces


def bounds_from_points(model_points):
    xs = [p[0] for p in model_points]
    ys = [p[1] for p in model_points]

    return min(xs), min(ys), max(xs), max(ys)


def add_christian_religious_details(
    model_points, 
    base_height_mm, 
    tower_count=1
):
    x1, y1, x2, y2 = bounds_from_points(model_points)

    width = x2 - x1
    depth = y2 - y1

    if width <= 0 or depth <= 0:
        return []

    meshes = []

    tower_height_mm = min(
        max(base_height_mm * 3.0, base_height_mm + 22.0),
        60.0
    )

    roof_extra = max(4.0, min(tower_height_mm * 0.22, 10.0))
    

    if width >= depth:
        tower_w = width * 0.12
        tower_d = depth * 0.17
        overlap = min(tower_w, tower_d) * 0.35

        left_tower = make_wide_tower(
            x1,
            y1,
            x1 + tower_w + overlap,
            y1 + tower_d + overlap,
            0,
            tower_height_mm,
            roof_extra
        )

        right_tower = make_wide_tower(
            x2 - tower_w - overlap,
            y1,
            x2,
            y1 + tower_d + overlap,
            0,
            tower_height_mm,
            roof_extra
        )

        nave_w = width * 0.22
        nave_x1 = x1 + (width - nave_w) / 2
        nave_x2 = nave_x1 + nave_w

        ridge = make_box(
            nave_x1,
            y1 + depth * 0.15,
            nave_x2,
            y2 - depth * 0.12,
            base_height_mm,
            base_height_mm + 2.0
        )

    else:
        tower_w = width * 0.22
        tower_d = depth * 0.16

        left_tower = make_box(
            x1,
            y1,
            x1 + tower_w,
            y1 + tower_d,
            base_height_mm,
            tower_top
        )

        right_tower = make_box(
            x1,
            y2 - tower_d,
            x1 + tower_w,
            y2,
            base_height_mm,
            tower_top
        )

        nave_d = depth * 0.22
        nave_y1 = y1 + (depth - nave_d) / 2
        nave_y2 = nave_y1 + nave_d

        ridge = make_box(
            x1 + width * 0.15,
            nave_y1,
            x2 - width * 0.12,
            nave_y2,
            base_height_mm,
            base_height_mm + 2.0
        )

        left_x1 = left_tower[0][0][0]
        left_y1 = left_tower[0][0][1]
        left_x2 = left_tower[0][2][0]
        left_y2 = left_tower[0][2][1]

        right_x1 = right_tower[0][0][0]
        right_y1 = right_tower[0][0][1]
        right_x2 = right_tower[0][2][0]
        right_y2 = right_tower[0][2][1]

        roof_extra = max(3.0, min(base_height_mm * 0.25, 10.0))

        left_roof = make_pyramid_roof(
            left_x1, left_y1, left_x2, left_y2,
            tower_top,
            tower_top + roof_extra
        )

        right_roof = make_pyramid_roof(
            right_x1, right_y1, right_x2, right_y2,
            tower_top,
            tower_top + roof_extra
        )

    meshes.append(left_tower)

    if tower_count >= 2:
        meshes.append(right_tower)

    meshes.append(ridge)

    return meshes

def generate_landmark_geometry(tags, model_points, base_height_mm):
    building = tags.get("building")
    amenity = tags.get("amenity")
    religion = tags.get("religion")

    if building == "mosque" or (
        amenity == "place_of_worship"
        and religion == "muslim"
    ):
        return generate_mosque_geometry(
            model_points,
            base_height_mm,
            minaret_count=1
        )

    if building in ["cathedral", "church"] or (
        amenity == "place_of_worship"
        and religion == "christian"
    ):

        tower_count = 1

        if building == "cathedral":
            tower_count = 2

        return add_christian_religious_details(
            model_points,
            base_height_mm,
            tower_count
        )

    return []