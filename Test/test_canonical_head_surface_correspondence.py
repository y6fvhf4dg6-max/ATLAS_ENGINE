import pytest

from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology():
    return AtlasCanonicalHeadTopology(
        topology_id="fixture-head",
        vertex_count=6,
        faces=(
            (0, 1, 2),
            (0, 2, 3),
            (0, 3, 4),
            (0, 4, 5),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3, 4, 5),
            "nose": (0, 2),
        },
    )


def test_preserves_observed_sample_to_canonical_surface_mapping():
    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id="fixture-surface-correspondence",
        topology=_topology(),
        observed_sample_to_canonical_surface={
            10: (0, (0.20, 0.30, 0.50)),
            20: (2, (0.10, 0.70, 0.20)),
        },
    )

    assert correspondence.correspondence_id == (
        "fixture-surface-correspondence"
    )
    assert correspondence.observed_sample_indices == (10, 20)
    assert correspondence.correspondence_count == 2

    assert correspondence.canonical_surface_location(10) == (
        0,
        pytest.approx((0.20, 0.30, 0.50)),
    )
    assert correspondence.canonical_surface_location(20) == (
        2,
        pytest.approx((0.10, 0.70, 0.20)),
    )

    assert (
        correspondence.connectivity_signature
        == _topology().connectivity_signature
    )


def test_allows_multiple_samples_on_same_canonical_face():
    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id="same-face",
        topology=_topology(),
        observed_sample_to_canonical_surface={
            10: (1, (1.0, 0.0, 0.0)),
            20: (1, (0.0, 1.0, 0.0)),
            30: (1, (0.0, 0.0, 1.0)),
        },
    )

    assert correspondence.correspondence_count == 3
    assert correspondence.canonical_face_indices == (
        1,
        1,
        1,
    )


@pytest.mark.parametrize(
    "mapping, expected",
    (
        (
            {10: (99, (0.2, 0.3, 0.5))},
            "canonical face index",
        ),
        (
            {10: (0, (0.2, 0.8))},
            "barycentric weights",
        ),
        (
            {10: (0, (0.2, float('nan'), 0.8))},
            "finite",
        ),
        (
            {10: (0, (-0.1, 0.5, 0.6))},
            "0.0..1.0",
        ),
        (
            {10: (0, (0.2, 0.3, 0.4))},
            "sum to 1.0",
        ),
    ),
)
def test_rejects_invalid_surface_locations(
    mapping,
    expected,
):
    with pytest.raises(
        (TypeError, ValueError),
        match=expected,
    ):
        AtlasCanonicalHeadSurfaceCorrespondence(
            correspondence_id="invalid",
            topology=_topology(),
            observed_sample_to_canonical_surface=mapping,
        )


def test_accepts_tiny_floating_point_barycentric_boundary_noise():
    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id="floating-point-boundary",
        topology=_topology(),
        observed_sample_to_canonical_surface={
            10: (
                0,
                (
                    -1.3322676295501878e-15,
                    0.25,
                    0.7500000000000013,
                ),
            ),
        },
    )

    face_index, weights = correspondence.canonical_surface_location(
        10
    )

    assert face_index == 0
    assert weights == pytest.approx(
        (0.0, 0.25, 0.75),
        abs=1e-15,
    )
    assert sum(weights) == pytest.approx(
        1.0,
        abs=1e-15,
    )



def test_rejects_invalid_sample_index():
    with pytest.raises(
        (TypeError, ValueError),
        match="observed sample index",
    ):
        AtlasCanonicalHeadSurfaceCorrespondence(
            correspondence_id="invalid-sample",
            topology=_topology(),
            observed_sample_to_canonical_surface={
                -1: (0, (0.2, 0.3, 0.5)),
            },
        )


def test_contract_does_not_claim_provider_or_geometry_application():
    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id="boundary-only",
        topology=_topology(),
        observed_sample_to_canonical_surface={
            10: (0, (0.2, 0.3, 0.5)),
        },
    )

    for forbidden_attribute in (
        "provider_id",
        "camera",
        "pose",
        "visibility",
        "identity_confidence",
        "scalar_detail",
        "displacement",
        "geometry",
        "phase_9_authorized",
    ):
        assert not hasattr(
            correspondence,
            forbidden_attribute,
        )
