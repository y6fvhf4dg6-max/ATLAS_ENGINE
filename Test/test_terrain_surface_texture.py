import math

import pytest

from CORE.atlas_terrain_surface_texture import (
    AtlasTerrainSurfaceTexture,
)


def test_surface_texture_is_zero_at_product_edges():
    texture = AtlasTerrainSurfaceTexture(
        size_x_mm=150.0,
        size_y_mm=150.0,
        amplitude_mm=0.16,
        wavelength_x_mm=28.0,
        wavelength_y_mm=37.0,
        edge_fade_mm=8.0,
    )

    edge_points = (
        (0.0, 75.0),
        (150.0, 75.0),
        (75.0, 0.0),
        (75.0, 150.0),
        (0.0, 0.0),
        (150.0, 150.0),
    )

    for x, y in edge_points:
        assert texture.offset_at(x, y) == pytest.approx(
            0.0,
            abs=1e-9,
        )


def test_surface_texture_stays_within_requested_amplitude():
    texture = AtlasTerrainSurfaceTexture(
        size_x_mm=150.0,
        size_y_mm=150.0,
        amplitude_mm=0.16,
        wavelength_x_mm=28.0,
        wavelength_y_mm=37.0,
        edge_fade_mm=8.0,
    )

    samples = [
        texture.offset_at(
            x=float(x),
            y=float(y),
        )
        for x in range(151)
        for y in range(151)
    ]

    tolerance = 1e-9

    assert max(samples) <= 0.16 + tolerance
    assert min(samples) >= -0.16 - tolerance


def test_surface_texture_varies_inside_product_area():
    texture = AtlasTerrainSurfaceTexture(
        size_x_mm=150.0,
        size_y_mm=150.0,
        amplitude_mm=0.16,
        wavelength_x_mm=28.0,
        wavelength_y_mm=37.0,
        edge_fade_mm=8.0,
    )

    offsets = {
        round(
            texture.offset_at(x, y),
            6,
        )
        for x, y in (
            (25.0, 25.0),
            (50.0, 40.0),
            (75.0, 75.0),
            (100.0, 90.0),
            (125.0, 120.0),
        )
    }

    assert len(offsets) > 1
    assert any(
        not math.isclose(
            value,
            0.0,
            abs_tol=1e-6,
        )
        for value in offsets
    )
