from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_dense_image_surface_evidence_producer import (
    AtlasPortraitDenseImageSurfaceEvidenceProducer,
)


def test_producer_samples_real_image_at_projected_vertices():
    image = np.zeros(
        (6, 8, 3),
        dtype=np.float64,
    )

    image[2, 3] = [0.2, 0.4, 0.6]
    image[4, 5] = [0.8, 0.7, 0.5]

    result = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer.build(
            evidence_id="real-view",
            source_view_id="front",
            source_rgb=image,
            canonical_vertex_indices=np.array(
                [10, 20],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [
                    [3.0, 2.0],
                    [5.0, 4.0],
                ],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [
                    [0.1, 0.3, 0.5],
                    [0.7, 0.6, 0.4],
                ],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0, 0.5],
                dtype=np.float64,
            ),
        )
    )

    assert result.sample_count == 2
    assert result.image_width == 8
    assert result.image_height == 6

    np.testing.assert_allclose(
        result.observed_rgb,
        np.array(
            [
                [0.2, 0.4, 0.6],
                [0.8, 0.7, 0.5],
            ]
        ),
    )


def test_producer_bilinearly_samples_subpixel_projection():
    image = np.zeros(
        (2, 2, 3),
        dtype=np.float64,
    )

    image[0, 0] = [0.0, 0.0, 0.0]
    image[0, 1] = [1.0, 0.0, 0.0]
    image[1, 0] = [0.0, 1.0, 0.0]
    image[1, 1] = [1.0, 1.0, 0.0]

    result = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer.build(
            evidence_id="bilinear",
            source_view_id="front",
            source_rgb=image,
            canonical_vertex_indices=np.array(
                [4],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[0.5, 0.5]],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [[0.5, 0.5, 0.0]],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0],
                dtype=np.float64,
            ),
        )
    )

    np.testing.assert_allclose(
        result.observed_rgb,
        [[0.5, 0.5, 0.0]],
        atol=1e-12,
    )


def test_producer_rejects_samples_outside_image():
    image = np.zeros(
        (6, 8, 3),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="inside source image",
    ):
        AtlasPortraitDenseImageSurfaceEvidenceProducer.build(
            evidence_id="outside",
            source_view_id="front",
            source_rgb=image,
            canonical_vertex_indices=np.array(
                [1],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[8.0, 2.0]],
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


def test_photometric_residual_is_confidence_weighted_rgb_difference():
    image = np.zeros(
        (5, 5, 3),
        dtype=np.float64,
    )

    image[1, 1] = [0.4, 0.5, 0.6]
    image[2, 2] = [0.8, 0.7, 0.6]

    evidence = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer.build(
            evidence_id="residual",
            source_view_id="front",
            source_rgb=image,
            canonical_vertex_indices=np.array(
                [1, 2],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [
                    [1.0, 1.0],
                    [2.0, 2.0],
                ],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [
                    [0.1, 0.2, 0.3],
                    [0.4, 0.3, 0.2],
                ],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0, 0.25],
                dtype=np.float64,
            ),
        )
    )

    residual = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer
        .photometric_residual(
            evidence
        )
    )

    expected = np.concatenate(
        [
            np.sqrt(1.0)
            * np.array([0.3, 0.3, 0.3]),
            np.sqrt(0.25)
            * np.array([0.4, 0.4, 0.4]),
        ]
    )

    np.testing.assert_allclose(
        residual,
        expected,
        atol=1e-12,
    )


def test_photometric_residual_is_deterministic_flat_vector():
    image = np.full(
        (3, 3, 3),
        0.5,
        dtype=np.float64,
    )

    evidence = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer.build(
            evidence_id="deterministic",
            source_view_id="front",
            source_rgb=image,
            canonical_vertex_indices=np.array(
                [1],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[1.0, 1.0]],
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
    )

    first = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer
        .photometric_residual(
            evidence
        )
    )

    second = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer
        .photometric_residual(
            evidence
        )
    )

    assert first.shape == (3,)
    np.testing.assert_array_equal(
        first,
        second,
    )


def test_producer_does_not_claim_anatomical_homology_or_identity_ownership():
    image = np.full(
        (3, 3, 3),
        0.5,
        dtype=np.float64,
    )

    result = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer.build(
            evidence_id="epistemic-boundary",
            source_view_id="front",
            source_rgb=image,
            canonical_vertex_indices=np.array(
                [1],
                dtype=np.int64,
            ),
            projected_xy=np.array(
                [[1.0, 1.0]],
                dtype=np.float64,
            ),
            rendered_rgb=np.array(
                [[0.5, 0.5, 0.5]],
                dtype=np.float64,
            ),
            confidence=np.array(
                [1.0],
                dtype=np.float64,
            ),
        )
    )

    assert (
        result.evidence_class
        == "IMAGE_CONDITIONED_DENSE_SURFACE_EVIDENCE"
    )
    assert result.anatomical_homology_claim is False
    assert result.canonical_identity_owner is False
    assert result.mutates_canonical_identity is False


def test_visibility_mask_uses_reciprocal_depth_to_keep_nearest_surface():
    projected_xy = np.array(
        [
            [1.0, 1.0],
            [4.0, 1.0],
            [1.0, 4.0],
            [1.0, 1.0],
            [4.0, 1.0],
            [1.0, 4.0],
        ],
        dtype=np.float64,
    )

    # Two exactly overlapping projected triangles.
    # First triangle is nearer to the camera (Z=2);
    # second triangle is farther away (Z=4).
    camera_z = np.array(
        [2.0, 2.0, 2.0, 4.0, 4.0, 4.0],
        dtype=np.float64,
    )

    faces = np.array(
        [
            [0, 1, 2],
            [3, 4, 5],
        ],
        dtype=np.int64,
    )

    visible = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer
        .rasterized_vertex_visibility_mask(
            projected_xy=projected_xy,
            camera_z=camera_z,
            faces=faces,
            image_width=6,
            image_height=6,
        )
    )

    assert visible.shape == (6,)
    assert visible.dtype == np.bool_

    assert np.all(
        visible[[0, 1, 2]]
    )
    assert not np.any(
        visible[[3, 4, 5]]
    )


def test_visibility_mask_rejects_nonpositive_camera_depth():
    with pytest.raises(
        ValueError,
        match="camera_z",
    ):
        (
            AtlasPortraitDenseImageSurfaceEvidenceProducer
            .rasterized_vertex_visibility_mask(
                projected_xy=np.array(
                    [
                        [1.0, 1.0],
                        [2.0, 1.0],
                        [1.0, 2.0],
                    ],
                    dtype=np.float64,
                ),
                camera_z=np.array(
                    [2.0, 0.0, 2.0],
                    dtype=np.float64,
                ),
                faces=np.array(
                    [[0, 1, 2]],
                    dtype=np.int64,
                ),
                image_width=4,
                image_height=4,
            )
        )


def test_visibility_mask_combines_raster_visibility_with_image_support_mask():
    projected_xy = np.array(
        [
            [1.0, 1.0],
            [4.0, 1.0],
            [1.0, 4.0],
        ],
        dtype=np.float64,
    )

    support_mask = np.zeros(
        (6, 6),
        dtype=bool,
    )

    support_mask[1, 1] = True
    support_mask[1, 4] = False
    support_mask[4, 1] = True

    visible = (
        AtlasPortraitDenseImageSurfaceEvidenceProducer
        .rasterized_vertex_visibility_mask(
            projected_xy=projected_xy,
            camera_z=np.array(
                [2.0, 2.0, 2.0],
                dtype=np.float64,
            ),
            faces=np.array(
                [[0, 1, 2]],
                dtype=np.int64,
            ),
            image_width=6,
            image_height=6,
            image_support_mask=support_mask,
        )
    )

    np.testing.assert_array_equal(
        visible,
        np.array(
            [True, False, True],
            dtype=bool,
        ),
    )


def test_visibility_mask_does_not_mutate_inputs():
    projected_xy = np.array(
        [
            [1.0, 1.0],
            [3.0, 1.0],
            [1.0, 3.0],
        ],
        dtype=np.float64,
    )

    camera_z = np.array(
        [2.0, 2.0, 2.0],
        dtype=np.float64,
    )

    faces = np.array(
        [[0, 1, 2]],
        dtype=np.int64,
    )

    projected_before = projected_xy.copy()
    depth_before = camera_z.copy()
    faces_before = faces.copy()

    (
        AtlasPortraitDenseImageSurfaceEvidenceProducer
        .rasterized_vertex_visibility_mask(
            projected_xy=projected_xy,
            camera_z=camera_z,
            faces=faces,
            image_width=5,
            image_height=5,
        )
    )

    np.testing.assert_array_equal(
        projected_xy,
        projected_before,
    )
    np.testing.assert_array_equal(
        camera_z,
        depth_before,
    )
    np.testing.assert_array_equal(
        faces,
        faces_before,
    )


def test_candidate_sensitive_pairwise_photometric_residual_reprojects_resamples_and_preserves_cardinality():
    producer = AtlasPortraitDenseImageSurfaceEvidenceProducer

    source_a = np.zeros((6, 6, 3), dtype=np.float64)
    source_b = np.zeros((6, 6, 3), dtype=np.float64)

    for y in range(6):
        for x in range(6):
            source_a[y, x] = [x / 10.0, y / 10.0, 0.1]
            source_b[y, x] = [y / 10.0, x / 10.0, 0.2]

    canonical_vertex_indices = np.array(
        [0, 1, 2],
        dtype=np.int64,
    )

    baseline_confidence = np.array(
        [1.0, 0.64, 0.25],
        dtype=np.float64,
    )

    faces = np.array(
        [[0, 1, 2]],
        dtype=np.int64,
    )

    projected_a = np.array(
        [
            [1.0, 1.0],
            [4.0, 1.0],
            [1.0, 4.0],
        ],
        dtype=np.float64,
    )

    projected_b_first = np.array(
        [
            [1.0, 1.0],
            [4.0, 1.0],
            [1.0, 4.0],
        ],
        dtype=np.float64,
    )

    projected_b_second = projected_b_first.copy()
    projected_b_second[0] = [2.0, 1.0]

    camera_z = np.array(
        [2.0, 2.0, 2.0],
        dtype=np.float64,
    )

    support_a = np.ones((6, 6), dtype=bool)
    support_b = np.ones((6, 6), dtype=bool)

    # The third accepted baseline-supported sample becomes
    # candidate-invisible in view B.  D2 must not silently
    # convert that sample into a zero residual.
    support_b[4, 1] = False

    first = producer.candidate_sensitive_pairwise_photometric_residual(
        source_rgb_a=source_a,
        source_rgb_b=source_b,
        canonical_vertex_indices=canonical_vertex_indices,
        baseline_confidence=baseline_confidence,
        candidate_projected_xy_a=projected_a,
        candidate_camera_z_a=camera_z,
        candidate_projected_xy_b=projected_b_first,
        candidate_camera_z_b=camera_z,
        faces=faces,
        image_support_mask_a=support_a,
        image_support_mask_b=support_b,
    )

    second = producer.candidate_sensitive_pairwise_photometric_residual(
        source_rgb_a=source_a,
        source_rgb_b=source_b,
        canonical_vertex_indices=canonical_vertex_indices,
        baseline_confidence=baseline_confidence,
        candidate_projected_xy_a=projected_a,
        candidate_camera_z_a=camera_z,
        candidate_projected_xy_b=projected_b_second,
        candidate_camera_z_b=camera_z,
        faces=faces,
        image_support_mask_a=support_a,
        image_support_mask_b=support_b,
    )

    assert first.shape == (canonical_vertex_indices.size * 3,)
    assert second.shape == first.shape

    # Candidate reprojection + RGB resampling must be live on
    # every evaluation rather than reusing persisted D1 RGB.
    assert not np.array_equal(first, second)

    # The accepted support cardinality is frozen.  Candidate
    # invisibility is therefore not permitted to erase the
    # baseline-supported third sample with three zero entries.
    invisible_slice = first[6:9]
    assert np.all(np.isfinite(invisible_slice))
    assert np.any(np.abs(invisible_slice) > 0.0)


def test_candidate_sensitive_pairwise_residual_recomputes_self_occlusion_each_evaluation():
    producer = AtlasPortraitDenseImageSurfaceEvidenceProducer

    source_a = np.zeros((6, 6, 3), dtype=np.float64)
    source_b = np.zeros((6, 6, 3), dtype=np.float64)

    # Accepted vertex 0 samples identical RGB in both views
    # whenever it is actually visible.
    source_a[1, 1] = [0.4, 0.4, 0.4]
    source_b[1, 1] = [0.4, 0.4, 0.4]

    # Two triangles occupy the same image footprint.
    projected = np.array(
        [
            [1.0, 1.0],
            [4.0, 1.0],
            [1.0, 4.0],
            [1.0, 1.0],
            [4.0, 1.0],
            [1.0, 4.0],
        ],
        dtype=np.float64,
    )

    faces = np.array(
        [
            [0, 1, 2],
            [3, 4, 5],
        ],
        dtype=np.int64,
    )

    depth_a = np.array(
        [2.0, 2.0, 2.0, 4.0, 4.0, 4.0],
        dtype=np.float64,
    )

    # First B evaluation: accepted triangle is behind the
    # second triangle, therefore candidate-invisible.
    depth_b_occluded = np.array(
        [4.0, 4.0, 4.0, 2.0, 2.0, 2.0],
        dtype=np.float64,
    )

    # Second B evaluation: candidate geometry changes and the
    # accepted triangle becomes the nearest visible surface.
    depth_b_visible = np.array(
        [2.0, 2.0, 2.0, 4.0, 4.0, 4.0],
        dtype=np.float64,
    )

    kwargs = dict(
        source_rgb_a=source_a,
        source_rgb_b=source_b,
        canonical_vertex_indices=np.array(
            [0],
            dtype=np.int64,
        ),
        baseline_confidence=np.array(
            [1.0],
            dtype=np.float64,
        ),
        candidate_projected_xy_a=projected,
        candidate_camera_z_a=depth_a,
        candidate_projected_xy_b=projected,
        faces=faces,
    )

    occluded = (
        producer
        .candidate_sensitive_pairwise_photometric_residual(
            **kwargs,
            candidate_camera_z_b=depth_b_occluded,
        )
    )

    visible = (
        producer
        .candidate_sensitive_pairwise_photometric_residual(
            **kwargs,
            candidate_camera_z_b=depth_b_visible,
        )
    )

    assert occluded.shape == (3,)
    assert visible.shape == (3,)

    # Occlusion must not delete the frozen accepted sample.
    np.testing.assert_allclose(
        occluded,
        np.ones(3),
        atol=1e-12,
    )

    # Once candidate visibility changes, the same residual
    # slots are recomputed from live image samples.
    np.testing.assert_allclose(
        visible,
        np.zeros(3),
        atol=1e-12,
    )

    assert not np.array_equal(
        occluded,
        visible,
    )
