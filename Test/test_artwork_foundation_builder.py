from CORE.atlas_artwork_foundation_builder import (
    AtlasArtworkFoundationBuilder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


class FakeCoordinateEngine:
    @staticmethod
    def point_to_stl_mm(lat, lon):
        return float(lat), float(lon)


def _terrain_mesh():
    return {
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (5.0, 0.0, 1.2),
                (10.0, 0.0, 1.4),
            ],
            [
                (0.0, 5.0, 1.2),
                (5.0, 5.0, 1.4),
                (10.0, 5.0, 1.6),
            ],
            [
                (0.0, 10.0, 1.4),
                (5.0, 10.0, 1.6),
                (10.0, 10.0, 1.8),
            ],
        ],
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
    }


def _animal_statue():
    return {
        "id": 5001,
        "lat": 5.0,
        "lon": 5.0,
        "geometry_type": "node",
        "artwork_type": "statue",
        "statue_type": "animal",
        "name": None,
        "tags": {
            "tourism": "artwork",
            "artwork_type": "statue",
            "statue": "animal",
        },
    }


def test_builds_closed_animal_statue_mesh():
    meshes = AtlasArtworkFoundationBuilder.build_artworks(
        artworks=[_animal_statue()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]
    report = AtlasMeshValidator.report(mesh)

    assert report["valid"]
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_animal_statue_uses_printable_dimensions():
    mesh = AtlasArtworkFoundationBuilder.build_artworks(
        artworks=[_animal_statue()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )[0]

    assert mesh["type"] == "artwork_foundation"
    assert mesh["profile"] == "animal_statue"
    assert mesh["source_id"] == 5001
    assert mesh["width_mm"] >= 0.80
    assert mesh["depth_mm"] >= 0.80
    assert mesh["height_mm"] >= 0.80


def test_artwork_is_placed_on_terrain():
    mesh = AtlasArtworkFoundationBuilder.build_artworks(
        artworks=[_animal_statue()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )[0]

    assert mesh["bottom_z"] == 1.4
    assert mesh["top_z"] > mesh["bottom_z"]


def test_animal_statues_align_with_nearest_same_profile_neighbor():
    first = {
        **_animal_statue(),
        "id": 6001,
        "lat": 2.0,
        "lon": 2.0,
    }

    second = {
        **_animal_statue(),
        "id": 6002,
        "lat": 6.0,
        "lon": 6.0,
    }

    meshes = AtlasArtworkFoundationBuilder.build_artworks(
        artworks=[first, second],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )

    assert len(meshes) == 2

    for mesh in meshes:
        assert mesh["profile"] == "animal_statue"
        assert abs(
            abs(mesh["orientation_degrees"]) - 45.0
        ) < 1e-9

        bottom = mesh["bottom"]

        first_edge_length = (
            (
                bottom[1][0] - bottom[0][0]
            ) ** 2
            + (
                bottom[1][1] - bottom[0][1]
            ) ** 2
        ) ** 0.5

        second_edge_length = (
            (
                bottom[2][0] - bottom[1][0]
            ) ** 2
            + (
                bottom[2][1] - bottom[1][1]
            ) ** 2
        ) ** 0.5

        assert abs(
            first_edge_length - mesh["depth_mm"]
        ) < 1e-9

        assert abs(
            second_edge_length - mesh["width_mm"]
        ) < 1e-9
