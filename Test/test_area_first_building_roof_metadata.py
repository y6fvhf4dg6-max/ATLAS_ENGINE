from CORE.atlas_mesh_builder import AtlasMeshBuilder
from CORE.atlas_scene_builder import AtlasSceneBuilder


RAW_BUILDING = {
    "id": 501,
    "geometry": [
        (39.0000, 32.0000),
        (39.0000, 32.0040),
        (39.0010, 32.0040),
        (39.0010, 32.0000),
    ],
    "tags": {
        "building": "yes",
    },
}


def test_area_first_scene_attaches_roof_metadata(monkeypatch):
    original_triangles = [
        (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        ),
    ]

    mesh = {
        "bottom": [],
        "top": [],
        "walls": [],
        "triangles": list(original_triangles),
    }

    monkeypatch.setattr(
        AtlasMeshBuilder,
        "build_mesh",
        staticmethod(
            lambda building, coordinate_engine: mesh
        ),
    )

    scene = AtlasSceneBuilder.build_scene(
        raw_buildings=[RAW_BUILDING],
        coordinate_engine=object(),
        roads=None,
        debug=False,
    )

    building_meshes = scene.layers["buildings"]

    assert len(building_meshes) == 1

    result_mesh = building_meshes[0]

    assert result_mesh["building_roof_profile"] == "gable"
    assert (
        result_mesh["building_roof_decision_source"]
        == "inferred"
    )
    assert result_mesh["building_oriented_aspect_ratio"] > 3.0
    assert result_mesh["building_rectangularity"] == 1.0

    assert result_mesh["triangles"] == original_triangles

    report = scene.metadata["building_report"]

    assert report["accepted"] == 1
    assert report["skipped"] == 0
    assert report["building_roof_profiles"] == {
        "gable": 1,
    }
    assert report["building_roof_decision_sources"] == {
        "inferred": 1,
    }


def test_area_first_scene_preserves_explicit_flat_roof(
    monkeypatch,
):
    raw_building = {
        **RAW_BUILDING,
        "id": 502,
        "tags": {
            "building": "yes",
            "roof:shape": "flat",
        },
    }

    mesh = {
        "bottom": [],
        "top": [],
        "walls": [],
        "triangles": [],
    }

    monkeypatch.setattr(
        AtlasMeshBuilder,
        "build_mesh",
        staticmethod(
            lambda building, coordinate_engine: mesh
        ),
    )

    scene = AtlasSceneBuilder.build_scene(
        raw_buildings=[raw_building],
        coordinate_engine=object(),
        roads=None,
        debug=False,
    )

    result_mesh = scene.layers["buildings"][0]

    assert result_mesh["building_roof_profile"] == "flat"
    assert result_mesh["building_roof_decision_source"] == "osm"
