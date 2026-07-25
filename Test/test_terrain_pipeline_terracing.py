import pytest

from CORE.atlas_terrain_pipeline import (
    AtlasTerrainPipeline,
)


class FlatTerrainProvider:
    def get_height(
        self,
        lat,
        lon,
    ):
        return 100.0


class SlopedTerrainProvider:
    def get_height(
        self,
        lat,
        lon,
    ):
        return 100.0 + lat * 10.0 + lon * 20.0


def _patch_srtm_provider(
    monkeypatch,
    provider,
):
    monkeypatch.setattr(
        "CORE.atlas_terrain_pipeline.AtlasSRTMProvider",
        lambda data_dir, debug: provider,
    )


def test_pipeline_keeps_existing_closed_slab_when_terracing_disabled(
    monkeypatch,
):
    _patch_srtm_provider(
        monkeypatch,
        FlatTerrainProvider(),
    )

    mesh = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(0.0, 0.0, 1.0, 1.0),
        target_size_mm=20.0,
        size_x_mm=20.0,
        size_y_mm=20.0,
        z_scale=1000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=3,
        terrace_step_mm=None,
        debug=False,
    )

    assert mesh["type"] == "terrain_closed_slab"
    assert mesh["metadata"]["closed"] is True
    assert mesh["metadata"].get("terraced") is not True
    assert "cell_levels" not in mesh


def test_pipeline_builds_closed_terraced_slab_when_enabled(
    monkeypatch,
):
    _patch_srtm_provider(
        monkeypatch,
        SlopedTerrainProvider(),
    )

    mesh = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(0.0, 0.0, 1.0, 1.0),
        target_size_mm=20.0,
        size_x_mm=20.0,
        size_y_mm=20.0,
        z_scale=1000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=3,
        terrace_step_mm=0.30,
        debug=False,
    )

    assert mesh["type"] == "terrain_terraced_closed_slab"
    assert mesh["metadata"]["closed"] is True
    assert mesh["metadata"]["terraced"] is True
    assert mesh["metadata"]["terrace_step_mm"] == pytest.approx(
        0.30
    )

    assert len(mesh["cell_levels"]) == 2
    assert all(
        len(row) == 2
        for row in mesh["cell_levels"]
    )


def test_pipeline_preserves_terrain_grid_and_geographic_metadata(
    monkeypatch,
):
    _patch_srtm_provider(
        monkeypatch,
        SlopedTerrainProvider(),
    )

    mesh = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(1.0, 2.0, 3.0, 4.0),
        target_size_mm=20.0,
        size_x_mm=20.0,
        size_y_mm=10.0,
        z_scale=1000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=3,
        terrace_step_mm=0.30,
        debug=False,
    )

    assert mesh["grid"]["sample_count"] == 9
    assert mesh["metadata"]["bbox"] == (
        1.0,
        2.0,
        3.0,
        4.0,
    )
    assert mesh["metadata"]["grid_size"] == 3
    assert mesh["metadata"]["size_x_mm"] == pytest.approx(
        20.0
    )
    assert mesh["metadata"]["size_y_mm"] == pytest.approx(
        10.0
    )
    assert mesh["metadata"]["z_scale"] == pytest.approx(
        1000.0
    )
    assert mesh["metadata"]["base_z"] == pytest.approx(
        0.80
    )
    assert mesh["metadata"]["bottom_z"] == pytest.approx(
        0.0
    )


def test_pipeline_terraced_top_points_match_cell_grid_dimensions(
    monkeypatch,
):
    _patch_srtm_provider(
        monkeypatch,
        SlopedTerrainProvider(),
    )

    mesh = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(0.0, 0.0, 1.0, 1.0),
        target_size_mm=20.0,
        size_x_mm=20.0,
        size_y_mm=20.0,
        z_scale=1000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=4,
        terrace_step_mm=0.30,
        debug=False,
    )

    assert len(mesh["top_points"]) == 4
    assert all(
        len(row) == 4
        for row in mesh["top_points"]
    )

    assert len(mesh["cell_levels"]) == 3
    assert all(
        len(row) == 3
        for row in mesh["cell_levels"]
    )


def test_pipeline_rejects_non_positive_terrace_step(
    monkeypatch,
):
    _patch_srtm_provider(
        monkeypatch,
        FlatTerrainProvider(),
    )

    with pytest.raises(
        ValueError,
        match="terrace_step_mm",
    ):
        AtlasTerrainPipeline.build_terrain_slab(
            bbox=(0.0, 0.0, 1.0, 1.0),
            target_size_mm=20.0,
            z_scale=1000.0,
            base_z=0.80,
            bottom_z=0.0,
            grid_size=3,
            terrace_step_mm=0.0,
            debug=False,
        )
