from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_mesh_builder import AtlasLandmarkMeshBuilder
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_landmark_mesh_builder_builds_bridge_mesh():
    landmark = AtlasLandmark(
        id="bridge-test-1",
        source="test",
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 6.0),
            (0.0, 6.0),
        ),
        tags={
            "bridge": "yes",
            "height": "8",
        },
    )

    mesh = AtlasLandmarkMeshBuilder.build(landmark)

    assert mesh["type"] == "bridge"
    assert len(mesh["triangles"]) == 12
