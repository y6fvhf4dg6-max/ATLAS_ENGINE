"""
ATLAS Foundation Scene Building Report Regression Tests

Bina gövdesi üretiminde oluşan reddetme nedenlerinin sahne
metadata raporunda toplandığını doğrular.
"""

from types import SimpleNamespace

from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
)
from CORE.atlas_foundation_first_pipeline import (
    AtlasFoundationFirstPipeline,
)
from CORE.atlas_castle_building_profiler import (
    AtlasCastleBuildingProfiler,
)
from CORE.atlas_castle_footprint_regularizer import (
    AtlasCastleFootprintRegularizer,
)
from CORE.atlas_scene_builder import AtlasSceneBuilder


def test_scene_collects_mesh_rejection_reason(monkeypatch):
    raw_building = {
        "id": 101,
        "geometry": [
            (41.0, 29.0),
            (41.0, 29.1),
            (41.1, 29.1),
            (41.1, 29.0),
        ],
        "tags": {
            "building": "yes",
        },
    }

    atlas_building = SimpleNamespace(
        estimated_height=8.0,
        is_castle_building=False,
        castle_profile=None,
        castle_roof_profile=None,
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

    def reject_building(**kwargs):
        diagnostics = kwargs["diagnostics"]
        diagnostics.update(
            {
                "accepted": False,
                "reason": "model_width_below_minimum",
            }
        )
        return None

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "build_building_mesh",
        staticmethod(reject_building),
    )

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[raw_building],
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=[],
        debug=False,
    )

    report = scene.metadata["building_report"]

    assert report["accepted"] == 0
    assert report["skipped"] == 1
    assert report["castle_buildings"] == 0
    assert report["rejection_counts"] == {
        "model_width_below_minimum": 1,
    }


def test_scene_counts_bbox_rejection():
    raw_building = {
        "id": 202,
        "geometry": [
            (40.0, 28.0),
            (40.0, 28.1),
            (40.1, 28.1),
            (40.1, 28.0),
        ],
        "tags": {
            "building": "yes",
        },
    }

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[raw_building],
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=[],
        bbox=(41.0, 29.0, 41.1, 29.1),
        debug=False,
    )

    report = scene.metadata["building_report"]

    assert report["accepted"] == 0
    assert report["skipped"] == 1
    assert report["rejection_counts"] == {
        "outside_bbox": 1,
    }



def test_pipeline_reports_temporary_mesh_failure(monkeypatch):
    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline.AtlasMeshBuilder.build_mesh",
        lambda *args, **kwargs: None,
    )

    diagnostics = {}

    mesh = AtlasFoundationFirstPipeline.build_building_mesh(
        building=object(),
        coordinate_engine=object(),
        terrain_mesh=object(),
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics == {
        "accepted": False,
        "reason": "temporary_mesh_failed",
    }


def test_pipeline_reports_foundation_surface_failure(monkeypatch):
    temporary_mesh = {
        "bottom": [
            (0.0, 0.0, 0.0),
            (2.0, 0.0, 0.0),
            (2.0, 2.0, 0.0),
        ],
        "top": [],
        "triangles": [],
    }

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline.AtlasMeshBuilder.build_mesh",
        lambda *args, **kwargs: temporary_mesh,
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationSurfaceBuilder.build_surface",
        lambda *args, **kwargs: None,
    )

    diagnostics = {}

    mesh = AtlasFoundationFirstPipeline.build_building_mesh(
        building=object(),
        coordinate_engine=object(),
        terrain_mesh=object(),
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics == {
        "accepted": False,
        "reason": "foundation_surface_failed",
    }



def test_pipeline_preserves_temporary_mesh_rejection_reason(monkeypatch):
    def reject_mesh(*args, **kwargs):
        diagnostics = kwargs["diagnostics"]
        diagnostics.update(
            {
                "accepted": False,
                "reason": "building_area_below_minimum",
            }
        )
        return None

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline.AtlasMeshBuilder.build_mesh",
        reject_mesh,
    )

    diagnostics = {}

    mesh = AtlasFoundationFirstPipeline.build_building_mesh(
        building=object(),
        coordinate_engine=object(),
        terrain_mesh=object(),
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics == {
        "accepted": False,
        "reason": "building_area_below_minimum",
    }


def test_pipeline_uses_explicit_foundation_z_override(monkeypatch):
    temporary_mesh = {
        "bottom": [
            (0.0, 0.0, 0.0),
            (2.0, 0.0, 0.0),
            (2.0, 2.0, 0.0),
        ],
        "top": [],
        "triangles": [],
    }

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasMeshBuilder.build_mesh",
        lambda *args, **kwargs: temporary_mesh,
    )

    def fail_if_surface_is_sampled(*args, **kwargs):
        raise AssertionError(
            "Foundation surface must not be sampled "
            "when an override is supplied"
        )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationSurfaceBuilder.build_surface",
        fail_if_surface_is_sampled,
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationMeshBuilder.build",
        lambda footprint_points, foundation_z: {
            "foundation_z": foundation_z,
        },
    )

    def fake_extrude(
        building,
        coordinate_engine,
        foundation_z,
        diagnostics=None,
        debug=False,
    ):
        return {
            "bottom": [
                (0.0, 0.0, foundation_z),
                (2.0, 0.0, foundation_z),
                (2.0, 2.0, foundation_z),
            ],
            "top": [],
            "triangles": [],
        }

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationMeshExtruder.extrude",
        fake_extrude,
    )

    mesh = AtlasFoundationFirstPipeline.build_building_mesh(
        building=object(),
        coordinate_engine=object(),
        terrain_mesh=object(),
        foundation_z_override=7.25,
    )

    assert mesh is not None
    assert mesh["foundation_z"] == 7.25
    assert mesh["foundation_surface"]["sample_mode"] == "override"
    assert mesh["foundation_surface"]["sample_count"] == 0
    assert mesh["foundation_mesh"]["foundation_z"] == 7.25

    assert {
        round(point[2], 6)
        for point in mesh["bottom"]
    } == {
        7.25,
    }


def test_scene_rejects_invalid_final_topology_after_post_processing(
    monkeypatch,
):
    raw_building = {
        "id": 303,
        "geometry": [
            (41.0, 29.0),
            (41.0, 29.1),
            (41.1, 29.1),
            (41.1, 29.0),
        ],
        "tags": {
            "building": "yes",
        },
    }

    atlas_building = SimpleNamespace(
        estimated_height=9.0,
        is_castle_building=False,
        castle_profile=None,
        castle_roof_profile=None,
        is_building_part=False,
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
        "CORE.atlas_foundation_scene_builder."
        "AtlasAncientTheatreProfiler.apply_to_building",
        lambda **kwargs: kwargs["atlas_building"],
    )

    def fake_build(**kwargs):
        return {
            "type": "building",
            "triangles": (
                (
                    (0.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0),
                    (0.0, 1.0, 0.0),
                ),
            ),
            "foundation_z": 0.0,
            "is_castle_building": False,
        }

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "build_building_mesh",
        staticmethod(fake_build),
    )

    monkeypatch.setattr(
        AtlasFoundationSceneBuilder,
        "_attach_building_roof_metadata",
        staticmethod(
            lambda **kwargs: kwargs["mesh"]
        ),
    )

    def passthrough_mesh(*args, **kwargs):
        if "mesh" in kwargs:
            return kwargs["mesh"]

        if "minaret_mesh" in kwargs:
            return kwargs["minaret_mesh"]

        if args:
            return args[0]

        raise AssertionError(
            "post-processing passthrough received no mesh"
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
            f"CORE.atlas_foundation_scene_builder."
            f"{name}.apply",
            passthrough_mesh,
        )

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasMinaretBalconyBuilder.attach",
        passthrough_mesh,
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_scene_builder."
        "AtlasLiedbergGateTowerBuilder.build",
        lambda **kwargs: None,
    )

    def invalid_final_report(mesh):
        return {
            "valid": False,
            "structure_valid": True,
            "triangles": len(
                mesh.get("triangles", ())
            ),
            "open_edge_count": 8,
            "non_manifold_edge_count": 0,
            "sample_open_edges": [],
            "sample_non_manifold_edges": [],
        }

    monkeypatch.setattr(
        "CORE.atlas_mesh_validator."
        "AtlasMeshValidator.report",
        invalid_final_report,
    )

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[raw_building],
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=[],
        debug=False,
    )

    report = scene.metadata["building_report"]

    assert scene.layers["buildings"] == []
    assert report["accepted"] == 0
    assert report["skipped"] == 1
    assert report["rejection_counts"] == {
        "invalid_final_mesh_topology": 1,
    }
