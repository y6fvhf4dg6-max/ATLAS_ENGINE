import numpy as np
import pytest

from CORE.atlas_canonical_head_asymmetry_composition import (
    AtlasCanonicalHeadAsymmetryComposition,
)
from CORE.atlas_canonical_head_asymmetry_displacement import (
    AtlasCanonicalHeadAsymmetryDisplacement,
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


def _asymmetry(topology=None):
    topology = topology or _topology()

    return AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="person-a-natural",
        topology=topology,
        displacement=np.array(
            [
                [-0.02, 0.00, 0.01],
                [-0.01, 0.01, 0.00],
                [0.03, 0.00, -0.01],
                [0.00, -0.01, 0.02],
            ],
            dtype=np.float64,
        ),
    )


def test_resolved_geometry_is_identity_plus_asymmetry_displacement():
    identity = _identity()
    asymmetry = _asymmetry(identity.reference_geometry.topology)

    composition = AtlasCanonicalHeadAsymmetryComposition(
        identity_shape=identity,
        asymmetry_displacement=asymmetry,
    )

    resolved = composition.resolved_geometry

    assert isinstance(resolved, AtlasCanonicalHeadGeometry)
    assert resolved.topology is identity.reference_geometry.topology

    np.testing.assert_allclose(
        resolved.vertices,
        identity.resolved_geometry.vertices + asymmetry.displacement,
    )


def test_zero_asymmetry_preserves_identity_geometry():
    identity = _identity()
    topology = identity.reference_geometry.topology

    symmetric = AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="symmetric-baseline",
        topology=topology,
        displacement=np.zeros(
            (topology.vertex_count, 3),
            dtype=np.float64,
        ),
    )

    composition = AtlasCanonicalHeadAsymmetryComposition(
        identity_shape=identity,
        asymmetry_displacement=symmetric,
    )

    np.testing.assert_allclose(
        composition.resolved_geometry.vertices,
        identity.resolved_geometry.vertices,
    )


def test_composition_does_not_mutate_identity_or_asymmetry():
    identity = _identity()
    asymmetry = _asymmetry(identity.reference_geometry.topology)

    before_identity = identity.resolved_geometry.vertices.copy()
    before_asymmetry = asymmetry.displacement.copy()

    composition = AtlasCanonicalHeadAsymmetryComposition(
        identity_shape=identity,
        asymmetry_displacement=asymmetry,
    )

    _ = composition.resolved_geometry

    np.testing.assert_allclose(
        identity.resolved_geometry.vertices,
        before_identity,
    )
    np.testing.assert_allclose(
        asymmetry.displacement,
        before_asymmetry,
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
        match="BLOCKED_IDENTITY_ASYMMETRY_CONNECTIVITY_MISMATCH",
    ):
        AtlasCanonicalHeadAsymmetryComposition(
            identity_shape=identity,
            asymmetry_displacement=_asymmetry(
                different_topology
            ),
        )


def test_rejects_non_identity_shape():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadIdentityShape",
    ):
        AtlasCanonicalHeadAsymmetryComposition(
            identity_shape={},
            asymmetry_displacement=_asymmetry(),
        )


def test_rejects_non_asymmetry_displacement():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadAsymmetryDisplacement",
    ):
        AtlasCanonicalHeadAsymmetryComposition(
            identity_shape=_identity(),
            asymmetry_displacement={},
        )


def test_contract_does_not_mix_expression_pose_camera_provider_or_likeness():
    identity = _identity()
    asymmetry = _asymmetry(identity.reference_geometry.topology)

    composition = AtlasCanonicalHeadAsymmetryComposition(
        identity_shape=identity,
        asymmetry_displacement=asymmetry,
    )

    assert not hasattr(composition, "expression")
    assert not hasattr(composition, "pose")
    assert not hasattr(composition, "camera")
    assert not hasattr(composition, "provider_id")
    assert not hasattr(composition, "confidence")
    assert not hasattr(composition, "likeness_score")
