import numpy as np
import pytest

from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_residual_detail_scale_normalizer import (
    AtlasCanonicalHeadResidualDetailScaleNormalizer,
)


def _observation(
    *,
    scalar_detail=(2.0, -4.0, 1.0),
):
    return AtlasCanonicalHeadResidualDetailObservation(
        observation_id="subject-01-front-detail",
        source_view_id="subject-01-front",
        image_width=1200,
        image_height=900,
        sample_indices=(10, 20, 30),
        sample_coordinates_normalized=np.array(
            [
                [0.25, 0.30],
                [0.50, 0.40],
                [0.75, 0.60],
            ],
            dtype=np.float64,
        ),
        scalar_detail=np.asarray(
            scalar_detail,
            dtype=np.float64,
        ),
        confidence=np.array(
            [1.0, 0.5, 0.25],
            dtype=np.float64,
        ),
    )


def test_maps_image_space_detail_into_canonical_reference_scale():
    result = AtlasCanonicalHeadResidualDetailScaleNormalizer.normalize(
        observation=_observation(),
        image_reference_span_px=200.0,
        canonical_reference_span=0.20,
    )

    assert result.scale_factor == pytest.approx(
        0.001
    )
    assert result.observation.scalar_detail == pytest.approx(
        (
            0.002,
            -0.004,
            0.001,
        )
    )


def test_is_resolution_invariant_when_detail_and_reference_span_scale_together():
    base = (
        AtlasCanonicalHeadResidualDetailScaleNormalizer
        .normalize(
            observation=_observation(
                scalar_detail=(
                    2.0,
                    -4.0,
                    1.0,
                )
            ),
            image_reference_span_px=200.0,
            canonical_reference_span=0.20,
        )
    )

    doubled = (
        AtlasCanonicalHeadResidualDetailScaleNormalizer
        .normalize(
            observation=_observation(
                scalar_detail=(
                    4.0,
                    -8.0,
                    2.0,
                )
            ),
            image_reference_span_px=400.0,
            canonical_reference_span=0.20,
        )
    )

    assert doubled.observation.scalar_detail == pytest.approx(
        base.observation.scalar_detail
    )


def test_preserves_confidence_sample_identity_and_coordinates():
    source = _observation()

    result = AtlasCanonicalHeadResidualDetailScaleNormalizer.normalize(
        observation=source,
        image_reference_span_px=200.0,
        canonical_reference_span=0.20,
    )

    assert result.observation.observation_id == source.observation_id
    assert result.observation.source_view_id == source.source_view_id
    assert result.observation.sample_indices == source.sample_indices
    assert np.array_equal(
        result.observation.sample_coordinates_normalized,
        source.sample_coordinates_normalized,
    )
    assert np.array_equal(
        result.observation.confidence,
        source.confidence,
    )


def test_does_not_mutate_source_observation():
    source = _observation()
    detail_before = source.scalar_detail.copy()
    confidence_before = source.confidence.copy()

    AtlasCanonicalHeadResidualDetailScaleNormalizer.normalize(
        observation=source,
        image_reference_span_px=200.0,
        canonical_reference_span=0.20,
    )

    assert np.array_equal(
        source.scalar_detail,
        detail_before,
    )
    assert np.array_equal(
        source.confidence,
        confidence_before,
    )


@pytest.mark.parametrize(
    ("image_reference_span_px", "canonical_reference_span"),
    (
        (0.0, 0.20),
        (-1.0, 0.20),
        (float("nan"), 0.20),
        (float("inf"), 0.20),
        (200.0, 0.0),
        (200.0, -0.20),
        (200.0, float("nan")),
        (200.0, float("inf")),
    ),
)
def test_rejects_invalid_reference_spans(
    image_reference_span_px,
    canonical_reference_span,
):
    with pytest.raises(ValueError):
        AtlasCanonicalHeadResidualDetailScaleNormalizer.normalize(
            observation=_observation(),
            image_reference_span_px=image_reference_span_px,
            canonical_reference_span=canonical_reference_span,
        )


def test_rejects_non_observation():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadResidualDetailObservation",
    ):
        AtlasCanonicalHeadResidualDetailScaleNormalizer.normalize(
            observation={},
            image_reference_span_px=200.0,
            canonical_reference_span=0.20,
        )
