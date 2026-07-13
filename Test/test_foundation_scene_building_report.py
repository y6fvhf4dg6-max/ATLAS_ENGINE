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
