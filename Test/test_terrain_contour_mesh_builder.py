import pytest

from CORE.atlas_terrain_contour_mesh_builder import (
    AtlasTerrainContourMeshBuilder,
)


def test_empty_contours_return_empty_mesh():
    triangles = AtlasTerrainContourMeshBuilder.build(
        contour_bands=[],
    )

    assert triangles == []


def test_single_band_returns_triangles():
    triangles = AtlasTerrainContourMeshBuilder.build(
        contour_bands=[
            [
                (0.0, 1.0),
                (10.0, 1.0),
                (10.0, -1.0),
                (0.0, -1.0),
            ]
        ],
    )

    assert len(triangles) > 0
