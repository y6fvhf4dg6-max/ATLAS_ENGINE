import numpy as np
import pytest

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
)
from CORE.atlas_canonical_head_residual_detail_amplitude_policy import (
    AtlasCanonicalHeadResidualDetailAmplitudePolicy,
)
from CORE.atlas_canonical_head_residual_detail_amplitude_resolver import (
    AtlasCanonicalHeadResidualDetailAmplitudeResolver,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
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
            "left_eye": (1, 2),
            "right_eye": (4, 5),
        },
    )


def _amplitude_result():
    topology = _topology()

    observation = AtlasCanonicalHeadResidualDetailObservation(
        observation_id="fixture-detail",
        source_view_id="view-a",
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
                [0.2, 0.3],
                [0.4, 0.4],
                [0.6, 0.5],
                [0.8, 0.7],
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

    correspondence = AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="fixture-correspondence",
        topology=topology,
        observed_sample_to_canonical_vertex={
            10: 0,
            20: 2,
            30: 4,
            40: 5,
        },
    )

    return (
        AtlasCanonicalHeadResidualDetailAmplitudeResolver
        .resolve(
            observation=observation,
            correspondence=correspondence,
        )
    )


def test_applies_confidence_weighting_to_raw_scalar_detail():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudePolicy
        .apply(
            amplitude_result=_amplitude_result(),
            maximum_absolute_amplitude=1.0,
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


def test_zero_confidence_removes_residual_detail_contribution():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudePolicy
        .apply(
            amplitude_result=_amplitude_result(),
            maximum_absolute_amplitude=1.0,
        )
    )

    assert result.weighted_amplitude[4] == pytest.approx(
        0.0
    )


def test_clips_weighted_amplitude_symmetrically():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudePolicy
        .apply(
            amplitude_result=_amplitude_result(),
            maximum_absolute_amplitude=0.15,
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

    assert result.maximum_absolute_amplitude == pytest.approx(
        0.15
    )


def test_large_limit_preserves_weighted_amplitude():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudePolicy
        .apply(
            amplitude_result=_amplitude_result(),
            maximum_absolute_amplitude=1.0,
        )
    )

    assert result.bounded_amplitude == pytest.approx(
        result.weighted_amplitude
    )


def test_preserves_connectivity_signature_and_mapped_count():
    amplitude_result = _amplitude_result()

    result = (
        AtlasCanonicalHeadResidualDetailAmplitudePolicy
        .apply(
            amplitude_result=amplitude_result,
            maximum_absolute_amplitude=0.15,
        )
    )

    assert (
        result.connectivity_signature
        == amplitude_result.connectivity_signature
    )
    assert (
        result.mapped_vertex_count
        == amplitude_result.mapped_vertex_count
    )


def test_result_arrays_are_immutable():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudePolicy
        .apply(
            amplitude_result=_amplitude_result(),
            maximum_absolute_amplitude=0.15,
        )
    )

    assert result.weighted_amplitude.flags.writeable is False
    assert result.bounded_amplitude.flags.writeable is False

    with pytest.raises(ValueError):
        result.bounded_amplitude[0] = 99.0


@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -0.1,
        float("nan"),
        float("inf"),
        "invalid",
    ),
)
def test_rejects_invalid_maximum_absolute_amplitude(
    value,
):
    with pytest.raises(
        ValueError,
        match="maximum_absolute_amplitude",
    ):
        AtlasCanonicalHeadResidualDetailAmplitudePolicy.apply(
            amplitude_result=_amplitude_result(),
            maximum_absolute_amplitude=value,
        )


def test_rejects_non_amplitude_result():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadResidualDetailAmplitudeResult",
    ):
        AtlasCanonicalHeadResidualDetailAmplitudePolicy.apply(
            amplitude_result={},
            maximum_absolute_amplitude=0.15,
        )


def test_policy_does_not_mutate_raw_resolver_result():
    amplitude_result = _amplitude_result()

    raw_before = (
        amplitude_result
        .canonical_scalar_detail
        .copy()
    )
    confidence_before = (
        amplitude_result
        .canonical_confidence
        .copy()
    )

    AtlasCanonicalHeadResidualDetailAmplitudePolicy.apply(
        amplitude_result=amplitude_result,
        maximum_absolute_amplitude=0.15,
    )

    assert np.array_equal(
        amplitude_result.canonical_scalar_detail,
        raw_before,
    )
    assert np.array_equal(
        amplitude_result.canonical_confidence,
        confidence_before,
    )


def test_result_does_not_claim_visibility_projection_or_geometry():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudePolicy
        .apply(
            amplitude_result=_amplitude_result(),
            maximum_absolute_amplitude=0.15,
        )
    )

    assert not hasattr(
        result,
        "visibility",
    )
    assert not hasattr(
        result,
        "camera",
    )
    assert not hasattr(
        result,
        "pose",
    )
    assert not hasattr(
        result,
        "normal_projection",
    )
    assert not hasattr(
        result,
        "displacement",
    )
    assert not hasattr(
        result,
        "geometry",
    )
    assert not hasattr(
        result,
        "provider_id",
    )
    assert not hasattr(
        result,
        "phase_9_authorized",
    )
