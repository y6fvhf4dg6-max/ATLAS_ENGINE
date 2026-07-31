import pytest
from types import SimpleNamespace

from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
)
from CORE.atlas_foundation_first_pipeline import (
    AtlasFoundationFirstPipeline,
)
from CORE.atlas_scene_builder import AtlasSceneBuilder
from CORE.atlas_castle_footprint_regularizer import (
    AtlasCastleFootprintRegularizer,
)
from CORE.atlas_castle_building_profiler import (
    AtlasCastleBuildingProfiler,
)


def make_building(
    *,
    geometry,
    roof_type=None,
    is_castle_building=False,
):
    return SimpleNamespace(
        building_id="roof-test-building",
        building_type="yes",
        area_m2=100.0,
        perimeter_m=50.0,
        estimated_height=10.0,
        levels=3,
        roof_type=roof_type,
        quality_score=100,
        tags={
            "building": "yes",
            **(
                {"roof:shape": roof_type}
                if roof_type is not None
                else {}
            ),
        },
        geometry=geometry,
        bbox=None,
        is_castle_building=is_castle_building,
    )


def test_long_rectangular_main_building_gets_gable_metadata():
    building = make_building(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )

    result = (
        AtlasFoundationSceneBuilder
        ._building_roof_metadata(
            atlas_building=building,
            is_building_part=False,
        )
    )

    assert result["building_roof_profile"] == "gable"
    assert (
        result["building_roof_decision_source"]
        == "inferred"
    )
    assert result["building_oriented_aspect_ratio"] > 3.0
    assert result["building_rectangularity"] == 1.0


def test_near_square_main_building_gets_hipped_metadata():
    building = make_building(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0010),
            (39.0010, 32.0010),
            (39.0010, 32.0000),
        ],
    )

    result = (
        AtlasFoundationSceneBuilder
        ._building_roof_metadata(
            atlas_building=building,
            is_building_part=False,
        )
    )

    assert result["building_roof_profile"] == "hipped"
    assert (
        result["building_roof_decision_source"]
        == "inferred"
    )


def test_explicit_osm_roof_shape_is_preserved():
    building = make_building(
        roof_type="flat",
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )

    result = (
        AtlasFoundationSceneBuilder
        ._building_roof_metadata(
            atlas_building=building,
            is_building_part=False,
        )
    )

    assert result["building_roof_profile"] == "flat"
    assert result["building_roof_decision_source"] == "osm"


def test_building_part_does_not_receive_inferred_roof():
    building = make_building(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )

    result = (
        AtlasFoundationSceneBuilder
        ._building_roof_metadata(
            atlas_building=building,
            is_building_part=True,
        )
    )

    assert result["building_roof_profile"] == "flat"
    assert (
        result["building_roof_decision_source"]
        == "building_part"
    )


def test_castle_building_returns_no_normal_roof_metadata():
    building = make_building(
        is_castle_building=True,
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )

    result = (
        AtlasFoundationSceneBuilder
        ._building_roof_metadata(
            atlas_building=building,
            is_building_part=False,
        )
    )

    assert result is None


def test_roof_metadata_is_attached_to_normal_building_mesh():
    building = make_building(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )
    mesh = {
        "source_id": "roof-test-building",
        "triangles": [],
    }
    profile_counts = {}
    decision_source_counts = {}

    result = (
        AtlasFoundationSceneBuilder
        ._attach_building_roof_metadata(
            mesh=mesh,
            atlas_building=building,
            is_building_part=False,
            profile_counts=profile_counts,
            decision_source_counts=decision_source_counts,
        )
    )

    assert result is mesh
    assert mesh["building_roof_profile"] == "gable"
    assert (
        mesh["building_roof_decision_source"]
        == "inferred"
    )
    assert mesh["building_oriented_aspect_ratio"] > 3.0
    assert mesh["building_rectangularity"] == 1.0

    assert profile_counts == {"gable": 1}
    assert decision_source_counts == {"inferred": 1}


def test_castle_mesh_does_not_receive_normal_roof_metadata():
    building = make_building(
        is_castle_building=True,
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )
    mesh = {
        "source_id": "castle-test-building",
        "triangles": [],
    }
    profile_counts = {}
    decision_source_counts = {}

    result = (
        AtlasFoundationSceneBuilder
        ._attach_building_roof_metadata(
            mesh=mesh,
            atlas_building=building,
            is_building_part=False,
            profile_counts=profile_counts,
            decision_source_counts=decision_source_counts,
        )
    )

    assert result is mesh
    assert "building_roof_profile" not in mesh
    assert "building_roof_decision_source" not in mesh
    assert profile_counts == {}
    assert decision_source_counts == {}


def test_roof_metadata_counts_accumulate():
    profile_counts = {}
    decision_source_counts = {}

    gable_building = make_building(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )
    flat_part = make_building(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
    )

    AtlasFoundationSceneBuilder._attach_building_roof_metadata(
        mesh={},
        atlas_building=gable_building,
        is_building_part=False,
        profile_counts=profile_counts,
        decision_source_counts=decision_source_counts,
    )
    AtlasFoundationSceneBuilder._attach_building_roof_metadata(
        mesh={},
        atlas_building=flat_part,
        is_building_part=True,
        profile_counts=profile_counts,
        decision_source_counts=decision_source_counts,
    )

    assert profile_counts == {
        "gable": 1,
        "flat": 1,
    }
    assert decision_source_counts == {
        "inferred": 1,
        "building_part": 1,
    }


def test_foundation_scene_applies_gable_roof_geometry(
    monkeypatch,
):
    bottom = [
        (0.0, 0.0, 0.0),
        (8.0, 0.0, 0.0),
        (8.0, 3.0, 0.0),
        (0.0, 3.0, 0.0),
    ]

    top = [
        (0.0, 0.0, 4.0),
        (8.0, 0.0, 4.0),
        (8.0, 3.0, 4.0),
        (0.0, 3.0, 4.0),
    ]

    original_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    mesh = {
        "bottom": bottom,
        "top": top,
        "walls": [
            (
                bottom[0],
                bottom[1],
                top[1],
                top[0],
            ),
            (
                bottom[1],
                bottom[2],
                top[2],
                top[1],
            ),
            (
                bottom[2],
                bottom[3],
                top[3],
                top[2],
            ),
            (
                bottom[3],
                bottom[0],
                top[0],
                top[3],
            ),
        ],
        "triangles": list(original_triangles),
        "bottom_z": 0.0,
        "top_z": 4.0,
    }

    atlas_building = SimpleNamespace(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0040),
            (39.0010, 32.0040),
            (39.0010, 32.0000),
        ],
        tags={"building": "yes"},
        roof_type=None,
        is_castle_building=False,
        castle_profile=None,
        castle_roof_profile=None,
        estimated_height=4.0,
    )

    raw_building = {
        "id": 601,
        "geometry": atlas_building.geometry,
        "tags": atlas_building.tags,
    }

    monkeypatch.setattr(
        AtlasSceneBuilder,
        "_is_raw_building_usable",
        staticmethod(lambda *args, **kwargs: True),
    )

    monkeypatch.setattr(
        AtlasSceneBuilder,
        "_to_atlas_building",
        staticmethod(lambda raw: atlas_building),
    )

    monkeypatch.setattr(
        AtlasCastleFootprintRegularizer,
        "prepare",
        staticmethod(
            lambda raw_building, castles: raw_building
        ),
    )

    monkeypatch.setattr(
        AtlasCastleBuildingProfiler,
        "apply_to_building",
        staticmethod(
            lambda atlas_building, raw_building, castles: (
                atlas_building
            )
        ),
    )

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "build_building_mesh",
        staticmethod(lambda **kwargs: mesh),
    )

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[raw_building],
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=[],
        debug=False,
    )

    result_mesh = scene.layers["buildings"][0]

    assert result_mesh["building_roof_profile"] == "gable"
    assert result_mesh["building_gable_roof_applied"] is True
    assert result_mesh["roof_geometry"] == "gable"

    assert len(
        result_mesh["building_gable_roof_triangles"]
    ) == 8

    assert len(result_mesh["triangles"]) == (
        len(original_triangles) + 8
    )


def test_foundation_scene_applies_hipped_roof_geometry(
    monkeypatch,
):
    bottom = [
        (0.0, 0.0, 0.0),
        (6.0, 0.0, 0.0),
        (6.0, 5.0, 0.0),
        (0.0, 5.0, 0.0),
    ]

    top = [
        (0.0, 0.0, 4.0),
        (6.0, 0.0, 4.0),
        (6.0, 5.0, 4.0),
        (0.0, 5.0, 4.0),
    ]

    original_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    mesh = {
        "bottom": bottom,
        "top": top,
        "walls": [
            (bottom[0], bottom[1], top[1], top[0]),
            (bottom[1], bottom[2], top[2], top[1]),
            (bottom[2], bottom[3], top[3], top[2]),
            (bottom[3], bottom[0], top[0], top[3]),
        ],
        "triangles": list(original_triangles),
        "foundation_z": 0.0,
    }

    atlas_building = SimpleNamespace(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0030),
            (39.0025, 32.0030),
            (39.0025, 32.0000),
        ],
        tags={"building": "yes"},
        roof_type=None,
        is_castle_building=False,
        castle_profile=None,
        castle_roof_profile=None,
        estimated_height=4.0,
    )

    raw_building = {
        "id": 603,
        "geometry": atlas_building.geometry,
        "tags": atlas_building.tags,
    }

    monkeypatch.setattr(
        AtlasSceneBuilder,
        "_is_raw_building_usable",
        staticmethod(lambda *args, **kwargs: True),
    )

    monkeypatch.setattr(
        AtlasSceneBuilder,
        "_to_atlas_building",
        staticmethod(lambda raw: atlas_building),
    )

    monkeypatch.setattr(
        AtlasCastleFootprintRegularizer,
        "prepare",
        staticmethod(
            lambda raw_building, castles: raw_building
        ),
    )

    monkeypatch.setattr(
        AtlasCastleBuildingProfiler,
        "apply_to_building",
        staticmethod(
            lambda atlas_building, raw_building, castles: (
                atlas_building
            )
        ),
    )

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "build_building_mesh",
        staticmethod(
            lambda *args, **kwargs: mesh
        ),
    )

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[raw_building],
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=[],
        debug=False,
    )

    result_mesh = scene.layers["buildings"][0]

    assert result_mesh["building_roof_profile"] == "hipped"
    assert result_mesh["building_hipped_roof_applied"] is True
    assert result_mesh["roof_geometry"] == "hipped"
    assert result_mesh["building_hipped_removed_top_triangles"] == 2
    assert len(result_mesh["building_hipped_roof_triangles"]) == 4
    assert len(result_mesh["triangles"]) == 14


def test_mausoleum_building_is_forced_to_flat_roof_metadata():
    building = make_building(
        geometry=[
            (39.0000, 32.0000),
            (39.0000, 32.0010),
            (39.0010, 32.0010),
            (39.0010, 32.0000),
        ],
    )
    building.tags.update(
        {
            "historic": "tomb",
            "tomb": "mausoleum",
        }
    )

    result = (
        AtlasFoundationSceneBuilder
        ._building_roof_metadata(
            atlas_building=building,
            is_building_part=False,
        )
    )

    assert result["building_roof_profile"] == "flat"
    assert (
        result["building_roof_decision_source"]
        == "monument"
    )


def test_mausoleum_parent_marks_building_part_as_monument_column():
    raw_part = {
        "id": 101,
        "geometry": [
            (39.0000, 32.0000),
            (39.0000, 32.0001),
            (39.0001, 32.0001),
            (39.0001, 32.0000),
        ],
        "tags": {
            "building:part": "yes",
            "height": "15",
        },
    }
    parent_record = {
        "id": 202,
        "tags": {
            "building": "yes",
            "historic": "tomb",
            "tomb": "mausoleum",
        },
    }

    result = (
        AtlasFoundationSceneBuilder
        ._mark_monument_column_part(
            raw_building=raw_part,
            parent_record=parent_record,
        )
    )

    assert result is not raw_part
    assert result["tags"] is not raw_part["tags"]
    assert (
        result["tags"]["atlas:monument_column_part"]
        == "yes"
    )
    assert (
        "atlas:monument_column_part"
        not in raw_part["tags"]
    )


def test_normal_parent_does_not_mark_building_part_as_monument_column():
    raw_part = {
        "id": 101,
        "geometry": [
            (39.0000, 32.0000),
            (39.0000, 32.0001),
            (39.0001, 32.0001),
            (39.0001, 32.0000),
        ],
        "tags": {
            "building:part": "yes",
        },
    }
    parent_record = {
        "id": 202,
        "tags": {
            "building": "yes",
        },
    }

    result = (
        AtlasFoundationSceneBuilder
        ._mark_monument_column_part(
            raw_building=raw_part,
            parent_record=parent_record,
        )
    )

    assert result is raw_part
    assert (
        "atlas:monument_column_part"
        not in result["tags"]
    )


def test_elevated_component_inside_mausoleum_is_special_architecture():
    building = make_building(
        geometry=[
            (39.0002, 32.0002),
            (39.0002, 32.0008),
            (39.0008, 32.0008),
            (39.0008, 32.0002),
        ],
    )
    building.tags.update(
        {
            "building:min_level": "6",
            "min_height": "22",
            "height": "25",
        }
    )

    parent_record = {
        "id": 28241512,
        "geometry": [
            (39.0000, 32.0000),
            (39.0000, 32.0010),
            (39.0010, 32.0010),
            (39.0010, 32.0000),
        ],
        "tags": {
            "building": "yes",
            "historic": "tomb",
            "tomb": "mausoleum",
        },
    }

    assert (
        AtlasFoundationSceneBuilder
        ._is_special_architectural_component(
            atlas_building=building,
            containing_parent_record=parent_record,
        )
        is True
    )


def test_finds_smallest_containing_special_architectural_parent():
    target_record = {
        "id": 397750660,
        "geometry": [
            (39.0000033, 32.0000000),
            (39.0000033, 32.0010000),
            (39.0010033, 32.0010000),
            (39.0010033, 32.0000000),
        ],
        "tags": {
            "building": "yes",
            "min_height": "22",
            "building:min_level": "6",
        },
    }

    mausoleum_record = {
        "id": 28241512,
        "geometry": [
            (39.0000, 32.0000),
            (39.0000, 32.0010),
            (39.0010, 32.0010),
            (39.0010, 32.0000),
        ],
        "tags": {
            "building": "yes",
            "historic": "tomb",
            "tomb": "mausoleum",
        },
    }

    unrelated_record = {
        "id": 999,
        "geometry": [
            (40.0000, 33.0000),
            (40.0000, 33.0010),
            (40.0010, 33.0010),
            (40.0010, 33.0000),
        ],
        "tags": {
            "building": "yes",
        },
    }

    result = (
        AtlasFoundationSceneBuilder
        ._find_containing_special_parent_record(
            raw_building=target_record,
            raw_buildings=[
                target_record,
                mausoleum_record,
                unrelated_record,
            ],
        )
    )

    assert result["id"] == 28241512


def test_all_parents_with_parts_require_shared_foundation_cache():
    hierarchy = {
        "parents": {
            100: {
                "parent": {"id": 100},
                "part_ids": [101],
            },
            200: {
                "parent": {"id": 200},
                "part_ids": [201, 202],
            },
        },
        "suppressed_parent_ids": [200],
    }

    result = (
        AtlasFoundationSceneBuilder
        ._shared_foundation_parent_ids(hierarchy)
    )

    assert result == {100, 200}


def test_foundation_scene_applies_pyramidal_roof_geometry(
    monkeypatch,
):
    bottom = [
        (0.0, 0.0, 0.0),
        (6.0, 0.0, 0.0),
        (6.0, 6.0, 0.0),
        (0.0, 6.0, 0.0),
    ]

    top = [
        (0.0, 0.0, 14.0),
        (6.0, 0.0, 14.0),
        (6.0, 6.0, 14.0),
        (0.0, 6.0, 14.0),
    ]

    original_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    mesh = {
        "bottom": bottom,
        "top": top,
        "walls": [
            (bottom[0], bottom[1], top[1], top[0]),
            (bottom[1], bottom[2], top[2], top[1]),
            (bottom[2], bottom[3], top[3], top[2]),
            (bottom[3], bottom[0], top[0], top[3]),
        ],
        "triangles": list(original_triangles),
        "foundation_z": 0.0,
        "bottom_z": 0.0,
        "top_z": 14.0,
    }

    tags = {
        "building:part": "yes",
        "height": "82",
        "roof:shape": "pyramidal",
        "roof:height": "40",
    }

    atlas_building = SimpleNamespace(
        geometry=[
            (50.73340, 7.09960),
            (50.73340, 7.09980),
            (50.73360, 7.09980),
            (50.73360, 7.09960),
        ],
        tags=tags,
        roof_type="pyramidal",
        is_castle_building=False,
        castle_profile=None,
        castle_roof_profile=None,
        estimated_height=82.0,
    )

    raw_building = {
        "id": 321760769,
        "geometry": atlas_building.geometry,
        "tags": tags,
    }

    coordinate_engine = SimpleNamespace(
        scale_ratio=3000.0,
    )

    monkeypatch.setattr(
        AtlasSceneBuilder,
        "_is_raw_building_usable",
        staticmethod(lambda *args, **kwargs: True),
    )

    monkeypatch.setattr(
        AtlasSceneBuilder,
        "_to_atlas_building",
        staticmethod(lambda raw: atlas_building),
    )

    monkeypatch.setattr(
        AtlasCastleFootprintRegularizer,
        "prepare",
        staticmethod(
            lambda raw_building, castles: raw_building
        ),
    )

    monkeypatch.setattr(
        AtlasCastleBuildingProfiler,
        "apply_to_building",
        staticmethod(
            lambda atlas_building, raw_building, castles: (
                atlas_building
            )
        ),
    )

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "build_building_mesh",
        staticmethod(
            lambda *args, **kwargs: mesh
        ),
    )

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[raw_building],
        coordinate_engine=coordinate_engine,
        terrain_mesh=object(),
        castles=[],
        debug=False,
    )

    result_mesh = scene.layers["buildings"][0]

    assert result_mesh["building_roof_profile"] == "pyramidal"
    assert result_mesh["building_pyramidal_roof_applied"] is True
    assert result_mesh["roof_geometry"] == "pyramidal"
    assert result_mesh["roof_height_mm"] == pytest.approx(
        40_000.0 / 3000.0
    )
    assert result_mesh["body_top_z"] == pytest.approx(14.0)
    assert result_mesh["roof_top_z"] == pytest.approx(
        14.0 + 40_000.0 / 3000.0
    )
    assert (
        result_mesh[
            "building_pyramidal_removed_top_triangles"
        ]
        == 2
    )
    assert len(
        result_mesh[
            "building_pyramidal_roof_triangles"
        ]
    ) == 4
    assert len(result_mesh["triangles"]) == 14
