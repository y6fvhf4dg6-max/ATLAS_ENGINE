import pytest
from shapely.geometry import Polygon

from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)


def _coordinate_engine():
    return AtlasCoordinateEngine(
        origin_lat=0.0,
        origin_lon=0.0,
        xy_scale=1000.0,
        z_scale=5000.0,
    )


def _terrain_mesh():
    return {
        "metadata": {
            "base_z": 0.8,
            "min_height_m": 0.0,
            "z_scale": 5000.0,
        }
    }


def _water_polygon():
    return Polygon(
        (
            (0.00010, 0.00010),
            (0.00030, 0.00010),
            (0.00030, 0.00030),
            (0.00010, 0.00030),
        )
    )


def test_water_surface_remains_flat_when_texture_is_disabled():
    meshes = AtlasWaterFoundationBuilder.build_coastline_water_meshes(
        water_polygons=[_water_polygon()],
        coordinate_engine=_coordinate_engine(),
        terrain_mesh=_terrain_mesh(),
        surface_texture_amplitude_mm=None,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    top_z_values = {
        round(point[2], 9)
        for point in mesh["top"]
    }

    assert top_z_values == {0.9}
    assert mesh["surface_texture_enabled"] is False


def test_water_surface_uses_multiple_heights_when_texture_is_enabled():
    meshes = AtlasWaterFoundationBuilder.build_coastline_water_meshes(
        water_polygons=[_water_polygon()],
        coordinate_engine=_coordinate_engine(),
        terrain_mesh=_terrain_mesh(),
        surface_texture_amplitude_mm=0.12,
        surface_texture_wavelength_x_mm=7.0,
        surface_texture_wavelength_y_mm=11.0,
        surface_texture_edge_fade_mm=1.5,
        surface_texture_maximum_edge_length_mm=8.0,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    top_z_values = {
        round(point[2], 6)
        for point in mesh["top"]
    }

    assert mesh["surface_texture_enabled"] is True
    assert len(top_z_values) > 2
    assert min(top_z_values) >= (
        0.9 - 0.12 - 1e-6
    )
    assert max(top_z_values) <= (
        0.9 + 0.12 + 1e-6
    )


def test_textured_water_preserves_flat_bottom_and_closed_walls():
    meshes = AtlasWaterFoundationBuilder.build_coastline_water_meshes(
        water_polygons=[_water_polygon()],
        coordinate_engine=_coordinate_engine(),
        terrain_mesh=_terrain_mesh(),
        surface_texture_amplitude_mm=0.12,
        surface_texture_wavelength_x_mm=7.0,
        surface_texture_wavelength_y_mm=11.0,
        surface_texture_edge_fade_mm=1.5,
        surface_texture_maximum_edge_length_mm=8.0,
    )

    mesh = meshes[0]

    assert {
        round(point[2], 9)
        for point in mesh["bottom"]
    } == {0.8}

    assert len(mesh["walls"]) > 0
    assert len(mesh["triangles"]) > 0
