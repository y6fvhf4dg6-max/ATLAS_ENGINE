import numpy as np
import pytest

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)
from CORE.atlas_canonical_head_identity_shape_compatibility_gate import (
    AtlasCanonicalHeadIdentityShapeCompatibilityGate,
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


def _shape(
    identity_shape_id,
    reference,
    amount,
):
    return AtlasCanonicalHeadIdentityShape(
        identity_shape_id=identity_shape_id,
        reference_geometry=reference,
        identity_displacement=np.full(
            reference.vertices.shape,
            amount,
            dtype=np.float64,
        ),
    )


def test_accepts_identity_shapes_sharing_reference_topology():
    reference = _reference()

    result = (
        AtlasCanonicalHeadIdentityShapeCompatibilityGate
        .evaluate(
            (
                _shape("person-a", reference, 0.01),
                _shape("person-b", reference, 0.02),
            )
        )
    )

    assert result.compatible is True
    assert result.status == "ACCEPTED"
    assert result.blocked_reasons == ()
    assert result.connectivity_signature == (
        reference.connectivity_signature
    )
    assert result.identity_shape_count == 2


def test_accepts_different_reference_instances_with_same_connectivity():
    first_reference = _reference(_topology("head-a"))
    second_reference = _reference(_topology("head-b"))

    result = (
        AtlasCanonicalHeadIdentityShapeCompatibilityGate
        .evaluate(
            (
                _shape(
                    "person-a",
                    first_reference,
                    0.01,
                ),
                _shape(
                    "person-b",
                    second_reference,
                    0.02,
                ),
            )
        )
    )

    assert result.compatible is True
    assert result.status == "ACCEPTED"


def test_blocks_mixed_connectivity_signatures():
    first_reference = _reference()

    different_topology = _topology(
        topology_id="different-head",
        faces=(
            (0, 1, 3),
            (1, 2, 3),
        ),
    )
    second_reference = _reference(
        different_topology
    )

    result = (
        AtlasCanonicalHeadIdentityShapeCompatibilityGate
        .evaluate(
            (
                _shape(
                    "person-a",
                    first_reference,
                    0.01,
                ),
                _shape(
                    "person-b",
                    second_reference,
                    0.02,
                ),
            )
        )
    )

    assert result.compatible is False
    assert result.status == "BLOCKED"
    assert (
        "BLOCKED_MIXED_CANONICAL_HEAD_CONNECTIVITY"
        in result.blocked_reasons
    )


def test_rejects_empty_identity_shape_collection():
    with pytest.raises(
        ValueError,
        match="identity_shapes",
    ):
        AtlasCanonicalHeadIdentityShapeCompatibilityGate.evaluate(
            ()
        )


def test_rejects_non_identity_shape_member():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadIdentityShape",
    ):
        AtlasCanonicalHeadIdentityShapeCompatibilityGate.evaluate(
            ({},)
        )


def test_result_does_not_claim_likeness_expression_pose_or_provider():
    reference = _reference()

    result = (
        AtlasCanonicalHeadIdentityShapeCompatibilityGate
        .evaluate(
            (
                _shape(
                    "person-a",
                    reference,
                    0.01,
                ),
            )
        )
    )

    assert not hasattr(result, "likeness_score")
    assert not hasattr(result, "identity_confidence")
    assert not hasattr(result, "expression")
    assert not hasattr(result, "pose")
    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "license_status")
