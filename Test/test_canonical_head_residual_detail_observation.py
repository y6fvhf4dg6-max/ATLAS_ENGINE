from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)


def _observation():
    return AtlasCanonicalHeadResidualDetailObservation(
        observation_id="  Subject 01 Front Detail  ",
        source_view_id=" subject_01_front ",
        image_width=1536,
        image_height=1152,
        sample_indices=(
            10,
            20,
            30,
        ),
        sample_coordinates_normalized=np.array(
            [
                [0.25, 0.30],
                [0.50, 0.55],
                [0.75, 0.70],
            ],
            dtype=np.float64,
        ),
        scalar_detail=np.array(
            [
                0.10,
                -0.05,
                0.02,
            ],
            dtype=np.float64,
        ),
        confidence=np.array(
            [
                1.0,
                0.8,
                0.4,
            ],
            dtype=np.float64,
        ),
    )


def test_preserves_indexed_image_space_residual_detail_observation():
    observation = _observation()

    assert observation.observation_id == (
        "subject_01_front_detail"
    )
    assert observation.source_view_id == (
        "subject_01_front"
    )

    assert observation.image_width == 1536
    assert observation.image_height == 1152

    assert observation.sample_indices == (
        10,
        20,
        30,
    )

    assert observation.sample_count == 3

    assert observation.sample_coordinates_normalized.shape == (
        3,
        2,
    )
    assert observation.scalar_detail.shape == (
        3,
    )
    assert observation.confidence.shape == (
        3,
    )


def test_exposes_deterministic_pixel_coordinates():
    observation = _observation()

    assert observation.pixel_coordinate(
        20
    ) == pytest.approx(
        (
            0.50 * (1536 - 1),
            0.55 * (1152 - 1),
        )
    )


def test_exposes_values_by_sample_index():
    observation = _observation()

    assert observation.scalar_detail_for_sample(
        20
    ) == pytest.approx(
        -0.05
    )

    assert observation.confidence_for_sample(
        20
    ) == pytest.approx(
        0.8
    )


def test_array_state_is_immutable_snapshot():
    coordinates = np.array(
        [
            [0.2, 0.3],
            [0.7, 0.8],
        ],
        dtype=np.float64,
    )
    detail = np.array(
        [
            0.1,
            -0.1,
        ],
        dtype=np.float64,
    )
    confidence = np.array(
        [
            0.9,
            0.6,
        ],
        dtype=np.float64,
    )

    observation = AtlasCanonicalHeadResidualDetailObservation(
        observation_id="fixture",
        source_view_id="view_a",
        image_width=100,
        image_height=80,
        sample_indices=(
            3,
            7,
        ),
        sample_coordinates_normalized=coordinates,
        scalar_detail=detail,
        confidence=confidence,
    )

    coordinates[0, 0] = 1.0
    detail[0] = 9.0
    confidence[0] = 0.0

    assert observation.sample_coordinates_normalized[
        0,
        0,
    ] == pytest.approx(
        0.2
    )
    assert observation.scalar_detail[
        0
    ] == pytest.approx(
        0.1
    )
    assert observation.confidence[
        0
    ] == pytest.approx(
        0.9
    )

    assert (
        observation.sample_coordinates_normalized
        .flags.writeable
        is False
    )
    assert observation.scalar_detail.flags.writeable is False
    assert observation.confidence.flags.writeable is False

    with pytest.raises(
        FrozenInstanceError
    ):
        observation.observation_id = "changed"


@pytest.mark.parametrize(
    "sample_indices",
    (
        (),
        (1, 1),
        (-1,),
        (True,),
        (1.5,),
    ),
)
def test_rejects_invalid_sample_indices(
    sample_indices,
):
    count = len(
        sample_indices
    )

    with pytest.raises(
        (TypeError, ValueError),
    ):
        AtlasCanonicalHeadResidualDetailObservation(
            observation_id="fixture",
            source_view_id="view",
            image_width=100,
            image_height=80,
            sample_indices=sample_indices,
            sample_coordinates_normalized=np.zeros(
                (
                    count,
                    2,
                ),
                dtype=np.float64,
            ),
            scalar_detail=np.zeros(
                count,
                dtype=np.float64,
            ),
            confidence=np.ones(
                count,
                dtype=np.float64,
            ),
        )


def test_rejects_coordinate_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="sample_coordinates_normalized",
    ):
        AtlasCanonicalHeadResidualDetailObservation(
            observation_id="fixture",
            source_view_id="view",
            image_width=100,
            image_height=80,
            sample_indices=(
                1,
                2,
            ),
            sample_coordinates_normalized=np.zeros(
                (
                    2,
                    3,
                ),
                dtype=np.float64,
            ),
            scalar_detail=np.zeros(
                2,
                dtype=np.float64,
            ),
            confidence=np.ones(
                2,
                dtype=np.float64,
            ),
        )


def test_rejects_coordinates_outside_normalized_image_range():
    with pytest.raises(
        ValueError,
        match="0.0..1.0",
    ):
        AtlasCanonicalHeadResidualDetailObservation(
            observation_id="fixture",
            source_view_id="view",
            image_width=100,
            image_height=80,
            sample_indices=(
                1,
            ),
            sample_coordinates_normalized=np.array(
                [
                    [1.2, 0.5],
                ],
                dtype=np.float64,
            ),
            scalar_detail=np.zeros(
                1,
                dtype=np.float64,
            ),
            confidence=np.ones(
                1,
                dtype=np.float64,
            ),
        )


def test_rejects_nonfinite_scalar_detail():
    with pytest.raises(
        ValueError,
        match="scalar_detail",
    ):
        AtlasCanonicalHeadResidualDetailObservation(
            observation_id="fixture",
            source_view_id="view",
            image_width=100,
            image_height=80,
            sample_indices=(
                1,
            ),
            sample_coordinates_normalized=np.array(
                [
                    [0.5, 0.5],
                ],
                dtype=np.float64,
            ),
            scalar_detail=np.array(
                [
                    np.nan,
                ],
                dtype=np.float64,
            ),
            confidence=np.ones(
                1,
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "confidence",
    (
        np.array(
            [-0.1],
            dtype=np.float64,
        ),
        np.array(
            [1.1],
            dtype=np.float64,
        ),
        np.array(
            [np.nan],
            dtype=np.float64,
        ),
    ),
)
def test_rejects_invalid_confidence(
    confidence,
):
    with pytest.raises(
        ValueError,
        match="confidence",
    ):
        AtlasCanonicalHeadResidualDetailObservation(
            observation_id="fixture",
            source_view_id="view",
            image_width=100,
            image_height=80,
            sample_indices=(
                1,
            ),
            sample_coordinates_normalized=np.array(
                [
                    [0.5, 0.5],
                ],
                dtype=np.float64,
            ),
            scalar_detail=np.zeros(
                1,
                dtype=np.float64,
            ),
            confidence=confidence,
        )


def test_unknown_sample_lookup_raises_key_error():
    observation = _observation()

    with pytest.raises(
        KeyError
    ):
        observation.scalar_detail_for_sample(
            999
        )


def test_contract_does_not_claim_provider_canonical_vertex_or_decision():
    observation = _observation()

    assert not hasattr(
        observation,
        "provider_id",
    )
    assert not hasattr(
        observation,
        "canonical_vertex_indices",
    )
    assert not hasattr(
        observation,
        "dense_correspondence",
    )
    assert not hasattr(
        observation,
        "camera",
    )
    assert not hasattr(
        observation,
        "pose",
    )
    assert not hasattr(
        observation,
        "likeness_score",
    )
    assert not hasattr(
        observation,
        "phase_9_authorized",
    )
