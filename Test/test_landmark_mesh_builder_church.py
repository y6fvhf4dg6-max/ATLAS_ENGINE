from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_mesh_builder import AtlasLandmarkMeshBuilder
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_landmark_mesh_builder_builds_church_landmark():
    landmark = AtlasLandmark(
        id=701,
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 40.0),
            (0.0, 40.0),
        ),
        tags={
            "building": "church",
            "height": "24",
        },
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=None,
    )

    assert mesh["type"] == "church_landmark"
    assert mesh["landmark_id"] == 701
    assert mesh["landmark_class"] == "church"
    assert len(mesh["triangles"]) > 0


def test_landmark_mesh_builder_builds_cathedral_landmark():
    landmark = AtlasLandmark(
        id=702,
        landmark_type=AtlasLandmarkType.CATHEDRAL,
        geometry=(
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 60.0),
            (0.0, 60.0),
        ),
        tags={
            "building": "cathedral",
        },
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=None,
    )

    assert mesh["landmark_class"] == "cathedral"
    assert len(mesh["tower_meshes"]) == 2
    assert len(mesh["spire_meshes"]) == 2
