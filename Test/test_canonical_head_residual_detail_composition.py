import numpy as np
import pytest

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)
from CORE.atlas_canonical_head_residual_detail_composition import (
    AtlasCanonicalHeadResidualDetailComposition,
)
from CORE.atlas_canonical_head_residual_detail_displacement import (
    AtlasCanonicalHeadResidualDetailDisplacement,
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
                [0.01, 0.00, 0.00],
                [0.00, 0.01, 0.00],
                [0.00, 0.00, 0.01],
                [0.01, 0.01, 0.00],
            ],
            dtype=np.float64,
        ),
    )


def _detail(topology=None):
    topology = topology or _topology()

    return AtlasCanonicalHeadResidualDetailDisplacement(
        detail_id="person-a-detail",
        topology=topology,
        displacement=np.array(
            [
                [0.0, 0.0, 0.002],
                [0.0, 0.0, -0.001],
                [0.0, 0.0, 0.003],
                [0.0, 0.0, 0.000],
            ],
            dtype=np.float64,
        ),
    )


def test_composes_identity_and_residual_detail_without_mutation():
    topology = _topology()
    identity = _identity(
        _reference(topology)
    )
    detail = _detail(topology)

    identity_before = (
        identity.resolved_geometry.vertices.copy()
    )
    detail_before = detail.displacement.copy()

    composition = AtlasCanonicalHeadResidualDetailComposition(
        identity_shape=identity,
        residual_detail_displacement=detail,
    )

    expected = (
        identity_before
        + detail_before
    )

    assert np.allclose(
        composition.resolved_geometry.vertices,
        expected,
    )
    assert np.array_equal(
        identity.resolved_geometry.vertices,
        identity_before,
    )
    assert np.array_equal(
        detail.displacement,
        detail_before,
    )


def test_preserves_canonical_connectivity_signature():
    topology = _topology()

    composition = AtlasCanonicalHeadResidualDetailComposition(
        identity_shape=_identity(
            _reference(topology)
        ),
        residual_detail_displacement=_detail(
            topology
        ),
    )

    assert (
        composition.connectivity_signature
        == topology.connectivity_signature
    )
    assert (
        composition.resolved_geometry.connectivity_signature
        == topology.connectivity_signature
    )


def test_accepts_different_topology_instances_with_same_connectivity():
    identity_topology = _topology(
        topology_id="identity-head",
    )
    detail_topology = _topology(
        topology_id="detail-head",
    )

    composition = AtlasCanonicalHeadResidualDetailComposition(
        identity_shape=_identity(
            _reference(identity_topology)
        ),
        residual_detail_displacement=_detail(
            detail_topology
        ),
    )

    assert (
        composition.connectivity_signature
        == identity_topology.connectivity_signature
    )


def test_blocks_mixed_connectivity():
    detail_topology = _topology(
        topology_id="different-head",
        faces=(
            (0, 1, 3),
            (1, 2, 3),
        ),
    )

    with pytest.raises(
        ValueError,
        match="BLOCKED_IDENTITY_RESIDUAL_DETAIL_CONNECTIVITY_MISMATCH",
    ):
        AtlasCanonicalHeadResidualDetailComposition(
            identity_shape=_identity(),
            residual_detail_displacement=_detail(
                detail_topology
            ),
        )


def test_rejects_non_identity_shape():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadIdentityShape",
    ):
        AtlasCanonicalHeadResidualDetailComposition(
            identity_shape={},
            residual_detail_displacement=_detail(),
        )


def test_rejects_non_residual_detail_displacement():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadResidualDetailDisplacement",
    ):
        AtlasCanonicalHeadResidualDetailComposition(
            identity_shape=_identity(),
            residual_detail_displacement={},
        )


def test_composition_does_not_claim_expression_pose_camera_provider_or_phase9():
    composition = AtlasCanonicalHeadResidualDetailComposition(
        identity_shape=_identity(),
        residual_detail_displacement=_detail(),
    )

    assert not hasattr(composition, "expression")
    assert not hasattr(composition, "pose")
    assert not hasattr(composition, "camera")
    assert not hasattr(composition, "provider_id")
    assert not hasattr(composition, "confidence")
    assert not hasattr(composition, "likeness_score")
    assert not hasattr(composition, "phase_9_authorized")
