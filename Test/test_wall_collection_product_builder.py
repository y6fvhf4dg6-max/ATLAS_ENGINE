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


def test_wall_collection_accepts_submicron_float_overflow_at_opening_limit():
    city_result = _city_result()
    city_result["terrain_size_x_mm"] = 134.0000000001
    city_result["terrain_size_y_mm"] = 134.0000000001

    product = AtlasWallCollectionProductBuilder.build(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
    )

    assert product["opening_width_mm"] == pytest.approx(134.0)
    assert product["opening_height_mm"] == pytest.approx(134.0)


def test_wall_collection_adds_optional_integrated_label_plate_without_moving_city():
    from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec

    product = AtlasWallCollectionProductBuilder.build(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        label_plate_spec=AtlasLabelPlateSpec(
            width_mm=118.0,
            height_mm=14.0,
            depth_mm=1.2,
        ),
    )

    assert product["city_offset_x_mm"] == pytest.approx(-50.0)
    assert product["city_offset_y_mm"] == pytest.approx(-60.0)

    assert len(product["label_plate_meshes"]) == 1
    assert len(product["meshes"]) == 4

    label_mesh = product["label_plate_meshes"][0]
    vertices = _all_vertices(label_mesh)

    assert label_mesh["type"] == "label_plate"
    assert min(x for x, _, _ in vertices) == pytest.approx(-59.0)
    assert max(x for x, _, _ in vertices) == pytest.approx(59.0)
    assert min(y for _, y, _ in vertices) == pytest.approx(-67.0)
    assert max(y for _, y, _ in vertices) == pytest.approx(-53.0)
    assert min(z for _, _, z in vertices) == pytest.approx(6.0)
    assert max(z for _, _, z in vertices) == pytest.approx(7.2)


def test_wall_collection_adds_two_line_label_text_on_front_of_plate():
    from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
    from CORE.atlas_label_text_spec import AtlasLabelTextSpec

    product = AtlasWallCollectionProductBuilder.build(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        label_plate_spec=AtlasLabelPlateSpec(
            width_mm=118.0,
            height_mm=14.0,
            depth_mm=1.2,
        ),
        label_text_spec=AtlasLabelTextSpec(
            primary_text="KÖLN",
            secondary_text="50.9375° N · 6.9603° E",
            primary_height_mm=4.2,
            secondary_height_mm=2.8,
            depth_mm=0.6,
            max_width_mm=108.0,
        ),
    )

    assert product["city_offset_x_mm"] == pytest.approx(-50.0)
    assert product["city_offset_y_mm"] == pytest.approx(-60.0)

    assert len(product["label_plate_meshes"]) == 1
    assert len(product["label_text_meshes"]) == 2
    assert len(product["meshes"]) == 6

    primary_mesh, secondary_mesh = product["label_text_meshes"]

    assert primary_mesh["type"] == "label_text"
    assert secondary_mesh["type"] == "label_text"
    assert primary_mesh["text"] == "KÖLN"
    assert secondary_mesh["text"] == "50.9375° N · 6.9603° E"

    primary_vertices = _all_vertices(primary_mesh)
    secondary_vertices = _all_vertices(secondary_mesh)

    assert min(z for _, _, z in primary_vertices) == pytest.approx(7.2)
    assert max(z for _, _, z in primary_vertices) == pytest.approx(7.8)
    assert min(z for _, _, z in secondary_vertices) == pytest.approx(7.2)
    assert max(z for _, _, z in secondary_vertices) == pytest.approx(7.8)

    assert min(y for _, y, _ in primary_vertices) > max(
        y for _, y, _ in secondary_vertices
    )

    for vertices in (primary_vertices, secondary_vertices):
        assert min(x for x, _, _ in vertices) >= -54.0 - 1e-6
        assert max(x for x, _, _ in vertices) <= 54.0 + 1e-6
        assert min(y for _, y, _ in vertices) >= -67.0 - 1e-6
        assert max(y for _, y, _ in vertices) <= -53.0 + 1e-6
