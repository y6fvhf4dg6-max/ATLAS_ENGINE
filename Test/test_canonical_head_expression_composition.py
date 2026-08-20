import numpy as np
import pytest

from CORE.atlas_canonical_head_expression_composition import (
    AtlasCanonicalHeadExpressionComposition,
)
from CORE.atlas_canonical_head_expression_displacement import (
    AtlasCanonicalHeadExpressionDisplacement,
)
from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology(
    topology_id="fixture-head-v1",
    faces=(
        (0, 1, 2),
        (0, 2, 3),
    ),
):
    return AtlasCanonicalHeadTopology(
        topology_id=topology_id,
        vertex_count=4,
        faces=faces,
        semantic_vertex_regions={
            "face": (0, 1, 2, 3),
            "nose": (0, 2),
            "left_eye": (0, 1),
            "right_eye": (2, 3),
        },
    )


def _reference(topology=None):
    topology = topology or _topology()

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


def _identity(reference=None):
    reference = reference or _reference()

    return AtlasCanonicalHeadIdentityShape(
        identity_shape_id="person-a",
        reference_geometry=reference,
        identity_displacement=np.array(
            [
                [0.00, 0.00, 0.10],
                [0.05, 0.00, 0.15],
                [0.05, 0.00, 0.20],
                [0.00, 0.00, 0.10],
            ],
            dtype=np.float64,
        ),
    )


def _expression(topology=None):
    topology = topology or _topology()

    return AtlasCanonicalHeadExpressionDisplacement(
        expression_id="smile",
        topology=topology,
        displacement=np.array(
            [
                [0.00, 0.00, 0.00],
                [0.00, -0.02, 0.01],
                [0.00, -0.03, 0.02],
                [0.00, 0.00, 0.00],
            ],
            dtype=np.float64,
        ),
    )


def test_resolved_geometry_is_identity_plus_expression_displacement():
    identity = _identity()
    expression = _expression(identity.reference_geometry.topology)

    composition = AtlasCanonicalHeadExpressionComposition(
        identity_shape=identity,
        expression_displacement=expression,
    )

    resolved = composition.resolved_geometry

    assert isinstance(resolved, AtlasCanonicalHeadGeometry)
    assert resolved.topology is identity.reference_geometry.topology

    np.testing.assert_allclose(
        resolved.vertices,
        (
            identity.resolved_geometry.vertices
            + expression.displacement
        ),
    )


def test_neutral_expression_preserves_identity_geometry():
    identity = _identity()
    topology = identity.reference_geometry.topology

    neutral = AtlasCanonicalHeadExpressionDisplacement(
        expression_id="neutral",
        topology=topology,
        displacement=np.zeros(
            (topology.vertex_count, 3),
            dtype=np.float64,
        ),
    )

    composition = AtlasCanonicalHeadExpressionComposition(
        identity_shape=identity,
        expression_displacement=neutral,
    )

    np.testing.assert_allclose(
        composition.resolved_geometry.vertices,
        identity.resolved_geometry.vertices,
    )


def test_composition_does_not_mutate_identity_or_expression():
    identity = _identity()
    expression = _expression(identity.reference_geometry.topology)

    before_identity = identity.resolved_geometry.vertices.copy()
    before_expression = expression.displacement.copy()

    composition = AtlasCanonicalHeadExpressionComposition(
        identity_shape=identity,
        expression_displacement=expression,
    )

    _ = composition.resolved_geometry

    np.testing.assert_allclose(
        identity.resolved_geometry.vertices,
        before_identity,
    )
    np.testing.assert_allclose(
        expression.displacement,
        before_expression,
    )


def test_blocks_mixed_connectivity():
    identity = _identity()

    different_topology = _topology(
        topology_id="different-head",
        faces=(
            (0, 1, 3),
            (1, 2, 3),
        ),
    )

    with pytest.raises(
        ValueError,
        match="BLOCKED_IDENTITY_EXPRESSION_CONNECTIVITY_MISMATCH",
    ):
        AtlasCanonicalHeadExpressionComposition(
            identity_shape=identity,
            expression_displacement=_expression(
                different_topology
            ),
        )


def test_rejects_non_identity_shape():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadIdentityShape",
    ):
        AtlasCanonicalHeadExpressionComposition(
            identity_shape={},
            expression_displacement=_expression(),
        )


def test_rejects_non_expression_displacement():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadExpressionDisplacement",
    ):
        AtlasCanonicalHeadExpressionComposition(
            identity_shape=_identity(),
            expression_displacement={},
        )


def test_contract_does_not_mix_pose_camera_provider_or_likeness():
    identity = _identity()
    expression = _expression(identity.reference_geometry.topology)

    composition = AtlasCanonicalHeadExpressionComposition(
        identity_shape=identity,
        expression_displacement=expression,
    )

    assert not hasattr(composition, "pose")
    assert not hasattr(composition, "camera")
    assert not hasattr(composition, "provider_id")
    assert not hasattr(composition, "confidence")
    assert not hasattr(composition, "likeness_score")
