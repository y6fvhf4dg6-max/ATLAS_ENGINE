import numpy as np
import pytest

from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_validity_analyzer import (
    AtlasParametricFaceSurfaceValidityAnalyzer,
)
from CORE.atlas_parametric_face_surface_validity_result import (
    AtlasParametricFaceSurfaceValidityResult,
)


def _surface(
    x_coordinates,
    y_coordinates,
    z_coordinates=None,
) -> AtlasParametricFaceSurface:
    x_array = np.asarray(
        x_coordinates,
        dtype=np.float64,
    )
    y_array = np.asarray(
        y_coordinates,
        dtype=np.float64,
    )

    if z_coordinates is None:
        z_array = np.zeros_like(
            x_array,
            dtype=np.float64,
        )
    else:
        z_array = np.asarray(
            z_coordinates,
            dtype=np.float64,
        )

    return AtlasParametricFaceSurface(
        x_coordinates=x_array,
        y_coordinates=y_array,
        z_coordinates=z_array,
    )


def _regular_surface(
    *,
    row_count=3,
    column_count=4,
) -> AtlasParametricFaceSurface:
    x_values = np.linspace(
        -1.0,
        1.0,
        column_count,
        dtype=np.float64,
    )
    y_values = np.linspace(
        -1.0,
        1.0,
        row_count,
        dtype=np.float64,
    )

    x_coordinates, y_coordinates = np.meshgrid(
        x_values,
        y_values,
    )

    z_coordinates = (
        0.20
        * (
            1.0
            - 0.25 * x_coordinates**2
            - 0.25 * y_coordinates**2
        )
    )

    return _surface(
        x_coordinates,
        y_coordinates,
        z_coordinates,
    )


def test_analyzer_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="surface",
    ):
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            object(),
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "area_tolerance",
        "normal_z_tolerance",
        "edge_length_tolerance",
    ],
)
def test_analyzer_rejects_non_finite_tolerance(
    field_name,
):
    values = {
        "area_tolerance": 1e-12,
        "normal_z_tolerance": 0.0,
        "edge_length_tolerance": 1e-12,
    }

    values[field_name] = float("nan")

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            _regular_surface(),
            **values,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "area_tolerance",
        "edge_length_tolerance",
    ],
)
def test_analyzer_rejects_negative_nonnegative_tolerance(
    field_name,
):
    values = {
        "area_tolerance": 1e-12,
        "normal_z_tolerance": 0.0,
        "edge_length_tolerance": 1e-12,
    }

    values[field_name] = -1e-6

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            _regular_surface(),
            **values,
        )


def test_analyzer_returns_validity_result():
    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            _regular_surface(),
        )
    )

    assert isinstance(
        result,
        AtlasParametricFaceSurfaceValidityResult,
    )


def test_regular_surface_is_safe():
    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            _regular_surface(
                row_count=5,
                column_count=7,
            ),
        )
    )

    assert result.row_count == 5
    assert result.column_count == 7
    assert result.point_count == 35
    assert result.cell_count == 24

    assert result.folded_cell_count == 0
    assert result.degenerate_cell_count == 0
    assert result.inverted_normal_count == 0

    assert result.minimum_signed_cell_area > 0.0
    assert result.minimum_normal_z > 0.0
    assert result.minimum_horizontal_edge_length > 0.0
    assert result.minimum_vertical_edge_length > 0.0

    assert result.is_safe


def test_analyzer_preserves_requested_tolerances():
    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            _regular_surface(),
            area_tolerance=1e-8,
            normal_z_tolerance=-0.25,
            edge_length_tolerance=1e-7,
        )
    )

    assert result.area_tolerance == pytest.approx(
        1e-8,
    )
    assert result.normal_z_tolerance == pytest.approx(
        -0.25,
    )
    assert result.edge_length_tolerance == pytest.approx(
        1e-7,
    )


def test_analyzer_reports_expected_regular_grid_area():
    surface = _surface(
        x_coordinates=[
            [0.0, 2.0],
            [0.0, 2.0],
        ],
        y_coordinates=[
            [0.0, 0.0],
            [3.0, 3.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert result.cell_count == 1

    assert result.minimum_signed_cell_area == pytest.approx(
        6.0,
    )


def test_reversed_column_orientation_is_folded():
    surface = _surface(
        x_coordinates=[
            [1.0, 0.0],
            [1.0, 0.0],
        ],
        y_coordinates=[
            [0.0, 0.0],
            [1.0, 1.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert result.folded_cell_count == 1
    assert result.minimum_signed_cell_area < 0.0
    assert result.has_foldover
    assert not result.is_safe


def test_collapsed_cell_is_degenerate():
    surface = _surface(
        x_coordinates=[
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        y_coordinates=[
            [0.0, 0.0],
            [1.0, 1.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert result.degenerate_cell_count == 1
    assert result.minimum_signed_cell_area == pytest.approx(
        0.0,
    )
    assert result.has_degenerate_cells
    assert not result.is_safe


def test_partial_grid_foldover_is_counted_per_cell():
    surface = _surface(
        x_coordinates=[
            [0.0, 1.0, 2.0],
            [0.0, 1.0, 0.0],
        ],
        y_coordinates=[
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert result.cell_count == 2
    assert result.folded_cell_count == 1
    assert result.degenerate_cell_count == 0
    assert result.folded_cell_ratio == pytest.approx(
        0.5,
    )


def test_downward_surface_orientation_has_inverted_normals():
    surface = _surface(
        x_coordinates=[
            [0.0, 1.0],
            [0.0, 1.0],
        ],
        y_coordinates=[
            [1.0, 1.0],
            [0.0, 0.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert result.inverted_normal_count == 4
    assert result.minimum_normal_z < 0.0
    assert result.has_inverted_normals
    assert not result.is_safe


def test_vertical_surface_has_zero_normal_z():
    surface = _surface(
        x_coordinates=[
            [0.0, 1.0],
            [0.0, 1.0],
        ],
        y_coordinates=[
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        z_coordinates=[
            [0.0, 0.0],
            [1.0, 1.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert result.minimum_normal_z == pytest.approx(
        0.0,
    )
    assert result.inverted_normal_count == 0


def test_positive_normal_tolerance_can_classify_near_vertical_normals():
    surface = _surface(
        x_coordinates=[
            [0.0, 1.0],
            [0.0, 1.0],
        ],
        y_coordinates=[
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        z_coordinates=[
            [0.0, 0.0],
            [1.0, 1.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
            normal_z_tolerance=0.01,
        )
    )

    assert result.inverted_normal_count == 4
    assert result.has_inverted_normals


def test_minimum_horizontal_edge_length_is_reported():
    surface = _surface(
        x_coordinates=[
            [0.0, 0.25, 2.0],
            [0.0, 0.25, 2.0],
        ],
        y_coordinates=[
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert (
        result.minimum_horizontal_edge_length
        == pytest.approx(
            0.25,
        )
    )


def test_minimum_vertical_edge_length_is_reported():
    surface = _surface(
        x_coordinates=[
            [0.0, 1.0],
            [0.0, 1.0],
            [0.0, 1.0],
        ],
        y_coordinates=[
            [0.0, 0.0],
            [0.20, 0.20],
            [2.0, 2.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert (
        result.minimum_vertical_edge_length
        == pytest.approx(
            0.20,
        )
    )


def test_zero_horizontal_edge_makes_surface_unsafe():
    surface = _surface(
        x_coordinates=[
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        y_coordinates=[
            [0.0, 0.0],
            [1.0, 1.0],
        ],
    )

    result = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
            edge_length_tolerance=1e-12,
        )
    )

    assert (
        result.minimum_horizontal_edge_length
        == pytest.approx(
            0.0,
        )
    )
    assert not result.is_safe
