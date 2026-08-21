import numpy as np
import pytest

from CORE.atlas_canonical_head_asymmetry_compatibility_gate import (
    AtlasCanonicalHeadAsymmetryCompatibilityGate,
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
        identity_displacement=np.full(
            reference.vertices.shape,
            0.01,
            dtype=np.float64,
        ),
    )


def _asymmetry(topology=None):
    topology = topology or _topology()

    return AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="person-a-natural",
        topology=topology,
        displacement=np.full(
            (topology.vertex_count, 3),
            0.02,
            dtype=np.float64,
        ),
    )


def test_accepts_identity_and_asymmetry_with_same_connectivity():
    topology = _topology()

    result = AtlasCanonicalHeadAsymmetryCompatibilityGate.evaluate(
        identity_shape=_identity(_reference(topology)),
        asymmetry_displacement=_asymmetry(topology),
    )

    assert result.compatible is True
    assert result.status == "ACCEPTED"
    assert result.blocked_reasons == ()
    assert (
        result.connectivity_signature
        == topology.connectivity_signature
    )


def test_accepts_different_topology_instances_with_same_connectivity():
    identity_topology = _topology(
        topology_id="identity-head",
    )
    asymmetry_topology = _topology(
        topology_id="asymmetry-head",
    )

    result = AtlasCanonicalHeadAsymmetryCompatibilityGate.evaluate(
        identity_shape=_identity(
            _reference(identity_topology)
        ),
        asymmetry_displacement=_asymmetry(
            asymmetry_topology
        ),
    )

    assert result.compatible is True
    assert result.status == "ACCEPTED"


def test_blocks_identity_asymmetry_with_mixed_connectivity():
    different_topology = _topology(
        topology_id="different-head",
        faces=(
            (0, 1, 3),
            (1, 2, 3),
        ),
    )

    result = AtlasCanonicalHeadAsymmetryCompatibilityGate.evaluate(
        identity_shape=_identity(),
        asymmetry_displacement=_asymmetry(
            different_topology
        ),
    )

    assert result.compatible is False
    assert result.status == "BLOCKED"
    assert result.blocked_reasons == (
        "BLOCKED_IDENTITY_ASYMMETRY_CONNECTIVITY_MISMATCH",
    )
    assert result.connectivity_signature is None


def test_rejects_non_identity_shape():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadIdentityShape",
    ):
        AtlasCanonicalHeadAsymmetryCompatibilityGate.evaluate(
            identity_shape={},
            asymmetry_displacement=_asymmetry(),
        )


def test_rejects_non_asymmetry_displacement():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadAsymmetryDisplacement",
    ):
        AtlasCanonicalHeadAsymmetryCompatibilityGate.evaluate(
            identity_shape=_identity(),
            asymmetry_displacement={},
        )


def test_result_does_not_claim_expression_pose_camera_provider_or_confidence():
    result = AtlasCanonicalHeadAsymmetryCompatibilityGate.evaluate(
        identity_shape=_identity(),
        asymmetry_displacement=_asymmetry(),
    )

    assert not hasattr(result, "expression")
    assert not hasattr(result, "pose")
    assert not hasattr(result, "camera")
    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "confidence")
    assert not hasattr(result, "likeness_score")
