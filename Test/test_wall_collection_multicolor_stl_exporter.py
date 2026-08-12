from pathlib import Path

from CORE.atlas_wall_collection_multicolor_stl_exporter import (
    AtlasWallCollectionMulticolorSTLExporter,
)


def _mesh(x):
    return {
        "type": "test_mesh",
        "triangles": [
            (
                (x, 0.0, 0.0),
                (x + 1.0, 0.0, 0.0),
                (x, 1.0, 0.0),
            ),
        ],
    }


def test_multicolor_exporter_merges_material_batches_into_five_color_stls(
    monkeypatch,
    tmp_path,
):
    black = (20, 20, 20)
    desert_tan = (205, 190, 160)
    brick_red = (156, 48, 42)
    dark_green = (73, 105, 58)
    blue = (70, 140, 180)

    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "KOELN_PREMIUM_V1",
        "material_batches": {
            "frame": {
                "rgb": black,
                "meshes": [_mesh(0.0)],
            },
            "terrain": {
                "rgb": desert_tan,
                "meshes": [_mesh(10.0)],
            },
            "building_walls": {
                "rgb": desert_tan,
                "meshes": [_mesh(20.0)],
            },
            "landmarks": {
                "rgb": desert_tan,
                "meshes": [_mesh(25.0)],
            },
            "building_roofs": {
                "rgb": brick_red,
                "meshes": [_mesh(30.0)],
            },
            "parks": {
                "rgb": dark_green,
                "meshes": [_mesh(40.0)],
            },
            "trees": {
                "rgb": dark_green,
                "meshes": [_mesh(50.0)],
            },
            "water": {
                "rgb": blue,
                "meshes": [_mesh(60.0)],
            },
            "label_plate": {
                "rgb": desert_tan,
                "meshes": [_mesh(70.0)],
            },
            "label_text": {
                "rgb": black,
                "meshes": [_mesh(80.0)],
            },
            "roads": {
                "rgb": black,
                "meshes": [_mesh(90.0)],
            },
        },
    }

    writes = []

    def fake_write(meshes, output_path, solid_name="ATLAS_MODEL"):
        writes.append(
            {
                "meshes": meshes,
                "output_path": Path(output_path),
                "solid_name": solid_name,
            }
        )
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    result = AtlasWallCollectionMulticolorSTLExporter.export_scene(
        scene=scene,
        output_directory=tmp_path,
        product_name="koeln_premium",
    )

    assert result["type"] == "wall_collection_multicolor_stl_package"
    assert result["profile_name"] == "KOELN_PREMIUM_V1"
    assert result["color_count"] == 5
    assert result["part_count"] == 5

    assert set(result["parts"]) == {
        "black",
        "desert_tan",
        "brick_red",
        "dark_green",
        "blue",
    }

    assert len(writes) == 5

    assert result["parts"]["black"]["rgb"] == black
    assert result["parts"]["desert_tan"]["rgb"] == desert_tan
    assert result["parts"]["brick_red"]["rgb"] == brick_red
    assert result["parts"]["dark_green"]["rgb"] == dark_green
    assert result["parts"]["blue"]["rgb"] == blue

    assert set(
        result["parts"]["desert_tan"]["source_batches"]
    ) == {
        "terrain",
        "building_walls",
        "landmarks",
        "label_plate",
    }

    assert set(result["parts"]["black"]["source_batches"]) == {
        "frame",
        "label_text",
        "roads",
    }

    assert result["parts"]["brick_red"]["source_batches"] == (
        "building_roofs",
    )

    assert set(result["parts"]["dark_green"]["source_batches"]) == {
        "parks",
        "trees",
    }

    assert result["parts"]["blue"]["source_batches"] == (
        "water",
    )

    assert result["parts"]["black"]["output_path"] == (
        tmp_path / "koeln_premium__black.stl"
    )
    assert result["parts"]["desert_tan"]["output_path"] == (
        tmp_path / "koeln_premium__desert_tan.stl"
    )
    assert result["parts"]["brick_red"]["output_path"] == (
        tmp_path / "koeln_premium__brick_red.stl"
    )
    assert result["parts"]["dark_green"]["output_path"] == (
        tmp_path / "koeln_premium__dark_green.stl"
    )
    assert result["parts"]["blue"]["output_path"] == (
        tmp_path / "koeln_premium__blue.stl"
    )

def test_multicolor_exporter_deduplicates_identical_triangles_across_same_color_batches(
    monkeypatch,
    tmp_path,
):
    white = (245, 245, 240)
    shared_mesh = _mesh(0.0)

    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "TEST_PROFILE",
        "material_batches": {
            "terrain": {
                "rgb": white,
                "meshes": [shared_mesh],
            },
            "building_walls": {
                "rgb": white,
                "meshes": [shared_mesh],
            },
        },
    }

    writes = []

    def fake_write(meshes, output_path, solid_name="ATLAS_MODEL"):
        writes.append(meshes)
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    AtlasWallCollectionMulticolorSTLExporter.export_scene(
        scene=scene,
        output_directory=tmp_path,
        product_name="dedup_test",
    )

    assert len(writes) == 1
    assert len(writes[0]) == 1
    assert len(writes[0][0]["triangles"]) == 1


def test_multicolor_exporter_includes_forest_canopy_in_dark_green_part(
    monkeypatch,
    tmp_path,
):
    dark_green = (73, 105, 58)

    canopy_mesh = {
        "type": "forest_canopy_foundation",
        "triangles": [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
            ),
        ],
    }

    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "TEST_PROFILE",
        "material_batches": {
            "trees": {
                "rgb": dark_green,
                "meshes": [canopy_mesh],
            },
        },
    }

    writes = []

    def fake_write(meshes, output_path, solid_name="ATLAS_MODEL"):
        writes.append(
            {
                "meshes": meshes,
                "output_path": Path(output_path),
                "solid_name": solid_name,
            }
        )
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    result = AtlasWallCollectionMulticolorSTLExporter.export_scene(
        scene=scene,
        output_directory=tmp_path,
        product_name="forest_canopy_test",
    )

    assert result["color_count"] == 1
    assert set(result["parts"]) == {"dark_green"}
    assert result["parts"]["dark_green"]["rgb"] == dark_green
    assert result["parts"]["dark_green"]["source_batches"] == (
        "trees",
    )

    assert len(writes) == 1
    assert len(writes[0]["meshes"]) == 1

    exported_mesh = writes[0]["meshes"][0]

    assert exported_mesh["type"] == "multicolor_merged_color_mesh"
    assert exported_mesh["triangles"] == canopy_mesh["triangles"]


def test_multicolor_exporter_reports_semantic_roles_per_physical_part(
    monkeypatch,
    tmp_path,
):
    black = (20, 20, 20)
    desert_tan = (205, 190, 160)
    brick_red = (156, 48, 42)
    dark_green = (73, 105, 58)
    blue = (70, 140, 180)

    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "KOELN_PREMIUM_V1",
        "material_batches": {
            "frame": {
                "rgb": black,
                "meshes": [_mesh(0.0)],
            },
            "terrain": {
                "rgb": desert_tan,
                "meshes": [_mesh(10.0)],
            },
            "building_walls": {
                "rgb": desert_tan,
                "meshes": [_mesh(20.0)],
            },
            "building_roofs": {
                "rgb": brick_red,
                "meshes": [_mesh(30.0)],
            },
            "parks": {
                "rgb": dark_green,
                "meshes": [_mesh(40.0)],
            },
            "trees": {
                "rgb": dark_green,
                "meshes": [_mesh(50.0)],
            },
            "water": {
                "rgb": blue,
                "meshes": [_mesh(60.0)],
            },
            "label_plate": {
                "rgb": desert_tan,
                "meshes": [_mesh(70.0)],
            },
            "label_text": {
                "rgb": black,
                "meshes": [_mesh(80.0)],
            },
            "roads": {
                "rgb": black,
                "meshes": [_mesh(90.0)],
            },
        },
    }

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        lambda **kwargs: kwargs["output_path"],
    )

    result = AtlasWallCollectionMulticolorSTLExporter.export_scene(
        scene=scene,
        output_directory=tmp_path,
        product_name="semantic_roles",
    )

    assert set(
        result["parts"]["desert_tan"]["semantic_roles"]
    ) == {
        "terrain",
        "generic_building",
        "label_plate",
    }

    assert set(
        result["parts"]["brick_red"]["semantic_roles"]
    ) == {
        "generic_building_roof",
    }

    assert set(
        result["parts"]["dark_green"]["semantic_roles"]
    ) == {
        "vegetation",
    }

    assert set(
        result["parts"]["black"]["semantic_roles"]
    ) == {
        "frame",
        "label_text",
        "roads_hardscape",
    }

    assert set(
        result["parts"]["blue"]["semantic_roles"]
    ) == {
        "water",
    }


def test_multicolor_exporter_groups_by_explicit_physical_material_when_available(
    monkeypatch,
    tmp_path,
):
    shared_rgb = (240, 235, 220)

    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "CUSTOM_PRODUCT_PROFILE",
        "material_batches": {
            "frame": {
                "rgb": shared_rgb,
                "physical_material": "material_shared",
                "semantic_role": "frame",
                "meshes": [_mesh(0.0)],
            },
            "terrain": {
                "rgb": shared_rgb,
                "physical_material": "material_shared",
                "semantic_role": "terrain",
                "meshes": [_mesh(10.0)],
            },
        },
    }

    writes = []

    def fake_write(
        meshes,
        output_path,
        solid_name="ATLAS_MODEL",
    ):
        writes.append(
            {
                "meshes": meshes,
                "output_path": Path(output_path),
                "solid_name": solid_name,
            }
        )
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    result = (
        AtlasWallCollectionMulticolorSTLExporter
        .export_scene(
            scene=scene,
            output_directory=tmp_path,
            product_name="custom_material_grouping",
        )
    )

    assert result["part_count"] == 1
    assert result["color_count"] == 1
    assert len(writes) == 1

    part = next(
        iter(result["parts"].values())
    )

    assert (
        part["physical_material"]
        == "material_shared"
    )

    assert set(
        part["source_batches"]
    ) == {
        "frame",
        "terrain",
    }

    assert set(
        part["semantic_roles"]
    ) == {
        "frame",
        "terrain",
    }

    assert part["rgb"] == shared_rgb


def test_multicolor_exporter_enforces_production_physical_color_limit(
    monkeypatch,
    tmp_path,
):
    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "PRODUCTION_LIMIT_TEST",
        "material_batches": {
            "terrain": {
                "rgb": (240, 240, 240),
                "physical_material": "material_1",
                "semantic_role": "terrain",
                "meshes": [_mesh(0.0)],
            },
            "water": {
                "rgb": (70, 140, 180),
                "physical_material": "material_2",
                "semantic_role": "water",
                "meshes": [_mesh(10.0)],
            },
        },
    }

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        lambda **kwargs: kwargs["output_path"],
    )

    try:
        (
            AtlasWallCollectionMulticolorSTLExporter
            .export_scene(
                scene=scene,
                output_directory=tmp_path,
                product_name="production_limit",
                maximum_physical_color_count=1,
            )
        )
    except ValueError as exc:
        assert (
            "maximum_physical_color_count"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected production physical color limit "
            "to be enforced"
        )


def test_multicolor_exporter_accepts_package_within_production_color_limit(
    monkeypatch,
    tmp_path,
):
    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "PRODUCTION_LIMIT_TEST",
        "material_batches": {
            "terrain": {
                "rgb": (240, 240, 240),
                "physical_material": "material_1",
                "semantic_role": "terrain",
                "meshes": [_mesh(0.0)],
            },
            "water": {
                "rgb": (70, 140, 180),
                "physical_material": "material_2",
                "semantic_role": "water",
                "meshes": [_mesh(10.0)],
            },
        },
    }

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        lambda **kwargs: kwargs["output_path"],
    )

    result = (
        AtlasWallCollectionMulticolorSTLExporter
        .export_scene(
            scene=scene,
            output_directory=tmp_path,
            product_name="production_limit_ok",
            maximum_physical_color_count=2,
        )
    )

    assert result["physical_color_count"] == 2
    assert result[
        "maximum_physical_color_count"
    ] == 2
