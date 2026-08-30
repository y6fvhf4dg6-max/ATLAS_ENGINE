import numpy as np
import pytest

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)
from CORE.atlas_canonical_head_vertex_normal_evaluator import (
    AtlasCanonicalHeadVertexNormalEvaluator,
)


def _planar_geometry():
    topology = AtlasCanonicalHeadTopology(
        topology_id="planar-head",
        vertex_count=4,
        faces=(
            (0, 1, 2),
            (0, 2, 3),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3),
            "nose": (0, 2),
            "left_eye": (0, 1),
            "right_eye": (2, 3),
        },
    )

    return AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )


def test_evaluates_unit_vertex_normals():
    geometry = _planar_geometry()

    normals = (
        AtlasCanonicalHeadVertexNormalEvaluator
        .evaluate(
            geometry
        )
    )

    assert normals.shape == (
        geometry.vertex_count,
        3,
    )
    assert normals.dtype == np.float64
    assert np.all(
        np.isfinite(
            normals
        )
    )
    assert np.allclose(
        np.linalg.norm(
            normals,
            axis=1,
        ),
        1.0,
        atol=1e-12,
    )


def test_planar_counterclockwise_surface_points_positive_z():
    normals = (
        AtlasCanonicalHeadVertexNormalEvaluator
        .evaluate(
            _planar_geometry()
        )
    )

    expected = np.tile(
        np.array(
            [0.0, 0.0, 1.0],
            dtype=np.float64,
        ),
        (4, 1),
    )

    assert np.allclose(
        normals,
        expected,
        atol=1e-12,
    )


def test_reversing_face_winding_reverses_normals():
    topology = AtlasCanonicalHeadTopology(
        topology_id="reversed-head",
        vertex_count=4,
        faces=(
            (0, 2, 1),
            (0, 3, 2),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3),
            "nose": (0, 2),
            "left_eye": (0, 1),
            "right_eye": (2, 3),
        },
    )

    geometry = AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=_planar_geometry().vertices,
    )

    normals = (
        AtlasCanonicalHeadVertexNormalEvaluator
        .evaluate(
            geometry
        )
    )

    assert np.allclose(
        normals[:, 2],
        -1.0,
        atol=1e-12,
    )


def test_returns_immutable_snapshot():
    normals = (
        AtlasCanonicalHeadVertexNormalEvaluator
        .evaluate(
            _planar_geometry()
        )
    )

    assert normals.flags.writeable is False

    with pytest.raises(ValueError):
        normals[0, 0] = 1.0


def test_rejects_noncanonical_geometry():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadGeometry",
    ):
        AtlasCanonicalHeadVertexNormalEvaluator.evaluate(
            {}
        )


def test_rejects_degenerate_surface():
    topology = AtlasCanonicalHeadTopology(
        topology_id="degenerate-head",
        vertex_count=3,
        faces=(
            (0, 1, 2),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2),
            "nose": (0,),
            "left_eye": (1,),
            "right_eye": (2,),
        },
    )

    geometry = AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="degenerate",
    ):
        AtlasCanonicalHeadVertexNormalEvaluator.evaluate(
            geometry
        )


def test_evaluator_does_not_claim_provider_camera_pose_or_identity_quality():
    evaluator = AtlasCanonicalHeadVertexNormalEvaluator

    assert not hasattr(
        evaluator,
        "provider_id",
    )
    assert not hasattr(
        evaluator,
        "camera",
    )
    assert not hasattr(
        evaluator,
        "pose",
    )
    assert not hasattr(
        evaluator,
        "confidence",
    )
    assert not hasattr(
        evaluator,
        "likeness_score",
    )
    assert not hasattr(
        evaluator,
        "phase_9_authorized",
    )

def test_evaluates_indexed_surface_without_canonical_wrapper():
    vertices = (
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
    )
    faces = ((0, 1, 2),)

    normals = (
        AtlasCanonicalHeadVertexNormalEvaluator
        .evaluate_indexed_surface(
            vertices=vertices,
            faces=faces,
        )
    )

    assert normals.shape == (3, 3)
    np.testing.assert_allclose(
        normals,
        np.array(
            [
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0],
            ]
        ),
    )
    assert normals.flags.writeable is False
