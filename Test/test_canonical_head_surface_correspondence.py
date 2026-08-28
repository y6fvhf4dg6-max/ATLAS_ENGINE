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

# === PHASE 8 ITEM 10.7 SURFACE CORRESPONDENCE AUDIT RED ===


def test_surface_correspondence_audit_records_exact_evidence_and_direction_states():
    from CORE.atlas_canonical_head_surface_correspondence import (
        AtlasCanonicalHeadSurfaceCorrespondenceAudit,
    )

    result = AtlasCanonicalHeadSurfaceCorrespondenceAudit.evaluate(
        correspondence_evidence_class=(
            "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
        ),
        correspondence_direction="SOURCE_TO_TARGET",
        bidirectional_evaluation_state="NOT_PERFORMED",
        topology_independent_evaluation_state="NOT_ESTABLISHED",
        closest_point_assumption="NOT_USED",
        barycentric_projection_state="VERIFIED",
        source_sampling_density="KNOWN",
        target_sampling_density="KNOWN",
        resampling_method="NONE",
        area_weighting="NOT_APPLIED",
        density_normalization_assumption="NOT_APPLIED",
    )

    assert result.correspondence_evidence_class == (
        "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
    )
    assert result.correspondence_direction == "SOURCE_TO_TARGET"
    assert result.bidirectional_evaluation_state == "NOT_PERFORMED"
    assert result.topology_independent_evaluation_state == "NOT_ESTABLISHED"


def test_geometric_closest_point_correspondence_cannot_claim_anatomical_homology():
    from CORE.atlas_canonical_head_surface_correspondence import (
        AtlasCanonicalHeadSurfaceCorrespondenceAudit,
    )

    with pytest.raises(
        ValueError,
        match="anatomical|homology|closest",
    ):
        AtlasCanonicalHeadSurfaceCorrespondenceAudit.evaluate(
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            topology_independent_evaluation_state="VERIFIED",
            closest_point_assumption="USED",
            barycentric_projection_state="NOT_USED",
            source_sampling_density="KNOWN",
            target_sampling_density="KNOWN",
            resampling_method="NONE",
            area_weighting="NOT_APPLIED",
            density_normalization_assumption="NOT_APPLIED",
            anatomical_homology_state="CLAIMED",
        )


def test_geometric_closest_point_correspondence_records_no_anatomical_homology():
    from CORE.atlas_canonical_head_surface_correspondence import (
        AtlasCanonicalHeadSurfaceCorrespondenceAudit,
    )

    result = AtlasCanonicalHeadSurfaceCorrespondenceAudit.evaluate(
        correspondence_evidence_class=(
            "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
        ),
        correspondence_direction="SOURCE_TO_TARGET",
        bidirectional_evaluation_state="NOT_PERFORMED",
        topology_independent_evaluation_state="VERIFIED",
        closest_point_assumption="USED",
        barycentric_projection_state="NOT_USED",
        source_sampling_density="KNOWN",
        target_sampling_density="KNOWN",
        resampling_method="NONE",
        area_weighting="NOT_APPLIED",
        density_normalization_assumption="NOT_APPLIED",
        anatomical_homology_state="NOT_CLAIMED",
    )

    assert result.anatomical_homology_state == "NOT_CLAIMED"


def test_barycentric_projection_does_not_auto_promote_to_dense_anatomical_correspondence():
    from CORE.atlas_canonical_head_surface_correspondence import (
        AtlasCanonicalHeadSurfaceCorrespondenceAudit,
    )

    with pytest.raises(
        ValueError,
        match="dense|anatomical|barycentric",
    ):
        AtlasCanonicalHeadSurfaceCorrespondenceAudit.evaluate(
            correspondence_evidence_class="DENSE_ANATOMICAL_CORRESPONDENCE",
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            topology_independent_evaluation_state="NOT_ESTABLISHED",
            closest_point_assumption="NOT_USED",
            barycentric_projection_state="VERIFIED",
            source_sampling_density="KNOWN",
            target_sampling_density="KNOWN",
            resampling_method="NONE",
            area_weighting="NOT_APPLIED",
            density_normalization_assumption="NOT_APPLIED",
            anatomical_homology_state="NOT_CLAIMED",
        )


def test_bidirectional_state_requires_explicit_bidirectional_direction():
    from CORE.atlas_canonical_head_surface_correspondence import (
        AtlasCanonicalHeadSurfaceCorrespondenceAudit,
    )

    with pytest.raises(
        ValueError,
        match="bidirectional|direction",
    ):
        AtlasCanonicalHeadSurfaceCorrespondenceAudit.evaluate(
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="VERIFIED",
            topology_independent_evaluation_state="VERIFIED",
            closest_point_assumption="USED",
            barycentric_projection_state="NOT_USED",
            source_sampling_density="KNOWN",
            target_sampling_density="KNOWN",
            resampling_method="NONE",
            area_weighting="NOT_APPLIED",
            density_normalization_assumption="NOT_APPLIED",
            anatomical_homology_state="NOT_CLAIMED",
        )


def test_unknown_sampling_and_weighting_assumptions_remain_explicitly_unresolved():
    from CORE.atlas_canonical_head_surface_correspondence import (
        AtlasCanonicalHeadSurfaceCorrespondenceAudit,
    )

    result = AtlasCanonicalHeadSurfaceCorrespondenceAudit.evaluate(
        correspondence_evidence_class="UNRESOLVED_CORRESPONDENCE",
        correspondence_direction="UNRESOLVED",
        bidirectional_evaluation_state="UNRESOLVED",
        topology_independent_evaluation_state="UNRESOLVED",
        closest_point_assumption="UNRESOLVED",
        barycentric_projection_state="UNRESOLVED",
        source_sampling_density="UNRESOLVED",
        target_sampling_density="UNRESOLVED",
        resampling_method="UNRESOLVED",
        area_weighting="UNRESOLVED",
        density_normalization_assumption="UNRESOLVED",
        anatomical_homology_state="UNRESOLVED",
    )

    assert result.source_sampling_density == "UNRESOLVED"
    assert result.target_sampling_density == "UNRESOLVED"
    assert result.resampling_method == "UNRESOLVED"
    assert result.area_weighting == "UNRESOLVED"
    assert result.density_normalization_assumption == "UNRESOLVED"
