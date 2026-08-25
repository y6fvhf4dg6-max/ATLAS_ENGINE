import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_rigid_alignment import (
    AtlasCanonicalHeadMetricRigidAlignment,
)


def test_recovers_exact_rigid_alignment_without_scaling():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [0.0, 20.0, 0.0],
            [0.0, 0.0, 30.0],
        ],
        dtype=np.float64,
    )

    rotation = np.asarray(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    translation = np.asarray(
        [100.0, -50.0, 25.0],
        dtype=np.float64,
    )

    target = source @ rotation.T + translation

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=target,
    )

    np.testing.assert_allclose(
        result.aligned_source_points,
        target,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        result.rotation,
        rotation,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        result.translation,
        translation,
        atol=1e-9,
    )
    assert result.scale_factor == pytest.approx(1.0)


def test_does_not_mutate_source_or_target_points():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )
    target = source + np.asarray(
        [4.0, 5.0, 6.0]
    )

    source_before = source.copy()
    target_before = target.copy()

    AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=target,
    )

    np.testing.assert_array_equal(
        source,
        source_before,
    )
    np.testing.assert_array_equal(
        target,
        target_before,
    )


def test_rejects_mismatched_point_counts():
    with pytest.raises(
        ValueError,
        match="same shape",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=np.zeros((3, 3)),
            target_points=np.zeros((4, 3)),
        )


def test_rejects_nonfinite_points():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, np.nan, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=source,
            target_points=np.zeros((3, 3)),
        )
