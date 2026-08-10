import pytest

from CORE.atlas_scene_morphology_mesh_area_resolver import (
    AtlasSceneMorphologyMeshAreaResolver,
)


def test_mesh_area_resolver_sums_xy_projected_triangle_area():
    meshes = [
        {
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (4.0, 0.0, 1.0),
                    (0.0, 2.0, 2.0),
                ),
                (
                    (10.0, 10.0, 0.0),
                    (12.0, 10.0, 0.0),
                    (10.0, 13.0, 0.0),
                ),
            ],
        },
    ]

    assert (
        AtlasSceneMorphologyMeshAreaResolver
        .projected_xy_area_mm2(meshes)
        == pytest.approx(7.0)
    )


def test_mesh_area_resolver_ignores_vertical_triangles():
    meshes = [
        {
            "triangles": [
                (
                    (1.0, 1.0, 0.0),
                    (1.0, 1.0, 3.0),
                    (1.0, 1.0, 6.0),
                ),
            ],
        },
    ]

    assert (
        AtlasSceneMorphologyMeshAreaResolver
        .projected_xy_area_mm2(meshes)
        == pytest.approx(0.0)
    )


def test_mesh_area_resolver_handles_empty_collection():
    assert (
        AtlasSceneMorphologyMeshAreaResolver
        .projected_xy_area_mm2(())
        == pytest.approx(0.0)
    )


def test_mesh_area_resolver_does_not_double_count_overlapping_projection():
    meshes = [
        {
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (4.0, 0.0, 0.0),
                    (0.0, 2.0, 0.0),
                ),
                (
                    (0.0, 0.0, 1.0),
                    (4.0, 0.0, 1.0),
                    (0.0, 2.0, 1.0),
                ),
            ],
        },
    ]

    assert (
        AtlasSceneMorphologyMeshAreaResolver
        .projected_xy_area_mm2(meshes)
        == pytest.approx(4.0)
    )
