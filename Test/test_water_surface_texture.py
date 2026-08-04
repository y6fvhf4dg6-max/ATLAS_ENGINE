import pytest

from CORE.atlas_water_surface_texture import (
    AtlasWaterSurfaceTexture,
)


def test_water_surface_texture_is_disabled_without_amplitude():
    texture = AtlasWaterSurfaceTexture(
        amplitude_mm=None,
        wavelength_x_mm=7.0,
        wavelength_y_mm=11.0,
        edge_fade_mm=1.5,
    )

    assert texture.enabled is False
    assert texture.offset_at(
        x_mm=3.0,
        y_mm=5.0,
        edge_distance_mm=10.0,
    ) == pytest.approx(0.0)


def test_water_surface_texture_produces_low_amplitude_wave():
    texture = AtlasWaterSurfaceTexture(
        amplitude_mm=0.12,
        wavelength_x_mm=7.0,
        wavelength_y_mm=11.0,
        edge_fade_mm=1.5,
    )

    offsets = [
        texture.offset_at(
            x_mm=x_mm,
            y_mm=y_mm,
            edge_distance_mm=10.0,
        )
        for x_mm, y_mm in (
            (1.0, 2.0),
            (2.5, 4.0),
            (5.0, 7.0),
            (8.0, 9.0),
        )
    ]

    assert texture.enabled is True
    assert len(set(round(value, 8) for value in offsets)) > 1
    assert max(
        abs(value)
        for value in offsets
    ) <= 0.12 + 1e-9


def test_water_surface_texture_fades_to_zero_at_boundary():
    texture = AtlasWaterSurfaceTexture(
        amplitude_mm=0.12,
        wavelength_x_mm=7.0,
        wavelength_y_mm=11.0,
        edge_fade_mm=1.5,
    )

    assert texture.offset_at(
        x_mm=2.0,
        y_mm=3.0,
        edge_distance_mm=0.0,
    ) == pytest.approx(0.0)

    near_edge = texture.offset_at(
        x_mm=2.0,
        y_mm=3.0,
        edge_distance_mm=0.75,
    )
    interior = texture.offset_at(
        x_mm=2.0,
        y_mm=3.0,
        edge_distance_mm=3.0,
    )

    assert abs(near_edge) < abs(interior)


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "amplitude_mm",
            {
                "amplitude_mm": -0.01,
                "wavelength_x_mm": 7.0,
                "wavelength_y_mm": 11.0,
                "edge_fade_mm": 1.5,
            },
        ),
        (
            "wavelength_x_mm",
            {
                "amplitude_mm": 0.12,
                "wavelength_x_mm": 0.0,
                "wavelength_y_mm": 11.0,
                "edge_fade_mm": 1.5,
            },
        ),
        (
            "wavelength_y_mm",
            {
                "amplitude_mm": 0.12,
                "wavelength_x_mm": 7.0,
                "wavelength_y_mm": -1.0,
                "edge_fade_mm": 1.5,
            },
        ),
        (
            "edge_fade_mm",
            {
                "amplitude_mm": 0.12,
                "wavelength_x_mm": 7.0,
                "wavelength_y_mm": 11.0,
                "edge_fade_mm": -0.1,
            },
        ),
    ),
)
def test_water_surface_texture_rejects_invalid_parameters(
    field_name,
    kwargs,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasWaterSurfaceTexture(**kwargs)


def test_water_surface_texture_never_moves_below_nominal_surface():
    texture = AtlasWaterSurfaceTexture(
        amplitude_mm=0.10,
        wavelength_x_mm=9.0,
        wavelength_y_mm=13.0,
        edge_fade_mm=1.5,
    )

    offsets = [
        texture.offset_at(
            x_mm=x_mm,
            y_mm=y_mm,
            edge_distance_mm=10.0,
        )
        for x_mm in range(0, 30)
        for y_mm in range(0, 30)
    ]

    assert min(offsets) >= 0.0
    assert max(offsets) <= 0.10 + 1e-9
    assert max(offsets) > 0.07
