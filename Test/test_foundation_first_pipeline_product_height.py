import pytest

from CORE.atlas_foundation_first_pipeline import (
    AtlasFoundationFirstPipeline,
)


def test_foundation_first_pipeline_propagates_product_height_override(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasMeshBuilder.build_mesh",
        lambda *args, **kwargs: {
            "bottom": (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (1.0, 1.0, 0.0),
            ),
            "triangles": (),
        },
    )

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "_mesh_xy_bounds",
        staticmethod(
            lambda mesh: (
                0.0,
                0.0,
                1.0,
                1.0,
            )
        ),
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationSurfaceBuilder.build_surface",
        lambda **kwargs: {
            "foundation_z": 0.50,
        },
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationMeshBuilder.build",
        lambda **kwargs: {
            "triangles": (),
        },
    )

    def fake_extrude(**kwargs):
        captured.update(kwargs)
        return {
            "triangles": (),
        }

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationMeshExtruder.extrude",
        fake_extrude,
    )

    building = object()
    coordinate_engine = object()
    terrain_mesh = object()

    result = AtlasFoundationFirstPipeline.build_building_mesh(
        building=building,
        coordinate_engine=coordinate_engine,
        terrain_mesh=terrain_mesh,
        product_height_m=12.0,
    )

    assert captured["product_height_m"] == pytest.approx(12.0)
    assert captured["building"] is building
    assert result["foundation_z"] == pytest.approx(0.50)


def test_foundation_first_pipeline_keeps_product_height_opt_in(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasMeshBuilder.build_mesh",
        lambda *args, **kwargs: {
            "bottom": (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (1.0, 1.0, 0.0),
            ),
            "triangles": (),
        },
    )

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "_mesh_xy_bounds",
        staticmethod(
            lambda mesh: (
                0.0,
                0.0,
                1.0,
                1.0,
            )
        ),
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationSurfaceBuilder.build_surface",
        lambda **kwargs: {
            "foundation_z": 0.50,
        },
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationMeshBuilder.build",
        lambda **kwargs: {
            "triangles": (),
        },
    )

    def fake_extrude(**kwargs):
        captured.update(kwargs)
        return {
            "triangles": (),
        }

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_pipeline."
        "AtlasFoundationMeshExtruder.extrude",
        fake_extrude,
    )

    AtlasFoundationFirstPipeline.build_building_mesh(
        building=object(),
        coordinate_engine=object(),
        terrain_mesh=object(),
    )

    assert "product_height_m" not in captured
