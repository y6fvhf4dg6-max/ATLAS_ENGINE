import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


def test_builder_returns_parametric_face_surface():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=9,
            column_count=11,
        )
    )

    assert isinstance(
        surface,
        AtlasParametricFaceSurface,
    )


def test_builder_uses_requested_grid_dimensions():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=9,
            column_count=11,
        )
    )

    assert surface.shape == (9, 11)
    assert surface.row_count == 9
    assert surface.column_count == 11


def test_builder_spans_normalized_xy_coordinates():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=9,
            column_count=11,
        )
    )

    assert surface.x_coordinates.min() == pytest.approx(
        -1.0,
    )
    assert surface.x_coordinates.max() == pytest.approx(
        1.0,
    )
    assert surface.y_coordinates.min() == pytest.approx(
        -1.0,
    )
    assert surface.y_coordinates.max() == pytest.approx(
        1.0,
    )


def test_builder_coordinate_rows_and_columns_are_regular():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=7,
            column_count=9,
        )
    )

    for row in surface.x_coordinates:
        assert row == pytest.approx(
            surface.x_coordinates[0],
        )

    for column_index in range(
        surface.column_count
    ):
        assert surface.y_coordinates[
            :,
            column_index,
        ] == pytest.approx(
            surface.y_coordinates[:, 0],
        )


def test_neutral_surface_is_horizontally_symmetric():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=17,
            column_count=21,
        )
    )

    assert surface.z_coordinates == pytest.approx(
        np.fliplr(
            surface.z_coordinates,
        )
    )


def test_nose_center_is_in_front_of_face_edges():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=21,
            column_count=21,
        )
    )

    center_row = surface.row_count // 2
    center_column = surface.column_count // 2

    nose_center_z = surface.z_coordinates[
        center_row,
        center_column,
    ]

    left_edge_z = surface.z_coordinates[
        center_row,
        0,
    ]
    right_edge_z = surface.z_coordinates[
        center_row,
        -1,
    ]

    assert nose_center_z > left_edge_z
    assert nose_center_z > right_edge_z


def test_center_column_contains_surface_maximum():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=21,
            column_count=21,
        )
    )

    maximum_column = np.unravel_index(
        np.argmax(
            surface.z_coordinates,
        ),
        surface.shape,
    )[1]

    assert maximum_column == (
        surface.column_count // 2
    )


def test_surface_depth_is_nonnegative_and_nonflat():
    surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=17,
            column_count=19,
        )
    )

    assert surface.minimum_z >= 0.0
    assert surface.maximum_z > surface.minimum_z


def test_builder_is_deterministic():
    first = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=13,
            column_count=15,
        )
    )
    second = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=13,
            column_count=15,
        )
    )

    assert first.x_coordinates == pytest.approx(
        second.x_coordinates,
    )
    assert first.y_coordinates == pytest.approx(
        second.y_coordinates,
    )
    assert first.z_coordinates == pytest.approx(
        second.z_coordinates,
    )

    assert first is not second


@pytest.mark.parametrize(
    "field_name",
    [
        "row_count",
        "column_count",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        1,
        0,
        -1,
    ],
)
def test_builder_requires_at_least_two_rows_and_columns(
    field_name,
    invalid_value,
):
    values = {
        "row_count": 9,
        "column_count": 11,
    }
    values[field_name] = invalid_value

    with pytest.raises(
        ValueError,
        match="at least 2",
    ):
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            **values,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "row_count",
        "column_count",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        3.5,
        "9",
        True,
        None,
    ],
)
def test_builder_rejects_non_integer_grid_dimensions(
    field_name,
    invalid_value,
):
    values = {
        "row_count": 9,
        "column_count": 11,
    }
    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match="integer",
    ):
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            **values,
        )
