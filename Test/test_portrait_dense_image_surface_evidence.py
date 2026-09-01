from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_dense_image_surface_evidence import (
    AtlasPortraitDenseImageSurfaceEvidence,
)


def _make_evidence():
    return AtlasPortraitDenseImageSurfaceEvidence(
        evidence_id="subject-01-turn-left-dense-surface",
        source_view_id="turn_left",
        image_width=1536,
        image_height=1152,
        canonical_vertex_indices=np.array(
            [12, 25, 99],
            dtype=np.int64,
        ),
        projected_xy=np.array(
            [
                [100.0, 200.0],
                [300.5, 400.25],
                [500.0, 600.0],
            ],
            dtype=np.float64,
        ),
        observed_rgb=np.array(
            [
                [0.2, 0.3, 0.4],
                [0.5, 0.6, 0.7],
                [0.8, 0.7, 0.6],
            ],
            dtype=np.float64,
        ),
        rendered_rgb=np.array(
            [
                [0.1, 0.3, 0.5],
                [0.4, 0.6, 0.8],
                [0.9, 0.7, 0.5],
            ],
            dtype=np.float64,
        ),
        confidence=np.array(
            [1.0, 0.5, 0.25],
            dtype=np.float64,
        ),
    )


def test_contract_preserves_dense_image_conditioned_surface_role():
    evidence = _make_evidence()

    assert evidence.evidence_id == (
        "subject-01-turn-left-dense-surface"
    )
    assert evidence.source_view_id == "turn_left"
    assert evidence.sample_count == 3

    assert (
        evidence.evidence_class
        == "IMAGE_CONDITIONED_DENSE_SURFACE_EVIDENCE"
    )
    assert evidence.anatomical_homology_claim is False
    assert evidence.canonical_identity_owner is False
    assert evidence.mutates_canonical_identity is False


def test_contract_is_immutable_and_copies_numeric_inputs():
    projected = np.array(
        [[10.0, 20.0]],
        dtype=np.float64,
    )

    evidence = AtlasPortraitDenseImageSurfaceEvidence(
        evidence_id="immutable",
        source_view_id="front",
        image_width=100,
        image_height=80,
        canonical_vertex_indices=np.array(
            [3],
            dtype=np.int64,
        ),
        projected_xy=projected,
        observed_rgb=np.array(
            [[0.1, 0.2, 0.3]],
            dtype=np.float64,
        ),
        rendered_rgb=np.array(
            [[0.2, 0.3, 0.4]],
            dtype=np.float64,
        ),
        confidence=np.array(
            [1.0],
            dtype=np.float64,
        ),
    )

    projected[0, 0] = 999.0

    assert evidence.projected_xy[0, 0] == 10.0
    assert evidence.projected_xy.flags.writeable is False
    assert evidence.observed_rgb.flags.writeable is False
    assert evidence.rendered_rgb.flags.writeable is False
    assert evidence.confidence.flags.writeable is False
    assert evidence.canonical_vertex_indices.flags.writeable is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("image_width", 0),
        ("image_height", 0),
        ("image_width", -1),
        ("image_height", -1),
    ],
)
def test_contract_rejects_nonpositive_image_dimensions(
    field,
    value,
):
    kwargs = dict(
        evidence_id="bad-size",
        source_view_id="front",
        image_width=100,
        image_height=80,
        canonical_vertex_indices=np.array(
            [1],
            dtype=np.int64,
        ),
        projected_xy=np.array(
            [[1.0, 2.0]],
            dtype=np.float64,
        ),
        observed_rgb=np.array(
            [[0.1, 0.2, 0.3]],
            dtype=np.float64,
        ),
        rendered_rgb=np.array(
            [[0.1, 0.2, 0.3]],
            dtype=np.float64,
        ),
        confidence=np.array(
            [1.0],
            dtype=np.float64,
        ),
    )

    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=field,
    ):
        AtlasPortraitDenseImageSurfaceEvidence(
            **kwargs
        )


def test_contract_rejects_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="sample count",
    ):
        AtlasPortraitDenseImageSurfaceEvidence(
            evidence_id="shape-mismatch",
            source_view_id="front",
            image_width=100,
            image_height=80,
            canonical_vertex_indices=np.array(
                [1, 2],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[1.0, 2.0]],
                dtype=np.float64,
            ),
            observed_rgb=np.array(
                [[0.1, 0.2, 0.3]],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [[0.1, 0.2, 0.3]],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0],
                dtype=np.float64,
            ),
        )


def test_contract_rejects_duplicate_vertex_indices():
    with pytest.raises(
        ValueError,
        match="unique",
    ):
        AtlasPortraitDenseImageSurfaceEvidence(
            evidence_id="duplicate",
            source_view_id="front",
            image_width=100,
            image_height=80,
            canonical_vertex_indices=np.array(
                [2, 2],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [
                    [1.0, 2.0],
                    [3.0, 4.0],
                ],
                dtype=np.float64,
            ),
            observed_rgb=np.array(
                [
                    [0.1, 0.2, 0.3],
                    [0.2, 0.3, 0.4],
                ],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [
                    [0.1, 0.2, 0.3],
                    [0.2, 0.3, 0.4],
                ],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0, 1.0],
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "bad_rgb",
    [
        np.array([[1.1, 0.2, 0.3]]),
        np.array([[-0.1, 0.2, 0.3]]),
        np.array([[np.nan, 0.2, 0.3]]),
    ],
)
def test_contract_rejects_invalid_rgb(bad_rgb):
    with pytest.raises(
        ValueError,
        match="rgb",
    ):
        AtlasPortraitDenseImageSurfaceEvidence(
            evidence_id="bad-rgb",
            source_view_id="front",
            image_width=100,
            image_height=80,
            canonical_vertex_indices=np.array(
                [1],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[1.0, 2.0]],
                dtype=np.float64,
            ),
            observed_rgb=bad_rgb,
            rendered_rgb=np.array(
                [[0.1, 0.2, 0.3]],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0],
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "confidence",
    [
        np.array([-0.1]),
        np.array([1.1]),
        np.array([np.nan]),
    ],
)
def test_contract_rejects_invalid_confidence(
    confidence,
):
    with pytest.raises(
        ValueError,
        match="confidence",
    ):
        AtlasPortraitDenseImageSurfaceEvidence(
            evidence_id="bad-confidence",
            source_view_id="front",
            image_width=100,
            image_height=80,
            canonical_vertex_indices=np.array(
                [1],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[1.0, 2.0]],
                dtype=np.float64,
            ),
            observed_rgb=np.array(
                [[0.1, 0.2, 0.3]],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [[0.1, 0.2, 0.3]],
                dtype=np.float64,
            ),
            confidence=confidence,
        )


def test_contract_rejects_nonfinite_projection():
    with pytest.raises(
        ValueError,
        match="projected_xy",
    ):
        AtlasPortraitDenseImageSurfaceEvidence(
            evidence_id="bad-project",
            source_view_id="front",
            image_width=100,
            image_height=80,
            canonical_vertex_indices=np.array(
                [1],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[np.inf, 2.0]],
                dtype=np.float64,
            ),
            observed_rgb=np.array(
                [[0.1, 0.2, 0.3]],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [[0.1, 0.2, 0.3]],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0],
                dtype=np.float64,
            ),
        )
