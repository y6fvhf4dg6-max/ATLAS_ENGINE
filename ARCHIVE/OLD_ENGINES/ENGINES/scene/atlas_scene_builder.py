"""
ATLAS Engine

Module : Scene Builder
Version: 0.1
Status : Development

Purpose:
Combines multiple 3D mesh parts into one scene mesh.
"""


def add_mesh_to_scene(scene_points, scene_faces, mesh_points, mesh_faces):
    offset = len(scene_points)

    scene_points.extend(mesh_points)

    for face in mesh_faces:
        scene_faces.append((
            face[0] + offset,
            face[1] + offset,
            face[2] + offset,
        ))

    return scene_points, scene_faces


def create_empty_scene():
    return [], []


def scene_info(scene_points, scene_faces):
    print("ATLAS Scene Builder v0.1")
    print("Sahne 3D nokta sayısı:", len(scene_points))
    print("Sahne yüzey sayısı:", len(scene_faces))


if __name__ == "__main__":
    scene_points, scene_faces = create_empty_scene()

    box_1_points = [
        (0, 0, 0),
        (20, 0, 0),
        (20, 20, 0),
        (0, 20, 0),
    ]

    box_1_faces = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    box_2_points = [
        (40, 40, 0),
        (60, 40, 0),
        (60, 60, 0),
        (40, 60, 0),
    ]

    box_2_faces = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    add_mesh_to_scene(
        scene_points,
        scene_faces,
        box_1_points,
        box_1_faces
    )

    add_mesh_to_scene(
        scene_points,
        scene_faces,
        box_2_points,
        box_2_faces
    )

    scene_info(scene_points, scene_faces)