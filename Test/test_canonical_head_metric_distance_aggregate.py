import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_distance_aggregate import (
    AtlasCanonicalHeadMetricDistanceAggregate,
)


def test_aggregates_raw_distance_metrics_in_millimetres():
    result = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray(
            [0.0, 1.0, 2.0, 3.0],
            dtype=np.float64,
        )
    )

    assert result.sample_count == 4
    assert result.mean_distance_mm == pytest.approx(1.5)
    assert result.median_distance_mm == pytest.approx(1.5)
    assert result.rmse_distance_mm == pytest.approx(
        np.sqrt(3.5)
    )
    assert result.p95_distance_mm == pytest.approx(
        np.percentile(
            np.asarray([0.0, 1.0, 2.0, 3.0]),
            95.0,
        )
    )
    assert result.max_distance_mm == pytest.approx(3.0)


def test_does_not_mutate_source_distances():
    source = np.asarray(
        [0.5, 1.5, 2.5],
        dtype=np.float64,
    )
    before = source.copy()

    AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=source
    )

    np.testing.assert_array_equal(
        source,
        before,
    )


@pytest.mark.parametrize(
    "distances",
    (
        np.asarray([]),
        np.asarray([1.0, np.nan]),
        np.asarray([1.0, np.inf]),
        np.asarray([1.0, -0.1]),
        np.asarray([[1.0, 2.0]]),
    ),
)
def test_rejects_invalid_distance_arrays(
    distances,
):
    with pytest.raises(ValueError, match="distances_mm"):
        AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
            distances_mm=distances
        )
