"""
ATLAS Engine 2.0

Module : Architecture Primitives
Version: 1.0

Purpose:
Reusable geometric primitives for Procedural Architecture Engine.
Focus: towers, cylindrical towers, tapered towers.
"""

import math


def merge_meshes(meshes):
    points = []
    faces = []

    for mesh_points, mesh_faces in meshes:
        offset = len(points)
        points.extend(mesh_points)

        for a, b, c in mesh_faces:
            faces.append((a + offset, b + offset, c + offset))

    return points, faces


def make_box(x1, y1, x2, y2, z1, z2):
    points = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2),
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


def make_cylinder(cx, cy, radius, z1, z2, segments=24):
    points = []

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        points.append((
            cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius,
            z1
        ))

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        points.append((
            cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius,
            z2
        ))

    bottom_center = len(points)
    points.append((cx, cy, z1))

    top_center = len(points)
    points.append((cx, cy, z2))

    faces = []

    for i in range(segments):
        j = (i + 1) % segments

        faces.append((i, j, segments + j))
        faces.append((i, segments + j, segments + i))

        faces.append((bottom_center, j, i))
        faces.append((top_center, segments + i, segments + j))

    return points, faces


def make_cone(cx, cy, radius, z1, z2, segments=24):
    points = []

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        points.append((
            cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius,
            z1
        ))

    apex = len(points)
    points.append((cx, cy, z2))

    base_center = len(points)
    points.append((cx, cy, z1))

    faces = []

    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, apex))
        faces.append((base_center, j, i))

    return points, faces


def make_tapered_box_tower(x1, y1, x2, y2, z1, z2, top_scale=0.65):
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    half_w_bottom = (x2 - x1) / 2
    half_d_bottom = (y2 - y1) / 2

    half_w_top = half_w_bottom * top_scale
    half_d_top = half_d_bottom * top_scale

    points = [
        (cx - half_w_bottom, cy - half_d_bottom, z1),
        (cx + half_w_bottom, cy - half_d_bottom, z1),
        (cx + half_w_bottom, cy + half_d_bottom, z1),
        (cx - half_w_bottom, cy + half_d_bottom, z1),

        (cx - half_w_top, cy - half_d_top, z2),
        (cx + half_w_top, cy - half_d_top, z2),
        (cx + half_w_top, cy + half_d_top, z2),
        (cx - half_w_top, cy + half_d_top, z2),
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


def make_stepped_tower(x1, y1, x2, y2, z1, z2, levels=3, shrink=0.82):
    meshes = []

    total_h = z2 - z1
    step_h = total_h / levels

    current_x1 = x1
    current_y1 = y1
    current_x2 = x2
    current_y2 = y2

    for level in range(levels):
        level_z1 = z1 + step_h * level
        level_z2 = z1 + step_h * (level + 1)

        meshes.append(
            make_box(
                current_x1,
                current_y1,
                current_x2,
                current_y2,
                level_z1,
                level_z2
            )
        )

        cx = (current_x1 + current_x2) / 2
        cy = (current_y1 + current_y2) / 2

        width = (current_x2 - current_x1) * shrink
        depth = (current_y2 - current_y1) * shrink

        current_x1 = cx - width / 2
        current_x2 = cx + width / 2
        current_y1 = cy - depth / 2
        current_y2 = cy + depth / 2

    return merge_meshes(meshes)


def make_round_tower_with_cone(cx, cy, radius, z1, z2, roof_height, segments=24):
    tower = make_cylinder(
        cx,
        cy,
        radius,
        z1,
        z2,
        segments=segments
    )

    roof = make_cone(
        cx,
        cy,
        radius * 1.05,
        z2,
        z2 + roof_height,
        segments=segments
    )

    return merge_meshes([tower, roof])


def make_wide_tower(x1, y1, x2, y2, z1, z2, roof_height):
    tower = make_stepped_tower(
        x1,
        y1,
        x2,
        y2,
        z1,
        z2,
        levels=3,
        shrink=0.86
    )

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    roof_w = (x2 - x1) * 0.55
    roof_d = (y2 - y1) * 0.55

    roof = make_pyramid_roof(
        cx - roof_w / 2,
        cy - roof_d / 2,
        cx + roof_w / 2,
        cy + roof_d / 2,
        z2,
        z2 + roof_height
    )

    return merge_meshes([tower, roof])

def make_clock_tower(x1, y1, x2, y2, z1, z2, roof_height):
    tower_body = make_stepped_tower(
        x1,
        y1,
        x2,
        y2,
        z1,
        z2,
        levels=3,
        shrink=0.88
    )

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    clock_size = min(x2 - x1, y2 - y1) * 0.35
    clock_depth = 0.15

    clock_face = make_box(
        cx - clock_size / 2,
        y1 - clock_depth,
        cx + clock_size / 2,
        y1,
        z2 * 0.72,
        z2 * 0.72 + clock_size
    )

    roof = make_pyramid_roof(
        x1,
        y1,
        x2,
        y2,
        z2,
        z2 + roof_height
    )

    return merge_meshes([
        tower_body,
        clock_face,
        roof
    ])    
def make_round_watch_tower(cx, cy, radius, z1, z2, roof_height, segments=20):
    tower_body = make_cylinder(
        cx,
        cy,
        radius,
        z1,
        z2,
        segments=segments
    )

    roof = make_cone(
        cx,
        cy,
        radius * 1.08,
        z2,
        z2 + roof_height,
        segments=segments
    )

    return merge_meshes([
        tower_body,
        roof
    ])    
def make_minaret(cx, cy, radius, z1, z2, roof_height, segments=16):
    shaft = make_cylinder(
        cx,
        cy,
        radius,
        z1,
        z2,
        segments=segments
    )

    balcony_z1 = z1 + (z2 - z1) * 0.62
    balcony_z2 = balcony_z1 + max(0.25, radius * 0.35)

    balcony = make_cylinder(
        cx,
        cy,
        radius * 1.35,
        balcony_z1,
        balcony_z2,
        segments=segments
    )

    spire = make_cone(
        cx,
        cy,
        radius * 0.95,
        z2,
        z2 + roof_height,
        segments=segments
    )

    return merge_meshes([
        shaft,
        balcony,
        spire
    ])    

def make_dome(cx, cy, radius, z1, z2, segments=24, rings=6):
    points = []

    for r in range(rings + 1):
        phi = (math.pi / 2) * r / rings
        ring_radius = radius * math.cos(phi)
        z = z1 + (z2 - z1) * math.sin(phi)

        for i in range(segments):
            angle = 2 * math.pi * i / segments
            points.append((
                cx + math.cos(angle) * ring_radius,
                cy + math.sin(angle) * ring_radius,
                z
            ))

    top_index = len(points)
    points.append((cx, cy, z2))

    faces = []

    for r in range(rings):
        for i in range(segments):
            j = (i + 1) % segments

            a = r * segments + i
            b = r * segments + j
            c = (r + 1) * segments + j
            d = (r + 1) * segments + i

            faces.append((a, b, c))
            faces.append((a, c, d))

    last_ring_start = rings * segments

    for i in range(segments):
        j = (i + 1) % segments
        faces.append((last_ring_start + i, last_ring_start + j, top_index))

    base_center = len(points)
    points.append((cx, cy, z1))

    for i in range(segments):
        j = (i + 1) % segments
        faces.append((base_center, j, i))

    return points, faces   

def make_drum(cx, cy, radius, z1, z2, segments=24):
    return make_cylinder(
        cx,
        cy,
        radius,
        z1,
        z2,
        segments=segments
    )

def make_finial(cx, cy, radius, z1, z2, segments=12):
    base = make_cylinder(
        cx,
        cy,
        radius * 0.35,
        z1,
        z1 + (z2 - z1) * 0.35,
        segments=segments
    )

    tip = make_cone(
        cx,
        cy,
        radius,
        z1 + (z2 - z1) * 0.35,
        z2,
        segments=segments
    )

    return merge_meshes([
        base,
        tip
    ])