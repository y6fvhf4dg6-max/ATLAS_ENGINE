from types import SimpleNamespace

from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
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
