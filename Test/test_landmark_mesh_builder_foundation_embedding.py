from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_mesh_builder import AtlasLandmarkMeshBuilder
from CORE.atlas_landmark_type import AtlasLandmarkType


class FakeTerrain:

    def sample_height(self, x, y):
        return x * 0.20 + y * 0.10


def test_landmark_base_follows_sloped_terrain():
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

    base_vertices = [
        point
        for triangle in mesh["triangles"]
        for point in triangle
        if point[2] < 1.0
    ]

    z_values = {
        round(point[2], 4)
        for point in base_vertices
    }

    assert len(z_values) > 1
