import pytest

from CORE.atlas_canonical_head_semantic_boundary import (
    AtlasCanonicalHeadSemanticBoundary,
)
from CORE.atlas_canonical_head_semantic_boundary_compatibility_gate import (
    AtlasCanonicalHeadSemanticBoundaryCompatibilityGate,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology(regions=None):
    return AtlasCanonicalHeadTopology(
        topology_id="fixture-head-v1",
        vertex_count=8,
        faces=(
            (0, 1, 2),
            (0, 2, 3),
            (0, 3, 4),
            (0, 4, 5),
            (0, 5, 6),
            (0, 6, 7),
        ),
        semantic_vertex_regions=regions
        or {
            "face": (0, 1, 2, 3, 4, 5, 6, 7),
            "left_ear": (0, 1),
            "right_ear": (6, 7),
            "jaw": (2, 3, 4, 5),
            "chin": (3, 4),
            "neck": (0, 7),
            "left_eye_region": (1, 2),
            "right_eye_region": (5, 6),
        },
    )


def test_accepts_topology_covering_all_canonical_head_regions():
    result = AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert result.compatible is True
    assert result.status == "ACCEPTED"
    assert result.blocked_reasons == ()
    assert result.missing_canonical_regions == ()


def test_blocks_missing_required_canonical_head_region():
    topology = _topology(
        {
            "face": (0, 1, 2, 3, 4, 5, 6, 7),
            "left_ear": (0, 1),
            "right_ear": (6, 7),
            "jaw": (2, 3, 4, 5),
            "chin": (3, 4),
            "neck": (0, 7),
            "left_eye_region": (1, 2),
        }
    )

    result = AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
        topology=topology,
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert result.compatible is False
    assert result.status == "BLOCKED"
    assert result.blocked_reasons == (
        "BLOCKED_MISSING_CANONICAL_HEAD_SEMANTIC_REGION",
    )
    assert result.missing_canonical_regions == (
        "right_eye_region",
    )


def test_separate_components_are_not_required_topology_regions():
    topology = _topology()

    result = AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
        topology=topology,
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert "hair" not in topology.semantic_vertex_regions
    assert "left_eyeball" not in topology.semantic_vertex_regions
    assert "right_eyeball" not in topology.semantic_vertex_regions
    assert result.compatible is True


def test_optional_detail_layers_are_not_required_topology_regions():
    topology = _topology()

    result = AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
        topology=topology,
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert "beard" not in topology.semantic_vertex_regions
    assert "moustache" not in topology.semantic_vertex_regions
    assert result.compatible is True


def test_rejects_noncanonical_topology():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
            topology={},
            boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
        )


def test_rejects_nonsemantic_boundary():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadSemanticBoundary",
    ):
        AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
            topology=_topology(),
            boundary={},
        )


def test_result_does_not_claim_geometry_provider_or_identity_confidence():
    result = AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert not hasattr(result, "vertices")
    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "confidence")
    assert not hasattr(result, "likeness_score")
    assert not hasattr(result, "identity_shape")
