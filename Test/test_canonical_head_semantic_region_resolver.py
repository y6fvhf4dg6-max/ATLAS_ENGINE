import pytest

from CORE.atlas_canonical_head_semantic_boundary import (
    AtlasCanonicalHeadSemanticBoundary,
)
from CORE.atlas_canonical_head_semantic_region_resolver import (
    AtlasCanonicalHeadSemanticRegionResolver,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology():
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
        semantic_vertex_regions={
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


def test_resolves_canonical_head_region_vertex_indices():
    resolver = AtlasCanonicalHeadSemanticRegionResolver(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert resolver.vertex_indices("jaw") == (2, 3, 4, 5)
    assert resolver.vertex_indices("chin") == (3, 4)


def test_normalizes_region_name():
    resolver = AtlasCanonicalHeadSemanticRegionResolver(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert resolver.vertex_indices("  Left Eye Region  ") == (1, 2)


def test_rejects_separate_component_as_topology_region():
    resolver = AtlasCanonicalHeadSemanticRegionResolver(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    with pytest.raises(
        ValueError,
        match="separate_component",
    ):
        resolver.vertex_indices("hair")


def test_rejects_optional_detail_layer_as_topology_region():
    resolver = AtlasCanonicalHeadSemanticRegionResolver(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    with pytest.raises(
        ValueError,
        match="optional_detail_layer",
    ):
        resolver.vertex_indices("beard")


def test_rejects_unknown_semantic_name():
    resolver = AtlasCanonicalHeadSemanticRegionResolver(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    with pytest.raises(
        KeyError,
        match="semantic ownership",
    ):
        resolver.vertex_indices("unknown-part")


def test_rejects_incompatible_topology_boundary_pair():
    topology = AtlasCanonicalHeadTopology(
        topology_id="missing-neck",
        vertex_count=4,
        faces=(
            (0, 1, 2),
            (0, 2, 3),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3),
            "left_ear": (0, 1),
            "right_ear": (2, 3),
            "jaw": (1, 2),
            "chin": (1, 2),
            "left_eye_region": (0, 1),
            "right_eye_region": (2, 3),
        },
    )

    with pytest.raises(
        ValueError,
        match="BLOCKED_MISSING_CANONICAL_HEAD_SEMANTIC_REGION",
    ):
        AtlasCanonicalHeadSemanticRegionResolver(
            topology=topology,
            boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
        )


def test_contract_does_not_claim_geometry_provider_or_identity_confidence():
    resolver = AtlasCanonicalHeadSemanticRegionResolver(
        topology=_topology(),
        boundary=AtlasCanonicalHeadSemanticBoundary.production_v1(),
    )

    assert not hasattr(resolver, "vertices")
    assert not hasattr(resolver, "provider_id")
    assert not hasattr(resolver, "confidence")
    assert not hasattr(resolver, "likeness_score")
    assert not hasattr(resolver, "identity_shape")
