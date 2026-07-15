import numpy as np
import pytest

from CORE.atlas_relief_pipeline import (
    AtlasReliefPipeline,
)


def _values():
    return np.array(
        [
            [10.0, 20.0, 30.0],
            [40.0, 50.0, 60.0],
            [70.0, 80.0, 90.0],
        ],
        dtype=np.float64,
    )


def test_pipeline_builds_complete_result():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
    )

    assert result["type"] == (
        "relief_pipeline_result"
    )
    assert result["mesh"]["type"] == (
        "relief_mesh"
    )
    assert result[
        "quality_report"
    ]["is_printable_topology"] is True


def test_pipeline_normalizes_input():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
    )

    normalized = result[
        "normalized_height_map"
    ]

    assert normalized.min() == pytest.approx(
        0.0
    )
    assert normalized.max() == pytest.approx(
        1.0
    )


def test_pipeline_supports_resampling():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
        target_rows=7,
        target_columns=9,
    )

    assert result[
        "processed_height_map"
    ].shape == (7, 9)

    assert result["mesh"]["row_count"] == 7
    assert result["mesh"]["column_count"] == 9


def test_pipeline_supports_smoothing():
    values = np.zeros(
        (7, 7),
        dtype=np.float64,
    )
    values[3, 3] = 1.0

    result = AtlasReliefPipeline.build(
        values,
        width_mm=20.0,
        depth_mm=20.0,
        smoothing_sigma=1.0,
        smoothing_radius=3,
    )

    processed = result[
        "processed_height_map"
    ]

    assert 0.0 < processed[3, 3] < 1.0
    assert processed[3, 2] > 0.0


def test_pipeline_supports_inversion():
    normal = AtlasReliefPipeline.build(
        _values(),
        width_mm=10.0,
        depth_mm=10.0,
    )

    inverted = AtlasReliefPipeline.build(
        _values(),
        width_mm=10.0,
        depth_mm=10.0,
        invert=True,
    )

    assert np.allclose(
        inverted["normalized_height_map"],
        1.0 - normal[
            "normalized_height_map"
        ],
    )


def test_pipeline_preserves_physical_dimensions():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=42.0,
        depth_mm=27.0,
        base_thickness_mm=1.2,
        relief_height_mm=3.5,
        origin_x=4.0,
        origin_y=6.0,
        origin_z=2.0,
    )

    report = result["quality_report"]

    assert report["width_mm"] == pytest.approx(
        42.0
    )
    assert report["depth_mm"] == pytest.approx(
        27.0
    )
    assert report[
        "total_height_mm"
    ] == pytest.approx(4.7)


def test_pipeline_is_deterministic():
    arguments = {
        "values": _values(),
        "width_mm": 30.0,
        "depth_mm": 20.0,
        "target_rows": 8,
        "target_columns": 10,
        "smoothing_sigma": 0.8,
        "smoothing_radius": 2,
    }

    first = AtlasReliefPipeline.build(
        **arguments
    )
    second = AtlasReliefPipeline.build(
        **arguments
    )

    assert np.array_equal(
        first["processed_height_map"],
        second["processed_height_map"],
    )

    assert (
        first["mesh"]["triangles"]
        == second["mesh"]["triangles"]
    )

    assert (
        first["quality_report"]
        == second["quality_report"]
    )


@pytest.mark.parametrize(
    "target_rows,target_columns",
    [
        (5, None),
        (None, 5),
    ],
)
def test_pipeline_requires_complete_target_size(
    target_rows,
    target_columns,
):
    with pytest.raises(ValueError):
        AtlasReliefPipeline.build(
            _values(),
            width_mm=10.0,
            depth_mm=10.0,
            target_rows=target_rows,
            target_columns=target_columns,
        )


def test_pipeline_rejects_radius_without_sigma():
    with pytest.raises(ValueError):
        AtlasReliefPipeline.build(
            _values(),
            width_mm=10.0,
            depth_mm=10.0,
            smoothing_radius=2,
        )
