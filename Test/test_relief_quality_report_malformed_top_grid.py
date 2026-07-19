import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _relief():
    return AtlasReliefMeshBuilder.build(
        [
            [0.0, 0.5],
            [1.0, 0.25],
        ],
        width_mm=8.0,
        depth_mm=6.0,
        relief_height_mm=2.0,
    )


@pytest.mark.parametrize(
    "point",
    [
        None,
        1.0,
        (),
        (0.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    ],
)
def test_rejects_invalid_top_grid_point_shape(
    point,
):
    relief = _relief()
    relief["top_grid"][0][0] = point

    with pytest.raises(
        ValueError,
        match=(
            "Relief top_grid contains "
            "an invalid point"
        ),
    ):
        AtlasReliefQualityReport.build(
            relief
        )


@pytest.mark.parametrize(
    "point",
    [
        (float("nan"), 0.0, 0.0),
        (0.0, float("inf"), 0.0),
        (0.0, 0.0, float("-inf")),
    ],
)
def test_rejects_non_finite_top_grid_coordinates(
    point,
):
    relief = _relief()
    relief["top_grid"][0][0] = point

    with pytest.raises(
        ValueError,
        match=(
            "Relief top_grid contains "
            "non-finite coordinates"
        ),
    ):
        AtlasReliefQualityReport.build(
            relief
        )


@pytest.mark.parametrize(
    "point",
    [
        ("invalid", 0.0, 0.0),
        (0.0, object(), 0.0),
        (0.0, 0.0, None),
    ],
)
def test_rejects_non_numeric_top_grid_coordinates(
    point,
):
    relief = _relief()
    relief["top_grid"][0][0] = point

    with pytest.raises(
        ValueError,
        match=(
            "Relief top_grid contains "
            "invalid coordinates"
        ),
    ):
        AtlasReliefQualityReport.build(
            relief
        )


def test_valid_top_grid_still_produces_surface_metrics():
    report = AtlasReliefQualityReport.build(
        _relief()
    )

    assert report[
        "surface_analysis_available"
    ] is True
    assert report["surface_edge_count"] == 5
    assert report[
        "maximum_slope_degrees"
    ] >= 0.0
