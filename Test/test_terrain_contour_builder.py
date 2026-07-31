from CORE.atlas_terrain_contour_builder import (
    AtlasTerrainContourBuilder,
)


def test_empty_grid_returns_empty_result():
    result = AtlasTerrainContourBuilder.build(
        top_points=[],
        base_z=0.8,
        contour_step_mm=0.4,
        band_half_width_mm=0.15,
    )

    assert result["triangles"] == []
    assert result["metadata"]["contour_step_mm"] == 0.4
    assert result["metadata"]["band_half_width_mm"] == 0.15


def test_metadata_contains_contour_parameters():
    result = AtlasTerrainContourBuilder.build(
        top_points=[],
        base_z=0.8,
        contour_step_mm=0.4,
        band_half_width_mm=0.15,
    )

    assert result["metadata"]["contour_step_mm"] == 0.4
    assert result["metadata"]["band_half_width_mm"] == 0.15

def test_empty_top_points_skip_processing():
    result = AtlasTerrainContourBuilder.build(
        top_points=[],
        base_z=0.8,
        contour_step_mm=0.4,
        band_half_width_mm=0.15,
    )

    assert result["triangles"] == []
    assert result["metadata"]["contour_count"] == 0
    assert result["metadata"]["band_count"] == 0


from unittest.mock import patch


@patch(
    "CORE.atlas_terrain_contour_builder."
    "AtlasTerrainContourTerraceBuilder"
)
def test_builder_calls_contour_extractor(
    terrace_builder,
):
    terrace_builder.extract_contours.return_value = []

    AtlasTerrainContourBuilder.build(
        top_points=[
            [(0.0, 0.0, 1.0)],
        ],
        base_z=0.8,
        contour_step_mm=0.4,
        band_half_width_mm=0.15,
    )

    terrace_builder.extract_contours.assert_called_once()


from unittest.mock import patch


@patch(
    "CORE.atlas_terrain_contour_builder."
    "AtlasTerrainContourTerraceBuilder"
)
def test_builder_reports_contour_count(
    terrace_builder,
):
    terrace_builder.extract_contours.return_value = [
        [(0.0, 0.0), (1.0, 0.0)],
        [(2.0, 0.0), (3.0, 0.0)],
    ]

    result = AtlasTerrainContourBuilder.build(
        top_points=[
            [(0.0, 0.0, 1.0)],
        ],
        base_z=0.8,
        contour_step_mm=0.4,
        band_half_width_mm=0.15,
    )

    assert result["metadata"]["contour_count"] == 2


from unittest.mock import patch


@patch(
    "CORE.atlas_terrain_contour_builder."
    "AtlasTerrainContourBandBuilder"
)
@patch(
    "CORE.atlas_terrain_contour_builder."
    "AtlasTerrainContourTerraceBuilder"
)
def test_builder_builds_band_for_each_contour(
    terrace_builder,
    band_builder,
):
    terrace_builder.extract_contours.return_value = [
        [(0.0, 0.0), (1.0, 0.0)],
        [(2.0, 0.0), (3.0, 0.0)],
    ]

    band_builder.build_band.return_value = []

    AtlasTerrainContourBuilder.build(
        top_points=[
            [(0.0, 0.0, 1.0)],
        ],
        base_z=0.8,
        contour_step_mm=0.4,
        band_half_width_mm=0.15,
    )

    assert band_builder.build_band.call_count == 2


from unittest.mock import patch


@patch(
    "CORE.atlas_terrain_contour_builder."
    "AtlasTerrainContourMeshBuilder"
)
@patch(
    "CORE.atlas_terrain_contour_builder."
    "AtlasTerrainContourBandBuilder"
)
@patch(
    "CORE.atlas_terrain_contour_builder."
    "AtlasTerrainContourTerraceBuilder"
)
def test_builder_builds_mesh_from_bands(
    terrace_builder,
    band_builder,
    mesh_builder,
):
    terrace_builder.extract_contours.return_value = [
        [(0.0, 0.0), (1.0, 0.0)],
        [(2.0, 0.0), (3.0, 0.0)],
    ]

    band_builder.build_band.side_effect = [
        [("band1",)],
        [("band2",)],
    ]

    mesh_builder.build.return_value = [
        ("t1",),
        ("t2",),
    ]

    result = AtlasTerrainContourBuilder.build(
        top_points=[
            [(0.0, 0.0, 1.0)],
        ],
        base_z=0.8,
        contour_step_mm=0.4,
        band_half_width_mm=0.15,
    )

    mesh_builder.build.assert_called_once_with(
        contour_bands=[
            [("band1",)],
            [("band2",)],
        ]
    )

    assert result["triangles"] == [
        ("t1",),
        ("t2",),
    ]

