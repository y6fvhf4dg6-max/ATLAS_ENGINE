import numpy as np
import pytest

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)
from CORE.atlas_canonical_head_view_residual_detail_bridge import (
    AtlasCanonicalHeadViewResidualDetailBridge,
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
            "left_eye": (1, 2),
            "right_eye": (4, 5),
        },
    )


def _observation():
    return AtlasCanonicalHeadResidualDetailObservation(
        observation_id="subject-01-front-detail",
        source_view_id="subject-01-front",
        image_width=640,
        image_height=480,
        sample_indices=(
            10,
            20,
            30,
            40,
        ),
        sample_coordinates_normalized=np.array(
            [
                [0.20, 0.30],
                [0.40, 0.40],
                [0.60, 0.50],
                [0.80, 0.70],
            ],
            dtype=np.float64,
        ),
        scalar_detail=np.array(
            [
                0.10,
                -0.40,
                0.05,
                0.60,
            ],
            dtype=np.float64,
        ),
        confidence=np.array(
            [
                1.0,
                0.5,
                0.0,
                0.5,
            ],
            dtype=np.float64,
        ),
    )


def _correspondence():
    return AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="subject-01-front-correspondence",
        topology=_topology(),
        observed_sample_to_canonical_vertex={
            10: 0,
            20: 2,
            30: 4,
            40: 5,
        },
    )


def test_bridges_view_observation_through_existing_canonical_chain():
    result = (
        AtlasCanonicalHeadViewResidualDetailBridge
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.15,
        )
    )

    assert result.observation_id == "subject-01-front-detail"
    assert result.source_view_id == "subject-01-front"

    assert result.canonical_scalar_detail == pytest.approx(
        (
            0.10,
            0.0,
            -0.40,
            0.0,
            0.05,
            0.60,
        )
    )

    assert result.canonical_confidence == pytest.approx(
        (
            1.0,
            0.0,
            0.5,
            0.0,
            0.0,
            0.5,
        )
    )

    assert result.weighted_amplitude == pytest.approx(
        (
            0.10,
            0.0,
            -0.20,
            0.0,
            0.0,
            0.30,
        )
    )

    assert result.bounded_amplitude == pytest.approx(
        (
            0.10,
            0.0,
            -0.15,
            0.0,
            0.0,
            0.15,
        )
    )


def test_preserves_existing_resolver_and_policy_boundaries():
    result = (
        AtlasCanonicalHeadViewResidualDetailBridge
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.15,
        )
    )

    assert result.maximum_absolute_amplitude == pytest.approx(
        0.15
    )
    assert result.mapped_vertex_count == 4
    assert (
        result.connectivity_signature
        == _correspondence().connectivity_signature
    )


def test_result_arrays_are_immutable():
    result = (
        AtlasCanonicalHeadViewResidualDetailBridge
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.15,
        )
    )

    for array in (
        result.canonical_scalar_detail,
        result.canonical_confidence,
        result.weighted_amplitude,
        result.bounded_amplitude,
    ):
        assert array.flags.writeable is False

    with pytest.raises(ValueError):
        result.bounded_amplitude[0] = 99.0


def test_bridge_does_not_mutate_view_observation():
    observation = _observation()

    scalar_before = observation.scalar_detail.copy()
    confidence_before = observation.confidence.copy()

    AtlasCanonicalHeadViewResidualDetailBridge.resolve(
        observation=observation,
        correspondence=_correspondence(),
        maximum_absolute_amplitude=0.15,
    )

    assert np.array_equal(
        observation.scalar_detail,
        scalar_before,
    )
    assert np.array_equal(
        observation.confidence,
        confidence_before,
    )


def test_invalid_correspondence_is_blocked_by_existing_chain():
    topology = _topology()

    bad_correspondence = AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="bad-correspondence",
        topology=topology,
        observed_sample_to_canonical_vertex={
            10: 0,
            999: 1,
        },
    )

    with pytest.raises(
        ValueError,
        match="BLOCKED_RESIDUAL_DETAIL_OBSERVATION_SAMPLE_MISMATCH",
    ):
        AtlasCanonicalHeadViewResidualDetailBridge.resolve(
            observation=_observation(),
            correspondence=bad_correspondence,
            maximum_absolute_amplitude=0.15,
        )


def test_invalid_amplitude_policy_is_rejected_by_existing_policy():
    with pytest.raises(
        ValueError,
        match="maximum_absolute_amplitude",
    ):
        AtlasCanonicalHeadViewResidualDetailBridge.resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.0,
        )


def test_rejects_non_observation():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadResidualDetailObservation",
    ):
        AtlasCanonicalHeadViewResidualDetailBridge.resolve(
            observation={},
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.15,
        )


def test_rejects_non_correspondence():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadDenseCorrespondence",
    ):
        AtlasCanonicalHeadViewResidualDetailBridge.resolve(
            observation=_observation(),
            correspondence={},
            maximum_absolute_amplitude=0.15,
        )


def test_bridge_does_not_claim_projection_visibility_or_geometry():
    result = (
        AtlasCanonicalHeadViewResidualDetailBridge
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.15,
        )
    )

    assert not hasattr(result, "camera")
    assert not hasattr(result, "pose")
    assert not hasattr(result, "visibility")
    assert not hasattr(result, "occlusion")
    assert not hasattr(result, "projected_normal")
    assert not hasattr(result, "normal_direction")
    assert not hasattr(result, "displacement")
    assert not hasattr(result, "geometry")
    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "identity_score")
    assert not hasattr(result, "phase_9_authorized")
