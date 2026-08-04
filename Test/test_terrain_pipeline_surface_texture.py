import copy

import pytest

from CORE.atlas_terrain_mesh_generator import (
    AtlasTerrainMeshGenerator,
)
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline


def _closed_flat_mesh():
    grid_size = 3
    size_x_mm = 20.0
    size_y_mm = 20.0

    top_points = [
        [
            (
                size_x_mm * column / (grid_size - 1),
                size_y_mm * row / (grid_size - 1),
                1.0,
            )
            for column in range(grid_size)
        ]
        for row in range(grid_size)
    ]

    bottom_points = (
        AtlasTerrainMeshGenerator.build_bottom_points(
            size_mm=20.0,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            grid_size=grid_size,
            bottom_z=0.0,
        )
    )

    triangles = [
        *AtlasTerrainMeshGenerator.build_surface_triangles(
            points=top_points,
            grid_size=grid_size,
        ),
        *AtlasTerrainMeshGenerator.build_bottom_triangles(
            bottom_points=bottom_points,
            grid_size=grid_size,
        ),
        *AtlasTerrainMeshGenerator.build_side_wall_triangles(
            top_points=top_points,
            bottom_points=bottom_points,
            grid_size=grid_size,
        ),
    ]

    return {
        "type": "terrain_closed_slab",
        "triangles": triangles,
        "metadata": {
            "grid_size": grid_size,
            "size_mm": 20.0,
            "size_x_mm": size_x_mm,
            "size_y_mm": size_y_mm,
            "base_z": 1.0,
            "bottom_z": 0.0,
            "closed": True,
            "triangle_count": len(triangles),
        },
        "grid": {
            "heights": [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
        },
        "top_points": top_points,
        "bottom_points": bottom_points,
    }


def _patch_closed_mesh(monkeypatch):
    source_mesh = _closed_flat_mesh()

    monkeypatch.setattr(
        AtlasTerrainPipeline,
        "_build_closed_mesh",
        staticmethod(
            lambda **_kwargs: copy.deepcopy(
                source_mesh
            )
        ),
    )

    return source_mesh


def test_surface_texture_is_disabled_by_default(monkeypatch):
    source_mesh = _patch_closed_mesh(monkeypatch)

    result = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(50.0, 8.0, 50.1, 8.1),
        target_size_mm=20.0,
        size_x_mm=20.0,
        size_y_mm=20.0,
        z_scale=3000.0,
        base_z=1.0,
        bottom_z=0.0,
        grid_size=3,
        terrain_provider_name="srtm",
        debug=False,
    )

    assert result["top_points"] == source_mesh["top_points"]
    assert result["bottom_points"] == source_mesh["bottom_points"]
    assert "surface_texture" not in result["metadata"]


def test_surface_texture_deforms_only_interior_top_surface(monkeypatch):
    source_mesh = _patch_closed_mesh(monkeypatch)

    result = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(50.0, 8.0, 50.1, 8.1),
        target_size_mm=20.0,
        size_x_mm=20.0,
        size_y_mm=20.0,
        z_scale=3000.0,
        base_z=1.0,
        bottom_z=0.0,
        grid_size=3,
        terrain_provider_name="srtm",
        surface_texture_amplitude_mm=0.16,
        surface_texture_wavelength_x_mm=28.0,
        surface_texture_wavelength_y_mm=37.0,
        surface_texture_edge_fade_mm=4.0,
        debug=False,
    )

    top_points = result["top_points"]

    # Dört kenarın tamamı değişmeden kalır.
    assert all(point[2] == pytest.approx(1.0) for point in top_points[0])
    assert all(point[2] == pytest.approx(1.0) for point in top_points[-1])
    assert all(row[0][2] == pytest.approx(1.0) for row in top_points)
    assert all(row[-1][2] == pytest.approx(1.0) for row in top_points)

    # Merkez noktası düşük genlikli bir ofset alır.
    assert top_points[1][1][2] != pytest.approx(1.0)
    assert abs(top_points[1][1][2] - 1.0) <= 0.16 + 1e-9

    # Alt tabla kesinlikle değişmez.
    assert result["bottom_points"] == source_mesh["bottom_points"]

    # Üst yüzey üçgenleri yeni merkez noktasını kullanır.
    textured_center = top_points[1][1]

    assert any(
        textured_center in triangle
        for triangle in result["triangles"]
    )

    metadata = result["metadata"]["surface_texture"]

    assert metadata["enabled"] is True
    assert metadata["amplitude_mm"] == pytest.approx(0.16)
    assert metadata["wavelength_x_mm"] == pytest.approx(28.0)
    assert metadata["wavelength_y_mm"] == pytest.approx(37.0)
    assert metadata["edge_fade_mm"] == pytest.approx(4.0)


def test_surface_texture_and_terracing_cannot_be_enabled_together(
    monkeypatch,
):
    _patch_closed_mesh(monkeypatch)

    with pytest.raises(
        ValueError,
        match="surface texture.*terracing",
    ):
        AtlasTerrainPipeline.build_terrain_slab(
            bbox=(50.0, 8.0, 50.1, 8.1),
            target_size_mm=20.0,
            size_x_mm=20.0,
            size_y_mm=20.0,
            z_scale=3000.0,
            base_z=1.0,
            bottom_z=0.0,
            grid_size=3,
            terrain_provider_name="srtm",
            terrace_step_mm=0.30,
            surface_texture_amplitude_mm=0.16,
            debug=False,
        )
