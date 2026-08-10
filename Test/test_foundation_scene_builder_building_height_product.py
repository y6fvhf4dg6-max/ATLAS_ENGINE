from types import SimpleNamespace

import pytest

from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
)


def _building(
    *,
    estimated_height=24.0,
    is_castle_building=False,
    is_building_part=False,
):
    return SimpleNamespace(
        estimated_height=float(estimated_height),
        is_castle_building=is_castle_building,
        is_building_part=is_building_part,
        tags=(
            {"building:part": "yes"}
            if is_building_part
            else {"building": "yes"}
        ),
    )


def test_scene_builder_resolves_generic_product_height_from_block_context():
    result = (
        AtlasFoundationSceneBuilder
        ._resolve_building_product_height(
            atlas_building=_building(
                estimated_height=24.0,
            ),
            source_id=100,
            scale_ratio=5500.0,
            context_by_source_id={
                100: {
                    "block_median_height_m": 10.0,
                    "landmark_distance_m": 120.0,
                    "semantic_importance": 0.20,
                },
            },
            minimum_readable_height_mm=2.0,
        )
    )

    assert result is not None

    assert result.source_height_m == pytest.approx(
        24.0
    )
    assert result.normalized_height_m < 24.0
    assert result.changed is True

    # Canonical source truth must remain untouched.
    assert (
        _building(
            estimated_height=24.0
        ).estimated_height
        == pytest.approx(24.0)
    )


def test_scene_builder_does_not_apply_generic_normalizer_to_castle():
    result = (
        AtlasFoundationSceneBuilder
        ._resolve_building_product_height(
            atlas_building=_building(
                estimated_height=24.0,
                is_castle_building=True,
            ),
            source_id=100,
            scale_ratio=5500.0,
            context_by_source_id={
                100: {
                    "block_median_height_m": 10.0,
                    "landmark_distance_m": 120.0,
                    "semantic_importance": 0.20,
                },
            },
            minimum_readable_height_mm=2.0,
        )
    )

    assert result is None


def test_scene_builder_does_not_normalize_building_parts_as_generic_buildings():
    result = (
        AtlasFoundationSceneBuilder
        ._resolve_building_product_height(
            atlas_building=_building(
                estimated_height=24.0,
                is_building_part=True,
            ),
            source_id=100,
            scale_ratio=5500.0,
            context_by_source_id={
                100: {
                    "block_median_height_m": 10.0,
                    "landmark_distance_m": 120.0,
                    "semantic_importance": 0.20,
                },
            },
            minimum_readable_height_mm=2.0,
        )
    )

    assert result is None


def test_scene_builder_returns_none_without_resolved_block_context():
    result = (
        AtlasFoundationSceneBuilder
        ._resolve_building_product_height(
            atlas_building=_building(),
            source_id=999,
            scale_ratio=5500.0,
            context_by_source_id={},
            minimum_readable_height_mm=2.0,
        )
    )

    assert result is None


def test_scene_builder_build_scene_propagates_normalized_product_height(
    monkeypatch,
):
    captured = {}

    raw_building = {
        "id": 100,
        "geometry": (
            (50.0, 8.0),
            (50.0, 8.001),
            (50.001, 8.001),
            (50.001, 8.0),
        ),
        "tags": {
            "building": "yes",
            "height": "24",
        },
    }

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasBuildingPartHierarchyProfiler.analyze",
        lambda buildings: {
            "mesh_buildings": list(buildings),
            "parents": {},
            "part_to_parent": {},
            "suppressed_parent_ids": set(),
            "minaret_components_by_minaret": {},
            "summary": {
                "parent_with_parts_count": 0,
                "assigned_building_part_count": 0,
                "unassigned_building_part_count": 0,
                "parent_part_counts": {},
                "suppressed_parent_count": 0,
            },
        },
    )

    monkeypatch.setattr(
        "CORE.atlas_scene_builder."
        "AtlasSceneBuilder._is_raw_building_usable",
        lambda *args, **kwargs: True,
    )

    class FakeBuilding:
        estimated_height = 24.0
        is_castle_building = False
        is_building_part = False
        tags = {"building": "yes", "height": "24"}

    monkeypatch.setattr(
        "CORE.atlas_scene_builder."
        "AtlasSceneBuilder._to_atlas_building",
        lambda record: FakeBuilding(),
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasCastleFootprintRegularizer.prepare",
        lambda **kwargs: kwargs["raw_building"],
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasCastleBuildingProfiler.apply_to_building",
        lambda **kwargs: kwargs["atlas_building"],
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasAncientTheatreProfiler.apply_to_building",
        lambda **kwargs: kwargs["atlas_building"],
    )

    def fake_build(**kwargs):
        captured["product_height_m"] = kwargs.get(
            "product_height_m"
        )
        return {
            "triangles": (),
            "foundation_z": 0.5,
            "is_castle_building": False,
        }

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasFoundationFirstPipeline.build_building_mesh",
        fake_build,
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasFoundationSceneBuilder._attach_building_roof_metadata",
        lambda **kwargs: kwargs["mesh"],
    )

    def passthrough_mesh(*args, **kwargs):
        if "mesh" in kwargs:
            return kwargs["mesh"]

        if args:
            return args[0]

        raise AssertionError(
            "roof passthrough received no mesh"
        )

    for name in (
        "AtlasBuildingGableRoofBuilder",
        "AtlasBuildingHippedRoofBuilder",
        "AtlasBuildingPyramidalRoofBuilder",
        "AtlasBuildingSkillionRoofBuilder",
        "AtlasBuildingApseGabledRoofBuilder",
        "AtlasMinaretRoofBuilder",
        "AtlasMonumentDomeRoofBuilder",
        "AtlasCastleRoofBuilder",
        "AtlasCastleGableRoofBuilder",
        "AtlasCastleMultiGableRoofBuilder",
    ):
        monkeypatch.setattr(
            f"CORE.atlas_foundation_scene_builder.{name}.apply",
            passthrough_mesh,
        )

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasMeshValidator.report",
        lambda mesh: {
            "valid": True,
            "open_edge_count": 0,
            "non_manifold_edge_count": 0,
        },
    )

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=(raw_building,),
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=(),
        xy_scale=5500.0,
        z_scale=5500.0,
        building_height_context_by_source_id={
            100: {
                "block_median_height_m": 10.0,
                "landmark_distance_m": 120.0,
                "semantic_importance": 0.20,
            },
        },
        building_minimum_readable_height_mm=2.0,
        debug=False,
    )

    assert captured["product_height_m"] < 24.0

    mesh = scene.get_all_meshes()[0]

    assert mesh["estimated_height_m"] == pytest.approx(24.0)
    assert mesh["product_height_m"] < 24.0
    assert mesh["height_product_normalization_changed"] is True
