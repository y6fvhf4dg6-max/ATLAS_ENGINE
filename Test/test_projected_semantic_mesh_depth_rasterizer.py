import numpy as np

from CORE.atlas_projected_semantic_mesh_depth_rasterizer import (
    AtlasProjectedSemanticMeshDepthRasterizer,
)


def test_rasterizes_planar_projected_triangle_depth_into_target_grid():
    mesh = {
        "triangles": [
            (
                (0.0, 0.0, 0.20),
                (4.0, 0.0, 0.20),
                (0.0, 4.0, 0.20),
            ),
        ],
    }

    result = (
        AtlasProjectedSemanticMeshDepthRasterizer
        .rasterize(
            mesh=mesh,
            width_mm=4.0,
            depth_mm=4.0,
            rows=5,
            columns=5,
        )
    )

    assert result["type"] == (
        "projected_semantic_mesh_depth_rasterization"
    )

    depth_map = result["depth_map"]
    coverage_map = result["coverage_map"]

    assert depth_map.shape == (5, 5)
    assert coverage_map.shape == (5, 5)

    assert np.count_nonzero(coverage_map) > 0

    np.testing.assert_allclose(
        depth_map[coverage_map],
        0.20,
    )


def test_overlapping_projected_triangles_keep_greatest_outward_depth():
    mesh = {
        "triangles": [
            (
                (0.0, 0.0, 0.15),
                (4.0, 0.0, 0.15),
                (0.0, 4.0, 0.15),
            ),
            (
                (0.0, 0.0, 0.35),
                (4.0, 0.0, 0.35),
                (0.0, 4.0, 0.35),
            ),
        ],
    }

    result = (
        AtlasProjectedSemanticMeshDepthRasterizer
        .rasterize(
            mesh=mesh,
            width_mm=4.0,
            depth_mm=4.0,
            rows=5,
            columns=5,
        )
    )

    covered = result["coverage_map"]

    np.testing.assert_allclose(
        result["depth_map"][covered],
        0.35,
    )


def test_rasterizes_world_space_projected_mesh_through_surface_target_frame():
    import pytest

    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="facade",
        source_component_id="ornament",
        target_component_id="wall",
        quad=(
            (10.0, 20.0, 5.0),
            (14.0, 20.0, 5.0),
            (14.0, 20.0, 9.0),
            (10.0, 20.0, 9.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    # These are WORLD-SPACE points corresponding to local:
    # (u=0,v=0,d=0.25)
    # (u=4,v=0,d=0.25)
    # (u=0,v=4,d=0.25)
    #
    # Target outward normal is (0,-1,0), therefore outward
    # depth 0.25 moves world Y from 20.0 to 19.75.
    mesh = {
        "triangles": [
            (
                (10.0, 19.75, 5.0),
                (14.0, 19.75, 5.0),
                (10.0, 19.75, 9.0),
            ),
        ],
    }

    result = (
        AtlasProjectedSemanticMeshDepthRasterizer
        .rasterize(
            mesh=mesh,
            target=target,
            width_mm=4.0,
            depth_mm=4.0,
            rows=5,
            columns=5,
        )
    )

    covered = result["coverage_map"]

    assert np.count_nonzero(covered) > 0

    np.testing.assert_allclose(
        result["depth_map"][covered],
        0.25,
    )

    assert result["coordinate_space"] == (
        "target_local_uv_signed_depth"
    )


def test_inward_world_space_projection_returns_negative_signed_depth():
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="recessed_facade",
        source_component_id="opening",
        target_component_id="wall",
        quad=(
            (0.0, 0.0, 0.0),
            (4.0, 0.0, 0.0),
            (4.0, 0.0, 4.0),
            (0.0, 0.0, 4.0),
        ),
        relief_polarity="inward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    # outward_normal = (0,-1,0)
    # inward depth 0.40 is therefore world Y = +0.40.
    mesh = {
        "triangles": [
            (
                (0.0, 0.40, 0.0),
                (4.0, 0.40, 0.0),
                (0.0, 0.40, 4.0),
            ),
        ],
    }

    result = (
        AtlasProjectedSemanticMeshDepthRasterizer
        .rasterize(
            mesh=mesh,
            target=target,
            width_mm=4.0,
            depth_mm=4.0,
            rows=5,
            columns=5,
        )
    )

    covered = result["coverage_map"]

    np.testing.assert_allclose(
        result["depth_map"][covered],
        -0.40,
    )


def test_inward_overlapping_world_triangles_keep_most_recessed_signed_depth():
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="recessed_opening",
        source_component_id="opening",
        target_component_id="wall",
        quad=(
            (0.0, 0.0, 0.0),
            (4.0, 0.0, 0.0),
            (4.0, 0.0, 4.0),
            (0.0, 0.0, 4.0),
        ),
        relief_polarity="inward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    # outward_normal = (0,-1,0)
    # world Y = 0.0  -> signed depth  0.0
    # world Y = 0.6  -> signed depth -0.6
    mesh = {
        "triangles": [
            (
                (0.0, 0.0, 0.0),
                (4.0, 0.0, 0.0),
                (0.0, 0.0, 4.0),
            ),
            (
                (0.0, 0.60, 0.0),
                (4.0, 0.60, 0.0),
                (0.0, 0.60, 4.0),
            ),
        ],
    }

    result = (
        AtlasProjectedSemanticMeshDepthRasterizer
        .rasterize(
            mesh=mesh,
            target=target,
            width_mm=4.0,
            depth_mm=4.0,
            rows=5,
            columns=5,
        )
    )

    covered = result["coverage_map"]

    np.testing.assert_allclose(
        result["depth_map"][covered],
        -0.60,
    )


def test_visible_winner_preserves_face_index_and_barycentric_weights():
    mesh = {
        "triangles": [
            (
                (0.0, 0.0, 0.15),
                (4.0, 0.0, 0.15),
                (0.0, 4.0, 0.15),
            ),
            (
                (0.0, 0.0, 0.35),
                (4.0, 0.0, 0.35),
                (0.0, 4.0, 0.35),
            ),
        ],
    }

    result = AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
        mesh=mesh,
        width_mm=4.0,
        depth_mm=4.0,
        rows=5,
        columns=5,
    )

    covered = result["coverage_map"]
    face_index_map = result["face_index_map"]
    barycentric_map = result["barycentric_map"]

    assert face_index_map.shape == (5, 5)
    assert barycentric_map.shape == (5, 5, 3)

    assert np.all(face_index_map[covered] == 1)
    np.testing.assert_allclose(
        np.sum(barycentric_map[covered], axis=1),
        1.0,
        atol=1e-12,
    )
    assert np.all(
        barycentric_map[covered] >= -1e-12
    )


def test_visible_surface_interpolates_indexed_vertex_normals():
    mesh = {
        "triangles": [
            (
                (0.0, 0.0, 0.20),
                (4.0, 0.0, 0.20),
                (0.0, 4.0, 0.20),
            ),
        ],
        "vertex_normals": [
            (0.0, 0.0, 1.0),
            (0.0, 0.0, 1.0),
            (0.0, 0.0, 1.0),
        ],
        "face_vertex_indices": [
            (0, 1, 2),
        ],
    }

    result = AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
        mesh=mesh,
        width_mm=4.0,
        depth_mm=4.0,
        rows=5,
        columns=5,
    )

    covered = result["coverage_map"]
    normal_map = result["normal_map"]

    assert normal_map.shape == (5, 5, 3)

    np.testing.assert_allclose(
        normal_map[covered],
        np.tile(
            np.array([0.0, 0.0, 1.0]),
            (np.count_nonzero(covered), 1),
        ),
        atol=1e-12,
    )
    np.testing.assert_allclose(
        np.linalg.norm(normal_map[covered], axis=1),
        1.0,
        atol=1e-12,
    )


def test_visible_normal_follows_same_overlap_winner_as_depth():
    mesh = {
        "triangles": [
            ((0., 0., .15), (4., 0., .15), (0., 4., .15)),
            ((0., 0., .35), (4., 0., .35), (0., 4., .35)),
        ],
        "vertex_normals": [
            (0., 0., 1.), (0., 0., 1.), (0., 0., 1.),
            (0., 1., 1.), (0., 1., 1.), (0., 1., 1.),
        ],
        "face_vertex_indices": [
            (0, 1, 2),
            (3, 4, 5),
        ],
    }

    result = AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
        mesh=mesh,
        width_mm=4.0,
        depth_mm=4.0,
        rows=5,
        columns=5,
    )

    covered = result["coverage_map"]
    expected = np.array([0., 1., 1.])
    expected /= np.linalg.norm(expected)

    np.testing.assert_allclose(
        result["normal_map"][covered],
        np.tile(expected, (np.count_nonzero(covered), 1)),
        atol=1e-12,
    )
    assert np.all(result["face_index_map"][covered] == 1)


def test_visible_normal_barycentrically_interpolates_and_normalizes():
    mesh = {
        "triangles": [
            ((0., 0., .2), (4., 0., .2), (0., 4., .2)),
        ],
        "vertex_normals": [
            (1., 0., 1.),
            (0., 1., 1.),
            (0., 0., 1.),
        ],
        "face_vertex_indices": [(0, 1, 2)],
    }

    result = AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
        mesh=mesh,
        width_mm=4.0,
        depth_mm=4.0,
        rows=5,
        columns=5,
    )

    covered = result["coverage_map"]

    np.testing.assert_allclose(
        np.linalg.norm(result["normal_map"][covered], axis=1),
        1.0,
        atol=1e-12,
    )

    row, column = np.argwhere(covered)[0]
    weights = result["barycentric_map"][row, column]
    raw = (
        weights[0] * np.array([1., 0., 1.])
        + weights[1] * np.array([0., 1., 1.])
        + weights[2] * np.array([0., 0., 1.])
    )
    expected = raw / np.linalg.norm(raw)

    np.testing.assert_allclose(
        result["normal_map"][row, column],
        expected,
        atol=1e-12,
    )
