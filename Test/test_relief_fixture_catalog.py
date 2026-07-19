import numpy as np
import pytest

from fixtures.relief.relief_fixture_catalog import (
    EXPECTED_FIXTURE_SHAPES,
    fixture_names,
    load_fixture,
)

EXPECTED_NAMES = (
    "asymmetric_surface_3x4",
    "checkerboard_4x4",
    "flat_3x3",
    "horizontal_ramp_3x3",
    "impulse_7x7",
    "small_reflect_2x3",
    "vertical_ramp_3x3",
)


def test_fixture_names_are_complete_and_deterministic():
    assert fixture_names() == EXPECTED_NAMES


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_fixture_shape_matches_registry(name):
    values = load_fixture(name)

    assert values.shape == EXPECTED_FIXTURE_SHAPES[name]


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_fixture_dtype_is_float64(name):
    values = load_fixture(name)

    assert values.dtype == np.float64


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_fixture_values_are_finite(name):
    values = load_fixture(name)

    assert np.isfinite(values).all()


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_fixture_values_are_normalized(name):
    values = load_fixture(name)

    assert float(values.min()) >= 0.0
    assert float(values.max()) <= 1.0


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_load_fixture_returns_independent_arrays(name):
    first = load_fixture(name)
    second = load_fixture(name)

    assert first is not second
    assert np.array_equal(first, second)

    first.flat[0] = 123.0

    assert not np.array_equal(first, second)
    assert np.array_equal(
        second,
        load_fixture(name),
    )


def test_unknown_fixture_name_is_rejected():
    with pytest.raises(
        KeyError,
        match="Unknown relief fixture",
    ):
        load_fixture("missing_fixture")
