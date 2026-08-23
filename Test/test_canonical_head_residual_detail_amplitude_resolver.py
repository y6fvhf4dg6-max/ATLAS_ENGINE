import numpy as np
import pytest

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
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
                0.10,
                -0.20,
                0.05,
                0.30,
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
    topology = _topology()

    return AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="fixture-correspondence",
        topology=topology,
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


def test_resolves_raw_scalar_detail_to_canonical_vertices():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudeResolver
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
        )
    )

    assert result.canonical_scalar_detail.shape == (
        6,
    )

    assert result.canonical_scalar_detail == pytest.approx(
        (
            0.10,
            0.0,
            -0.20,
            0.0,
            0.0,
            0.30,
        )
    )

    assert result.mapped_vertex_count == 3


def test_preserves_confidence_as_separate_canonical_channel():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudeResolver
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
        )
    )

    assert result.canonical_confidence == pytest.approx(
        (
            1.0,
            0.0,
            0.8,
            0.0,
            0.0,
            0.5,
        )
    )

    # Raw scalar detail must NOT be multiplied by confidence here.
    assert result.canonical_scalar_detail[2] == pytest.approx(
        -0.20
    )
    assert result.canonical_confidence[2] == pytest.approx(
        0.8
    )


def test_unmapped_canonical_vertices_remain_zero():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudeResolver
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(
                {
                    30: 4,
                }
            ),
        )
    )

    assert result.canonical_scalar_detail == pytest.approx(
        (
            0.0,
            0.0,
            0.0,
            0.0,
            0.05,
            0.0,
        )
    )

    assert result.canonical_confidence == pytest.approx(
        (
            0.0,
            0.0,
            0.0,
            0.0,
            0.7,
            0.0,
        )
    )


def test_result_preserves_connectivity_signature():
    correspondence = _correspondence()

    result = (
        AtlasCanonicalHeadResidualDetailAmplitudeResolver
        .resolve(
            observation=_observation(),
            correspondence=correspondence,
        )
    )

    assert (
        result.connectivity_signature
        == correspondence.connectivity_signature
    )


def test_result_arrays_are_immutable():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudeResolver
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
        )
    )

    assert result.canonical_scalar_detail.flags.writeable is False
    assert result.canonical_confidence.flags.writeable is False

    with pytest.raises(
        ValueError
    ):
        result.canonical_scalar_detail[0] = 9.0


def test_blocks_unknown_observation_sample_via_existing_gate():
    with pytest.raises(
        ValueError,
        match="BLOCKED_RESIDUAL_DETAIL_OBSERVATION_SAMPLE_MISMATCH",
    ):
        AtlasCanonicalHeadResidualDetailAmplitudeResolver.resolve(
            observation=_observation(),
            correspondence=_correspondence(
                {
                    10: 0,
                    999: 1,
                }
            ),
        )


def test_rejects_invalid_inputs():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadResidualDetailObservation",
    ):
        AtlasCanonicalHeadResidualDetailAmplitudeResolver.resolve(
            observation={},
            correspondence=_correspondence(),
        )

    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadDenseCorrespondence",
    ):
        AtlasCanonicalHeadResidualDetailAmplitudeResolver.resolve(
            observation=_observation(),
            correspondence={},
        )


def test_result_does_not_apply_policy_or_produce_geometry():
    result = (
        AtlasCanonicalHeadResidualDetailAmplitudeResolver
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
        )
    )

    assert not hasattr(
        result,
        "weighted_amplitude",
    )
    assert not hasattr(
        result,
        "maximum_amplitude",
    )
    assert not hasattr(
        result,
        "clipped_amplitude",
    )
    assert not hasattr(
        result,
        "visibility",
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
        "phase_9_authorized",
    )
