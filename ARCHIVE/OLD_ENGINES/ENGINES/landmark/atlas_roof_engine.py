"""
ATLAS Engine 2.0

Module : Roof Engine
Version: 1.0

Purpose:
Generate simple printable roof geometry for normal buildings.

Scope v1:
- Flat roof
- Gable roof
- Hip roof
"""


def make_flat_roof(x1, y1, x2, y2, z, thickness=0.4):
    points = [
        (x1, y1, z),
        (x2, y1, z),
        (x2, y2, z),
        (x1, y2, z),

        (x1, y1, z + thickness),
        (x2, y1, z + thickness),
        (x2, y2, z + thickness),
        (x1, y2, z + thickness),
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


def make_gable_roof(x1, y1, x2, y2, z, roof_height):
    width = x2 - x1
    depth = y2 - y1

    if width >= depth:
        cy = (y1 + y2) / 2

        points = [
            (x1, y1, z),
            (x2, y1, z),
            (x2, y2, z),
            (x1, y2, z),
            (x1, cy, z + roof_height),
            (x2, cy, z + roof_height),
        ]

        faces = [
            (0, 1, 5), (0, 5, 4),
            (3, 4, 5), (3, 5, 2),
            (0, 4, 3),
            (1, 2, 5),
            (0, 3, 2), (0, 2, 1),
        ]

    else:
        cx = (x1 + x2) / 2

        points = [
            (x1, y1, z),
            (x2, y1, z),
            (x2, y2, z),
            (x1, y2, z),
            (cx, y1, z + roof_height),
            (cx, y2, z + roof_height),
        ]

        faces = [
            (0, 4, 5), (0, 5, 3),
            (1, 2, 5), (1, 5, 4),
            (0, 1, 4),
            (3, 5, 2),
            (0, 3, 2), (0, 2, 1),
        ]

    return points, faces


def make_hip_roof(x1, y1, x2, y2, z, roof_height):
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    inset_x = (x2 - x1) * 0.12
    inset_y = (y2 - y1) * 0.12

    points = [
        (x1, y1, z),
        (x2, y1, z),
        (x2, y2, z),
        (x1, y2, z),

        (cx - inset_x, cy - inset_y, z + roof_height),
        (cx + inset_x, cy - inset_y, z + roof_height),
        (cx + inset_x, cy + inset_y, z + roof_height),
        (cx - inset_x, cy + inset_y, z + roof_height),
    ]

    faces = [
        (0, 1, 5), (0, 5, 4),
        (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6),
        (3, 0, 4), (3, 4, 7),

        (4, 5, 6), (4, 6, 7),
        (0, 3, 2), (0, 2, 1),
    ]

    return points, faces


def bounds_from_points(model_points):
    xs = [p[0] for p in model_points]
    ys = [p[1] for p in model_points]

    return min(xs), min(ys), max(xs), max(ys)


def choose_roof_type(tags):
    building = tags.get("building")
    historic = tags.get("historic")

    if historic:
        return "hip"

    if building in ["house", "detached", "semidetached_house"]:
        return "gable"

    if building in ["residential", "apartments"]:
        return "hip"

    if building in ["industrial", "commercial", "retail", "warehouse"]:
        return "flat"

    return "flat"


def generate_roof_geometry(tags, model_points, base_height_mm):
    x1, y1, x2, y2 = bounds_from_points(model_points)

    width = x2 - x1
    depth = y2 - y1

    if width <= 0 or depth <= 0:
        return []

    roof_type = choose_roof_type(tags)

    roof_height = max(
        0.7,
        min(min(width, depth) * 0.14, 1.6)
    )

    if roof_type == "gable":
        return [make_gable_roof(x1, y1, x2, y2, base_height_mm, roof_height)]

    if roof_type == "hip":
        return [make_hip_roof(x1, y1, x2, y2, base_height_mm, roof_height)]

    if roof_type == "flat":
        return [make_flat_roof(x1, y1, x2, y2, base_height_mm)]

    return []