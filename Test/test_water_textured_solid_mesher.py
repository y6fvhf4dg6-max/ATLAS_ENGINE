from collections import Counter

import pytest

from CORE.atlas_water_surface_texture import (
    AtlasWaterSurfaceTexture,
)
from CORE.atlas_water_textured_solid_mesher import (
    AtlasWaterTexturedSolidMesher,
)


def _edge_key(first, second):
    def point_key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    return tuple(
        sorted(
            (
                point_key(first),
                point_key(second),
            )
        )
    )


def _topology_counts(triangles):
    counts = Counter()

    for first, second, third in triangles:
        counts[_edge_key(first, second)] += 1
        counts[_edge_key(second, third)] += 1
        counts[_edge_key(third, first)] += 1

    return {
        "open_edges": sum(
            count == 1
            for count in counts.values()
        ),
        "non_manifold_edges": sum(
            count > 2
            for count in counts.values()
        ),
    }


def _texture():
    return AtlasWaterSurfaceTexture(
        amplitude_mm=0.12,
        wavelength_x_mm=7.0,
        wavelength_y_mm=11.0,
        edge_fade_mm=1.5,
    )


def _build():
    return AtlasWaterTexturedSolidMesher.build(
        boundary_points=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 14.0),
            (0.0, 14.0),
        ),
        water_bottom_z=0.8,
        water_surface_z=0.9,
        texture=_texture(),
        maximum_edge_length_mm=2.5,
    )


def test_textured_water_adds_interior_surface_vertices():
    result = _build()

    assert len(result["top"]) > 4
    assert result["surface_texture_enabled"] is True
    assert result["surface_vertex_count"] == len(
        result["top"]
    )


def test_textured_water_boundary_stays_at_nominal_surface_height():
    result = _build()

    boundary_z_values = {
        round(point[2], 9)
        for point in result["boundary_top"]
    }

    assert boundary_z_values == {0.9}


def test_textured_water_interior_contains_multiple_wave_heights():
    result = _build()

    interior_z_values = {
        round(point[2], 6)
        for point in result["interior_top"]
    }

    assert len(interior_z_values) > 2
    assert min(interior_z_values) >= (
        0.9 - 0.12 - 1e-6
    )
    assert max(interior_z_values) <= (
        0.9 + 0.12 + 1e-6
    )


def test_textured_water_preserves_flat_bottom():
    result = _build()

    assert {
        round(point[2], 9)
        for point in result["bottom"]
    } == {0.8}


def test_textured_water_solid_is_closed_and_manifold():
    result = _build()

    topology = _topology_counts(
        result["triangles"]
    )

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0


@pytest.mark.parametrize(
    "maximum_edge_length_mm",
    (0.0, -1.0),
)
def test_textured_water_rejects_invalid_mesh_resolution(
    maximum_edge_length_mm,
):
    with pytest.raises(
        ValueError,
        match="maximum_edge_length_mm",
    ):
        AtlasWaterTexturedSolidMesher.build(
            boundary_points=(
                (0.0, 0.0),
                (10.0, 0.0),
                (10.0, 10.0),
                (0.0, 10.0),
            ),
            water_bottom_z=0.8,
            water_surface_z=0.9,
            texture=_texture(),
            maximum_edge_length_mm=(
                maximum_edge_length_mm
            ),
        )
