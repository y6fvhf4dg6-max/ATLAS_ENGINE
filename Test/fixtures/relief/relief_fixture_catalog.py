from __future__ import annotations

from typing import Callable

import numpy as np

FixtureFactory = Callable[[], np.ndarray]


def flat_3x3() -> np.ndarray:
    """
    Returns a constant normalized height map.

    Intended uses:
    - flat-surface regression
    - zero-slope quality checks
    - constant-map preservation
    """

    return np.full(
        (3, 3),
        0.5,
        dtype=np.float64,
    )


def horizontal_ramp_3x3() -> np.ndarray:
    """
    Returns a normalized horizontal ramp.

    Intended uses:
    - predictable X-axis slope
    - bilinear resampling
    - physical Z mapping
    """

    return np.array(
        [
            [0.0, 0.5, 1.0],
            [0.0, 0.5, 1.0],
            [0.0, 0.5, 1.0],
        ],
        dtype=np.float64,
    )


def vertical_ramp_3x3() -> np.ndarray:
    """
    Returns a normalized vertical ramp.

    Intended uses:
    - predictable Y-axis slope
    - axis-orientation regression
    - physical Z mapping
    """

    return np.array(
        [
            [0.0, 0.0, 0.0],
            [0.5, 0.5, 0.5],
            [1.0, 1.0, 1.0],
        ],
        dtype=np.float64,
    )


def asymmetric_surface_3x4() -> np.ndarray:
    """
    Returns a non-symmetric normalized surface.

    Intended uses:
    - inversion regression
    - deterministic pipeline output
    - accidental transpose detection
    - axis-order detection
    """

    return np.array(
        [
            [0.00, 0.20, 0.70, 1.00],
            [0.10, 0.55, 0.35, 0.80],
            [0.90, 0.40, 0.15, 0.60],
        ],
        dtype=np.float64,
    )


def impulse_7x7() -> np.ndarray:
    """
    Returns a centered unit impulse.

    Intended uses:
    - Gaussian smoothing
    - symmetry regression
    - impulse-mass checks
    """

    values = np.zeros(
        (7, 7),
        dtype=np.float64,
    )
    values[3, 3] = 1.0

    return values


def checkerboard_4x4() -> np.ndarray:
    """
    Returns a high-frequency normalized checkerboard.

    Intended uses:
    - smoothing behavior
    - resampling behavior
    - detail-loss regression
    """

    return np.array(
        [
            [0.0, 1.0, 0.0, 1.0],
            [1.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0, 1.0],
            [1.0, 0.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )


def small_reflect_2x3() -> np.ndarray:
    """
    Returns a small normalized map for reflected-padding tests.

    Intended uses:
    - two-row Gaussian boundary behavior
    - large-radius smoothing on a small grid
    """

    return np.array(
        [
            [0.0, 0.5, 1.0],
            [1.0, 0.25, 0.0],
        ],
        dtype=np.float64,
    )


_FIXTURE_FACTORIES: dict[str, FixtureFactory] = {
    "asymmetric_surface_3x4": asymmetric_surface_3x4,
    "checkerboard_4x4": checkerboard_4x4,
    "flat_3x3": flat_3x3,
    "horizontal_ramp_3x3": horizontal_ramp_3x3,
    "impulse_7x7": impulse_7x7,
    "small_reflect_2x3": small_reflect_2x3,
    "vertical_ramp_3x3": vertical_ramp_3x3,
}


EXPECTED_FIXTURE_SHAPES: dict[str, tuple[int, int]] = {
    name: factory().shape for name, factory in _FIXTURE_FACTORIES.items()
}


def fixture_names() -> tuple[str, ...]:
    """
    Returns all registered fixture names in deterministic order.
    """

    return tuple(sorted(_FIXTURE_FACTORIES))


def load_fixture(name: str) -> np.ndarray:
    """
    Returns a new independent float64 array for a named fixture.
    """

    try:
        factory = _FIXTURE_FACTORIES[name]
    except KeyError as error:
        available = ", ".join(fixture_names())

        raise KeyError(
            f"Unknown relief fixture: {name}. " f"Available fixtures: {available}"
        ) from error

    return factory().copy()
