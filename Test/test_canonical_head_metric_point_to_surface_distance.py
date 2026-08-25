import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_point_to_surface_distance import (
    AtlasCanonicalHeadMetricPointToSurfaceDistance,
)


def test_measures_exact_distance_to_triangle_surface():
    target_vertices = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [0.0, 10.0, 0.0],
        ],
        dtype=np.float64,
    )
    target_faces = (
        (0, 1, 2),
    )
    source_points = np.asarray(
        [
            [2.0, 2.0, 3.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = AtlasCanonicalHeadMetricPointToSurfaceDistance.evaluate(
        source_points=source_points,
        target_vertices=target_vertices,
        target_faces=target_faces,
    )

    np.testing.assert_allclose(
        result.distances_mm,
        np.asarray([3.0, 0.0]),
        atol=1e-9,
    )
    assert result.mean_distance_mm == pytest.approx(1.5)
    assert result.max_distance_mm == pytest.approx(3.0)


def test_handles_closest_point_on_triangle_edge():
    result = AtlasCanonicalHeadMetricPointToSurfaceDistance.evaluate(
        source_points=np.asarray(
            [[6.0, 6.0, 0.0]],
            dtype=np.float64,
        ),
        target_vertices=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [10.0, 0.0, 0.0],
                [0.0, 10.0, 0.0],
            ],
            dtype=np.float64,
        ),
        target_faces=((0, 1, 2),),
    )

    assert result.distances_mm[0] == pytest.approx(
        np.sqrt(2.0),
        abs=1e-9,
    )


def test_rejects_nonfinite_source_points():
    with pytest.raises(
        ValueError,
        match="source_points",
    ):
        AtlasCanonicalHeadMetricPointToSurfaceDistance.evaluate(
            source_points=np.asarray(
                [[0.0, np.nan, 0.0]]
            ),
            target_vertices=np.asarray(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                ]
            ),
            target_faces=((0, 1, 2),),
        )


def test_rejects_invalid_target_face_indices():
    with pytest.raises(
        ValueError,
        match="target_faces",
    ):
        AtlasCanonicalHeadMetricPointToSurfaceDistance.evaluate(
            source_points=np.asarray(
                [[0.0, 0.0, 0.0]]
            ),
            target_vertices=np.asarray(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                ]
            ),
            target_faces=((0, 1, 3),),
        )
