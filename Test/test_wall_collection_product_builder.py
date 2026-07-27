import pytest

from CORE.atlas_wall_collection_product_builder import (
    AtlasWallCollectionProductBuilder,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


def _city_result():
    return {
        "terrain_size_x_mm": 100.0,
        "terrain_size_y_mm": 120.0,
        "mesh_groups": {
            "terrain": [
                {
                    "type": "terrain_closed_slab",
                    "triangles": [
                        (
                            (0.0, 0.0, 0.0),
                            (100.0, 0.0, 0.0),
                            (100.0, 120.0, 0.0),
                        ),
                    ],
                },
            ],
            "buildings": [
                {
                    "type": "building",
                    "triangles": [
                        (
                            (10.0, 20.0, 0.8),
                            (20.0, 20.0, 0.8),
                            (20.0, 30.0, 4.0),
                        ),
                    ],
                },
            ],
        },
    }


def _all_vertices(mesh):
    return [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]


def test_wall_collection_centers_city_inside_frame_opening():
    product = AtlasWallCollectionProductBuilder.build(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
    )

    assert product["type"] == "wall_collection_product"
    assert product["outer_width_mm"] == pytest.approx(150.0)
    assert product["outer_height_mm"] == pytest.approx(150.0)
    assert product["opening_width_mm"] == pytest.approx(134.0)
    assert product["opening_height_mm"] == pytest.approx(134.0)

    assert product["city_offset_x_mm"] == pytest.approx(-50.0)
    assert product["city_offset_y_mm"] == pytest.approx(-60.0)

    assert len(product["frame_meshes"]) == 1
    assert len(product["city_meshes"]) == 2
    assert len(product["meshes"]) == 3

    terrain_vertices = _all_vertices(product["city_meshes"][0])

    assert min(x for x, _, _ in terrain_vertices) == pytest.approx(-50.0)
    assert max(x for x, _, _ in terrain_vertices) == pytest.approx(50.0)
    assert min(y for _, y, _ in terrain_vertices) == pytest.approx(-60.0)
    assert max(y for _, y, _ in terrain_vertices) == pytest.approx(60.0)


def test_wall_collection_preserves_city_z_values():
    product = AtlasWallCollectionProductBuilder.build(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
    )

    building_vertices = _all_vertices(product["city_meshes"][1])

    assert min(z for _, _, z in building_vertices) == pytest.approx(0.8)
    assert max(z for _, _, z in building_vertices) == pytest.approx(4.0)


def test_wall_collection_rejects_scene_larger_than_opening():
    city_result = _city_result()
    city_result["terrain_size_x_mm"] = 140.0

    with pytest.raises(ValueError):
        AtlasWallCollectionProductBuilder.build(
            city_result=city_result,
            frame_spec=AtlasWallFrameSpec(),
            frame_depth_mm=6.0,
        )
