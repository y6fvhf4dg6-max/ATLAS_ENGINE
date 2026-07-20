import pytest

from CORE.atlas_parametric_face_surface_validity_result import (
    AtlasParametricFaceSurfaceValidityResult,
)


def _result(
    **overrides,
) -> AtlasParametricFaceSurfaceValidityResult:
    values = {
        "row_count": 41,
        "column_count": 51,
        "cell_count": 2000,
        "folded_cell_count": 0,
        "degenerate_cell_count": 0,
        "inverted_normal_count": 0,
        "minimum_signed_cell_area": 0.001,
        "minimum_normal_z": 0.65,
        "minimum_horizontal_edge_length": 0.04,
        "minimum_vertical_edge_length": 0.05,
        "area_tolerance": 1e-12,
        "normal_z_tolerance": 0.0,
        "edge_length_tolerance": 1e-12,
    }

    values.update(
        overrides,
    )

    return AtlasParametricFaceSurfaceValidityResult(
        **values,
    )


def test_result_preserves_integer_counts():
    result = _result()

    assert result.row_count == 41
    assert result.column_count == 51
    assert result.cell_count == 2000
    assert result.folded_cell_count == 0
    assert result.degenerate_cell_count == 0
    assert result.inverted_normal_count == 0


def test_result_normalizes_numeric_values_to_float():
    result = AtlasParametricFaceSurfaceValidityResult(
        row_count=3,
        column_count=4,
        cell_count=6,
        folded_cell_count=1,
        degenerate_cell_count=2,
        inverted_normal_count=3,
        minimum_signed_cell_area=1,
        minimum_normal_z=0,
        minimum_horizontal_edge_length=2,
        minimum_vertical_edge_length=3,
        area_tolerance=0,
        normal_z_tolerance=0,
        edge_length_tolerance=0,
    )

    assert isinstance(
        result.minimum_signed_cell_area,
        float,
    )
    assert isinstance(
        result.minimum_normal_z,
        float,
    )
    assert isinstance(
        result.minimum_horizontal_edge_length,
        float,
    )
    assert isinstance(
        result.minimum_vertical_edge_length,
        float,
    )


def test_result_reports_folded_cell_ratio():
    result = _result(
        row_count=11,
        column_count=21,
        cell_count=200,
        folded_cell_count=10,
    )

    assert result.folded_cell_ratio == pytest.approx(
        0.05,
    )


def test_result_reports_degenerate_cell_ratio():
    result = _result(
        row_count=11,
        column_count=21,
        cell_count=200,
        degenerate_cell_count=4,
    )

    assert result.degenerate_cell_ratio == pytest.approx(
        0.02,
    )


def test_result_reports_inverted_normal_ratio():
    result = _result(
        row_count=10,
        column_count=20,
        cell_count=171,
        inverted_normal_count=10,
    )

    assert result.point_count == 200

    assert result.inverted_normal_ratio == pytest.approx(
        0.05,
    )


def test_valid_surface_is_safe():
    result = _result()

    assert result.is_safe
    assert not result.has_foldover
    assert not result.has_degenerate_cells
    assert not result.has_inverted_normals


def test_folded_surface_is_not_safe():
    result = _result(
        folded_cell_count=1,
        minimum_signed_cell_area=-0.001,
    )

    assert result.has_foldover
    assert not result.is_safe


def test_degenerate_surface_is_not_safe():
    result = _result(
        degenerate_cell_count=1,
        minimum_signed_cell_area=0.0,
    )

    assert result.has_degenerate_cells
    assert not result.is_safe


def test_inverted_normals_make_surface_not_safe():
    result = _result(
        inverted_normal_count=1,
        minimum_normal_z=-0.10,
    )

    assert result.has_inverted_normals
    assert not result.is_safe


def test_collapsed_horizontal_edge_makes_surface_not_safe():
    result = _result(
        minimum_horizontal_edge_length=0.0,
    )

    assert result.has_collapsed_edges
    assert not result.is_safe


def test_collapsed_vertical_edge_makes_surface_not_safe():
    result = _result(
        minimum_vertical_edge_length=1e-13,
        edge_length_tolerance=1e-12,
    )

    assert result.has_collapsed_edges
    assert not result.is_safe


def test_edges_above_tolerance_are_not_collapsed():
    result = _result(
        minimum_horizontal_edge_length=2e-12,
        minimum_vertical_edge_length=3e-12,
        edge_length_tolerance=1e-12,
    )

    assert not result.has_collapsed_edges
    assert result.is_safe


@pytest.mark.parametrize(
    "field_name",
    [
        "row_count",
        "column_count",
        "cell_count",
        "folded_cell_count",
        "degenerate_cell_count",
        "inverted_normal_count",
    ],
)
def test_result_rejects_boolean_integer_fields(
    field_name,
):
    values = {
        "row_count": 41,
        "column_count": 51,
        "cell_count": 2000,
        "folded_cell_count": 0,
        "degenerate_cell_count": 0,
        "inverted_normal_count": 0,
    }

    values[field_name] = True

    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        _result(
            **values,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "row_count",
        "column_count",
    ],
)
def test_result_requires_at_least_two_grid_points(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _result(
            **{
                field_name: 1,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "cell_count",
        "folded_cell_count",
        "degenerate_cell_count",
        "inverted_normal_count",
    ],
)
def test_result_rejects_negative_counts(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _result(
            **{
                field_name: -1,
            }
        )


def test_result_rejects_inconsistent_cell_count():
    with pytest.raises(
        ValueError,
        match="cell_count",
    ):
        _result(
            row_count=5,
            column_count=7,
            cell_count=999,
        )


def test_result_rejects_folded_count_above_cell_count():
    with pytest.raises(
        ValueError,
        match="folded_cell_count",
    ):
        _result(
            cell_count=2000,
            folded_cell_count=2001,
        )


def test_result_rejects_degenerate_count_above_cell_count():
    with pytest.raises(
        ValueError,
        match="degenerate_cell_count",
    ):
        _result(
            cell_count=2000,
            degenerate_cell_count=2001,
        )


def test_result_rejects_inverted_count_above_point_count():
    with pytest.raises(
        ValueError,
        match="inverted_normal_count",
    ):
        _result(
            row_count=4,
            column_count=5,
            cell_count=12,
            inverted_normal_count=21,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "minimum_signed_cell_area",
        "minimum_normal_z",
        "minimum_horizontal_edge_length",
        "minimum_vertical_edge_length",
        "area_tolerance",
        "normal_z_tolerance",
        "edge_length_tolerance",
    ],
)
def test_result_rejects_non_finite_numeric_fields(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _result(
            **{
                field_name: float("nan"),
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "minimum_horizontal_edge_length",
        "minimum_vertical_edge_length",
        "area_tolerance",
        "edge_length_tolerance",
    ],
)
def test_result_rejects_negative_nonnegative_fields(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _result(
            **{
                field_name: -0.001,
            }
        )
