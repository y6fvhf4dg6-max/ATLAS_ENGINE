import numpy as np
import pytest

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
)
from CORE.atlas_canonical_head_residual_detail_correspondence_gate import (
    AtlasCanonicalHeadResidualDetailCorrespondenceGate,
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


def _observation():
    return AtlasCanonicalHeadResidualDetailObservation(
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
                0.1,
                -0.1,
                0.05,
                0.02,
            ],
            dtype=np.float64,
        ),
        confidence=np.array(
            [
                1.0,
                0.8,
                0.7,
                0.5,
            ],
            dtype=np.float64,
        ),
    )


def _correspondence(
    mapping=None,
):
    return AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="fixture-detail-correspondence",
        topology=_topology(),
        observed_sample_to_canonical_vertex=(
            mapping
            if mapping is not None
            else {
                10: 0,
                20: 2,
                40: 5,
            }
        ),
    )


def test_accepts_correspondence_whose_samples_exist_in_observation():
    result = (
        AtlasCanonicalHeadResidualDetailCorrespondenceGate
        .evaluate(
            observation=_observation(),
            correspondence=_correspondence(),
        )
    )

    assert result.compatible is True
    assert result.status == "ACCEPTED"
    assert result.blocked_reasons == ()
    assert result.matched_sample_count == 3

    assert result.observed_sample_indices == (
        10,
        20,
        40,
    )

    assert result.canonical_vertex_indices == (
        0,
        2,
        5,
    )

    assert (
        result.connectivity_signature
        == _correspondence().connectivity_signature
    )


def test_allows_observation_to_contain_unmapped_samples():
    result = (
        AtlasCanonicalHeadResidualDetailCorrespondenceGate
        .evaluate(
            observation=_observation(),
            correspondence=_correspondence(
                {
                    20: 1,
                    30: 4,
                }
            ),
        )
    )

    assert result.compatible is True
    assert result.matched_sample_count == 2
    assert result.observed_sample_indices == (
        20,
        30,
    )


def test_blocks_correspondence_referencing_unknown_observation_sample():
    result = (
        AtlasCanonicalHeadResidualDetailCorrespondenceGate
        .evaluate(
            observation=_observation(),
            correspondence=_correspondence(
                {
                    10: 0,
                    999: 1,
                }
            ),
        )
    )

    assert result.compatible is False
    assert result.status == "BLOCKED"
    assert result.blocked_reasons == (
        "BLOCKED_RESIDUAL_DETAIL_OBSERVATION_SAMPLE_MISMATCH",
    )
    assert result.matched_sample_count == 0
    assert result.observed_sample_indices == ()
    assert result.canonical_vertex_indices == ()
    assert result.connectivity_signature is None


def test_rejects_non_observation():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadResidualDetailObservation",
    ):
        AtlasCanonicalHeadResidualDetailCorrespondenceGate.evaluate(
            observation={},
            correspondence=_correspondence(),
        )


def test_rejects_non_dense_correspondence():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadDenseCorrespondence",
    ):
        AtlasCanonicalHeadResidualDetailCorrespondenceGate.evaluate(
            observation=_observation(),
            correspondence={},
        )


def test_result_does_not_apply_detail_or_confidence_policy():
    result = (
        AtlasCanonicalHeadResidualDetailCorrespondenceGate
        .evaluate(
            observation=_observation(),
            correspondence=_correspondence(),
        )
    )

    assert not hasattr(
        result,
        "canonical_amplitudes",
    )
    assert not hasattr(
        result,
        "weighted_detail",
    )
    assert not hasattr(
        result,
        "maximum_amplitude",
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
        "provider_id",
    )
    assert not hasattr(
        result,
        "phase_9_authorized",
    )
