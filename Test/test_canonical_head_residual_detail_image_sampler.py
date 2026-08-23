import numpy as np
import pytest

from CORE.atlas_canonical_head_residual_detail_image_sampler import (
    AtlasCanonicalHeadResidualDetailImageSampler,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)


def _scalar_field():
    return np.array(
        [
            [0.00, 0.10, 0.20],
            [0.30, 0.40, 0.50],
            [0.60, 0.70, 0.80],
        ],
        dtype=np.float64,
    )


def _confidence_field():
    return np.array(
        [
            [1.00, 0.90, 0.80],
            [0.70, 0.60, 0.50],
            [0.40, 0.30, 0.20],
        ],
        dtype=np.float64,
    )


def test_builds_residual_detail_observation_from_image_fields():
    result = AtlasCanonicalHeadResidualDetailImageSampler.sample(
        observation_id="subject-01-front-detail",
        source_view_id="subject-01-front",
        scalar_detail_field=_scalar_field(),
        confidence_field=_confidence_field(),
        sample_indices=(10, 20, 30),
        sample_coordinates_normalized=np.array(
            [
                [0.0, 0.0],
                [0.5, 0.5],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        ),
    )

    assert isinstance(
        result,
        AtlasCanonicalHeadResidualDetailObservation,
    )
    assert result.observation_id == "subject-01-front-detail"
    assert result.source_view_id == "subject-01-front"
    assert result.image_width == 3
    assert result.image_height == 3
    assert result.sample_indices == (
        10,
        20,
        30,
    )


def test_samples_scalar_detail_bilinearly_in_normalized_image_space():
    result = AtlasCanonicalHeadResidualDetailImageSampler.sample(
        observation_id="fixture",
        source_view_id="view-a",
        scalar_detail_field=_scalar_field(),
        confidence_field=_confidence_field(),
        sample_indices=(0, 1, 2, 3),
        sample_coordinates_normalized=np.array(
            [
                [0.0, 0.0],
                [0.5, 0.5],
                [1.0, 1.0],
                [0.25, 0.25],
            ],
            dtype=np.float64,
        ),
    )

    assert result.scalar_detail == pytest.approx(
        (
            0.00,
            0.40,
            0.80,
            0.20,
        )
    )


def test_samples_confidence_as_separate_bilinear_channel():
    result = AtlasCanonicalHeadResidualDetailImageSampler.sample(
        observation_id="fixture",
        source_view_id="view-a",
        scalar_detail_field=_scalar_field(),
        confidence_field=_confidence_field(),
        sample_indices=(0, 1, 2, 3),
        sample_coordinates_normalized=np.array(
            [
                [0.0, 0.0],
                [0.5, 0.5],
                [1.0, 1.0],
                [0.25, 0.25],
            ],
            dtype=np.float64,
        ),
    )

    assert result.confidence == pytest.approx(
        (
            1.00,
            0.60,
            0.20,
            0.80,
        )
    )


def test_sampling_does_not_weight_scalar_detail_by_confidence():
    scalar = np.full(
        (3, 3),
        0.5,
        dtype=np.float64,
    )
    confidence = np.zeros(
        (3, 3),
        dtype=np.float64,
    )

    result = AtlasCanonicalHeadResidualDetailImageSampler.sample(
        observation_id="fixture",
        source_view_id="view-a",
        scalar_detail_field=scalar,
        confidence_field=confidence,
        sample_indices=(0,),
        sample_coordinates_normalized=np.array(
            [[0.5, 0.5]],
            dtype=np.float64,
        ),
    )

    assert result.scalar_detail[0] == pytest.approx(
        0.5
    )
    assert result.confidence[0] == pytest.approx(
        0.0
    )


def test_rejects_mismatched_field_shapes():
    with pytest.raises(
        ValueError,
        match="confidence_field shape",
    ):
        AtlasCanonicalHeadResidualDetailImageSampler.sample(
            observation_id="fixture",
            source_view_id="view-a",
            scalar_detail_field=np.zeros(
                (3, 3),
                dtype=np.float64,
            ),
            confidence_field=np.zeros(
                (4, 3),
                dtype=np.float64,
            ),
            sample_indices=(0,),
            sample_coordinates_normalized=np.array(
                [[0.5, 0.5]],
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "field_name,field",
    (
        (
            "scalar_detail_field",
            np.array(
                [[0.0, np.nan]],
                dtype=np.float64,
            ),
        ),
        (
            "confidence_field",
            np.array(
                [[1.0, np.inf]],
                dtype=np.float64,
            ),
        ),
    ),
)
def test_rejects_nonfinite_fields(
    field_name,
    field,
):
    arguments = {
        "observation_id": "fixture",
        "source_view_id": "view-a",
        "scalar_detail_field": np.zeros(
            (1, 2),
            dtype=np.float64,
        ),
        "confidence_field": np.ones(
            (1, 2),
            dtype=np.float64,
        ),
        "sample_indices": (0,),
        "sample_coordinates_normalized": np.array(
            [[0.5, 0.0]],
            dtype=np.float64,
        ),
    }
    arguments[field_name] = field

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasCanonicalHeadResidualDetailImageSampler.sample(
            **arguments
        )


def test_rejects_confidence_outside_unit_interval():
    confidence = np.ones(
        (2, 2),
        dtype=np.float64,
    )
    confidence[0, 0] = 1.1

    with pytest.raises(
        ValueError,
        match="confidence_field",
    ):
        AtlasCanonicalHeadResidualDetailImageSampler.sample(
            observation_id="fixture",
            source_view_id="view-a",
            scalar_detail_field=np.zeros(
                (2, 2),
                dtype=np.float64,
            ),
            confidence_field=confidence,
            sample_indices=(0,),
            sample_coordinates_normalized=np.array(
                [[0.5, 0.5]],
                dtype=np.float64,
            ),
        )


def test_rejects_sample_count_mismatch():
    with pytest.raises(
        ValueError,
        match="sample_coordinates_normalized",
    ):
        AtlasCanonicalHeadResidualDetailImageSampler.sample(
            observation_id="fixture",
            source_view_id="view-a",
            scalar_detail_field=_scalar_field(),
            confidence_field=_confidence_field(),
            sample_indices=(
                0,
                1,
            ),
            sample_coordinates_normalized=np.array(
                [[0.5, 0.5]],
                dtype=np.float64,
            ),
        )


def test_boundary_does_not_claim_projection_visibility_or_canonical_mapping():
    result = AtlasCanonicalHeadResidualDetailImageSampler.sample(
        observation_id="fixture",
        source_view_id="view-a",
        scalar_detail_field=_scalar_field(),
        confidence_field=_confidence_field(),
        sample_indices=(0,),
        sample_coordinates_normalized=np.array(
            [[0.5, 0.5]],
            dtype=np.float64,
        ),
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
        "visibility",
    )
    assert not hasattr(
        result,
        "occlusion",
    )
    assert not hasattr(
        result,
        "correspondence",
    )
    assert not hasattr(
        result,
        "canonical_vertex_indices",
    )
    assert not hasattr(
        result,
        "bounded_amplitude",
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
