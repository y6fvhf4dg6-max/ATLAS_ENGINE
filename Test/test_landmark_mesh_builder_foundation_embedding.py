from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_mesh_builder import AtlasLandmarkMeshBuilder
from CORE.atlas_landmark_type import AtlasLandmarkType


class FakeTerrain:
    def sample_height(self, x, y):
        return x * 0.20 + y * 0.10


def test_landmark_is_translated_by_one_rigid_foundation_height():
    landmark = AtlasLandmark(
        id=1,
        landmark_type=AtlasLandmarkType.LIGHTHOUSE,
        geometry=(
            (0.0, 0.0),
            (8.0, 0.0),
            (8.0, 8.0),
            (0.0, 8.0),
        ),
        tags={"height": "35"},
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=FakeTerrain(),
    )

    bottom_z_values = {
        round(point[2], 8)
        for point in mesh["bottom"]
    }

    top_z_values = {
        round(point[2], 8)
        for point in mesh["top"]
    }

    assert len(bottom_z_values) == 1
    assert len(top_z_values) == 1

    bottom_z = next(iter(bottom_z_values))
    top_z = next(iter(top_z_values))

    assert top_z - bottom_z == 35.0
