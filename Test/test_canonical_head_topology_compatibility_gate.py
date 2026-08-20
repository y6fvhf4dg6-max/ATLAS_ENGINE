import pytest

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)
from CORE.atlas_canonical_head_topology_compatibility_gate import (
    AtlasCanonicalHeadTopologyCompatibilityGate,
)


def _topology(**overrides):
    values = {
        "topology_id": "fixture-head-v1",
        "vertex_count": 6,
        "faces": (
            (0, 1, 2),
            (0, 2, 3),
            (0, 3, 4),
            (0, 4, 5),
        ),
        "semantic_vertex_regions": {
            "face": (0, 1, 2, 3, 4, 5),
            "nose": (0, 2, 3),
            "left_eye": (1, 2),
            "right_eye": (4, 5),
        },
    }
    values.update(overrides)
    return AtlasCanonicalHeadTopology(**values)


def test_accepts_topology_with_required_canonical_regions():
    result = (
        AtlasCanonicalHeadTopologyCompatibilityGate
        .evaluate(_topology())
    )

    assert result.compatible is True
    assert result.status == "ACCEPTED"
    assert result.blocked_reasons == ()
    assert result.missing_regions == ()


@pytest.mark.parametrize(
    "missing_region",
    (
        "face",
        "nose",
        "left_eye",
        "right_eye",
    ),
)
def test_blocks_missing_required_semantic_region(
    missing_region,
):
    regions = {
        "face": (0, 1, 2, 3, 4, 5),
        "nose": (0, 2, 3),
        "left_eye": (1, 2),
        "right_eye": (4, 5),
    }
    del regions[missing_region]

    result = (
        AtlasCanonicalHeadTopologyCompatibilityGate
        .evaluate(
            _topology(
                semantic_vertex_regions=regions,
            )
        )
    )

    assert result.compatible is False
    assert result.status == "BLOCKED"
    assert missing_region in result.missing_regions
    assert (
        "BLOCKED_MISSING_CANONICAL_SEMANTIC_REGION"
        in result.blocked_reasons
    )


def test_required_region_policy_is_explicit_and_deterministic():
    assert (
        AtlasCanonicalHeadTopologyCompatibilityGate
        .REQUIRED_SEMANTIC_REGIONS
        == (
            "face",
            "nose",
            "left_eye",
            "right_eye",
        )
    )


def test_rejects_non_topology_contract():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadTopologyCompatibilityGate.evaluate(
            {}
        )


def test_result_does_not_claim_provider_or_identity_quality():
    result = (
        AtlasCanonicalHeadTopologyCompatibilityGate
        .evaluate(_topology())
    )

    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "identity_confidence")
    assert not hasattr(result, "likeness_score")
    assert not hasattr(result, "license_status")
