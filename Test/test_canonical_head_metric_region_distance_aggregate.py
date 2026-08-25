import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
    AtlasCanonicalHeadMetricRegionDistanceAggregate,
)


def test_aggregates_distances_for_named_regions():
    distances = np.asarray(
        [0.5, 1.0, 2.0, 4.0, 8.0],
        dtype=np.float64,
    )

    result = AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
        distances_mm=distances,
        region_sample_indices={
            "nose": (1, 2),
            "jaw_chin": (3, 4),
        },
    )

    nose = result.region("nose")
    jaw_chin = result.region("jaw_chin")

    assert nose.sample_count == 2
    assert nose.mean_distance_mm == pytest.approx(1.5)
    assert nose.max_distance_mm == pytest.approx(2.0)

    assert jaw_chin.sample_count == 2
    assert jaw_chin.mean_distance_mm == pytest.approx(6.0)
    assert jaw_chin.max_distance_mm == pytest.approx(8.0)


def test_normalizes_region_names():
    result = AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
        distances_mm=np.asarray(
            [1.0, 2.0],
            dtype=np.float64,
        ),
        region_sample_indices={
            "Jaw Chin": (0, 1),
        },
    )

    assert result.region_names == ("jaw_chin",)
    assert result.region(" jaw   chin ").sample_count == 2


def test_rejects_out_of_bounds_region_sample_indices():
    with pytest.raises(
        ValueError,
        match="region_sample_indices",
    ):
        AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
            distances_mm=np.asarray(
                [1.0, 2.0],
                dtype=np.float64,
            ),
            region_sample_indices={
                "nose": (0, 2),
            },
        )


def test_rejects_empty_regions():
    with pytest.raises(
        ValueError,
        match="region_sample_indices",
    ):
        AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
            distances_mm=np.asarray(
                [1.0, 2.0],
                dtype=np.float64,
            ),
            region_sample_indices={},
        )


def test_rejects_empty_region_sample_set():
    with pytest.raises(
        ValueError,
        match="region_sample_indices",
    ):
        AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
            distances_mm=np.asarray(
                [1.0, 2.0],
                dtype=np.float64,
            ),
            region_sample_indices={
                "nose": (),
            },
        )
