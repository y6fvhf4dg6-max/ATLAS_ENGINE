import numpy as np
import pytest
from dataclasses import FrozenInstanceError

from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


def _coordinates():
    x_coordinates = np.array(
        [
            [-1.0, 0.0, 1.0],
            [-1.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    y_coordinates = np.array(
        [
            [-0.5, -0.5, -0.5],
            [0.5, 0.5, 0.5],
        ],
        dtype=np.float64,
    )

    z_coordinates = np.array(
        [
            [0.0, 0.4, 0.0],
            [0.1, 0.8, 0.1],
        ],
        dtype=np.float64,
    )

    return (
        x_coordinates,
        y_coordinates,
        z_coordinates,
    )


def _surface():
    (
        x_coordinates,
        y_coordinates,
        z_coordinates,
    ) = _coordinates()

    return AtlasParametricFaceSurface(
        x_coordinates=x_coordinates,
        y_coordinates=y_coordinates,
        z_coordinates=z_coordinates,
    )


def test_surface_stores_float64_coordinate_grids():
    surface = AtlasParametricFaceSurface(
        x_coordinates=[
            [-1, 0, 1],
            [-1, 0, 1],
        ],
        y_coordinates=[
            [-0.5, -0.5, -0.5],
            [0.5, 0.5, 0.5],
        ],
        z_coordinates=[
            [0, 0.4, 0],
            [0.1, 0.8, 0.1],
        ],
    )

    assert surface.x_coordinates.dtype == np.float64
    assert surface.y_coordinates.dtype == np.float64
    assert surface.z_coordinates.dtype == np.float64


def test_surface_reports_grid_dimensions():
    surface = _surface()

    assert surface.shape == (2, 3)
    assert surface.row_count == 2
    assert surface.column_count == 3


def test_surface_reports_z_range():
    surface = _surface()

    assert surface.minimum_z == pytest.approx(
        0.0,
    )
    assert surface.maximum_z == pytest.approx(
        0.8,
    )


def test_surface_copies_source_coordinate_arrays():
    (
        x_coordinates,
        y_coordinates,
        z_coordinates,
    ) = _coordinates()

    surface = AtlasParametricFaceSurface(
        x_coordinates=x_coordinates,
        y_coordinates=y_coordinates,
        z_coordinates=z_coordinates,
    )

    x_coordinates[0, 0] = 99.0
    y_coordinates[0, 0] = 99.0
    z_coordinates[0, 0] = 99.0

    assert surface.x_coordinates[0, 0] == pytest.approx(
        -1.0,
    )
    assert surface.y_coordinates[0, 0] == pytest.approx(
        -0.5,
    )
    assert surface.z_coordinates[0, 0] == pytest.approx(
        0.0,
    )


def test_surface_coordinate_arrays_are_read_only():
    surface = _surface()

    assert not surface.x_coordinates.flags.writeable
    assert not surface.y_coordinates.flags.writeable
    assert not surface.z_coordinates.flags.writeable

    with pytest.raises(
        ValueError,
    ):
        surface.z_coordinates[0, 0] = 2.0


def test_surface_dataclass_fields_are_frozen():
    surface = _surface()

    with pytest.raises(
        FrozenInstanceError,
    ):
        surface.z_coordinates = np.zeros(
            (2, 3),
            dtype=np.float64,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "x_coordinates",
        "y_coordinates",
        "z_coordinates",
    ],
)
def test_surface_rejects_non_two_dimensional_coordinates(
    field_name,
):
    (
        x_coordinates,
        y_coordinates,
        z_coordinates,
    ) = _coordinates()

    values = {
        "x_coordinates": x_coordinates,
        "y_coordinates": y_coordinates,
        "z_coordinates": z_coordinates,
    }

    values[field_name] = np.zeros(
        6,
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="two-dimensional",
    ):
        AtlasParametricFaceSurface(
            **values,
        )


def test_surface_rejects_coordinate_shape_mismatch():
    (
        x_coordinates,
        y_coordinates,
        z_coordinates,
    ) = _coordinates()

    with pytest.raises(
        ValueError,
        match="identical shapes",
    ):
        AtlasParametricFaceSurface(
            x_coordinates=x_coordinates,
            y_coordinates=y_coordinates,
            z_coordinates=z_coordinates[
                :,
                :2,
            ],
        )


@pytest.mark.parametrize(
    "shape",
    [
        (1, 3),
        (3, 1),
        (1, 1),
    ],
)
def test_surface_requires_at_least_two_rows_and_columns(
    shape,
):
    values = np.zeros(
        shape,
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="at least two rows and two columns",
    ):
        AtlasParametricFaceSurface(
            x_coordinates=values,
            y_coordinates=values,
            z_coordinates=values,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "x_coordinates",
        "y_coordinates",
        "z_coordinates",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_surface_rejects_non_finite_coordinates(
    field_name,
    invalid_value,
):
    (
        x_coordinates,
        y_coordinates,
        z_coordinates,
    ) = _coordinates()

    values = {
        "x_coordinates": x_coordinates,
        "y_coordinates": y_coordinates,
        "z_coordinates": z_coordinates,
    }

    invalid = values[field_name].copy()
    invalid[0, 0] = invalid_value
    values[field_name] = invalid

    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        AtlasParametricFaceSurface(
            **values,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "x_coordinates",
        "y_coordinates",
        "z_coordinates",
    ],
)
def test_surface_rejects_non_numeric_coordinates(
    field_name,
):
    (
        x_coordinates,
        y_coordinates,
        z_coordinates,
    ) = _coordinates()

    values = {
        "x_coordinates": x_coordinates,
        "y_coordinates": y_coordinates,
        "z_coordinates": z_coordinates,
    }

    values[field_name] = [
        ["invalid", 0.0],
        [0.0, 0.0],
    ]

    with pytest.raises(
        ValueError,
        match="numeric",
    ):
        AtlasParametricFaceSurface(
            **values,
        )
