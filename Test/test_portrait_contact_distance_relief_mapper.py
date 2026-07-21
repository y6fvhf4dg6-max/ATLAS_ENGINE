import numpy as np
import pytest

from CORE.atlas_portrait_contact_distance_relief_mapper import (
    AtlasPortraitContactDistanceReliefMapper,
)
from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


def _projection_result():
    return AtlasPortraitContactPlaneProjectionResult(
        distance_to_plane=np.array(
            [
                [0.8, 0.4, 0.8],
                [0.7, 0.0, 0.7],
            ],
            dtype=np.float64,
        ),
        contact_plane_z=0.8,
        contact_row=1,
        contact_column=1,
        maximum_distance=0.8,
        source_shape=(2, 3),
        metadata={
            "projection_mode": "frontal_contact_plane",
        },
    )


def test_mapper_returns_float64_relief_height():
    result = AtlasPortraitContactDistanceReliefMapper.map(
        _projection_result(),
    )

    assert result["relief_height"].dtype == np.float64
    assert result["relief_height"].shape == (2, 3)


def test_mapper_inverts_contact_distance_direction():
    result = AtlasPortraitContactDistanceReliefMapper.map(
        _projection_result(),
    )

    expected = np.array(
        [
            [0.0, 0.4, 0.0],
            [0.1, 0.8, 0.1],
        ],
        dtype=np.float64,
    )

    assert result["relief_height"] == pytest.approx(
        expected,
    )


def test_contact_point_becomes_maximum_relief_height():
    projection = _projection_result()

    result = AtlasPortraitContactDistanceReliefMapper.map(
        projection,
    )

    assert result["relief_height"][
        projection.contact_index
    ] == pytest.approx(
        projection.maximum_distance,
    )


def test_farthest_points_become_zero_relief_height():
    result = AtlasPortraitContactDistanceReliefMapper.map(
        _projection_result(),
    )

    assert result["relief_height"][0, 0] == pytest.approx(
        0.0,
    )
    assert result["relief_height"][0, 2] == pytest.approx(
        0.0,
    )


def test_mapper_reports_height_range():
    result = AtlasPortraitContactDistanceReliefMapper.map(
        _projection_result(),
    )

    assert result["minimum_relief_height"] == pytest.approx(
        0.0,
    )
    assert result["maximum_relief_height"] == pytest.approx(
        0.8,
    )


def test_mapper_records_deterministic_metadata():
    result = AtlasPortraitContactDistanceReliefMapper.map(
        _projection_result(),
    )

    assert result["type"] == (
        "portrait_contact_distance_relief_mapping"
    )
    assert result["mapping_mode"] == (
        "maximum_distance_minus_distance"
    )
    assert result["source_shape"] == (2, 3)


def test_mapper_does_not_modify_projection_result():
    projection = _projection_result()

    original = projection.distance_to_plane.copy()

    AtlasPortraitContactDistanceReliefMapper.map(
        projection,
    )

    assert projection.distance_to_plane == pytest.approx(
        original,
    )


def test_mapper_is_deterministic():
    projection = _projection_result()

    first = AtlasPortraitContactDistanceReliefMapper.map(
        projection,
    )
    second = AtlasPortraitContactDistanceReliefMapper.map(
        projection,
    )

    assert first["relief_height"] == pytest.approx(
        second["relief_height"],
    )
    assert first["mapping_mode"] == second["mapping_mode"]
    assert first["source_shape"] == second["source_shape"]


def test_mapper_handles_zero_distance_range():
    projection = AtlasPortraitContactPlaneProjectionResult(
        distance_to_plane=np.zeros(
            (
                2,
                2,
            ),
            dtype=np.float64,
        ),
        contact_plane_z=0.5,
        contact_row=0,
        contact_column=0,
        maximum_distance=0.0,
        source_shape=(2, 2),
        metadata={
            "projection_mode": "frontal_contact_plane",
        },
    )

    result = AtlasPortraitContactDistanceReliefMapper.map(
        projection,
    )

    assert result["relief_height"] == pytest.approx(
        np.zeros(
            (
                2,
                2,
            ),
            dtype=np.float64,
        )
    )
    assert result["minimum_relief_height"] == pytest.approx(
        0.0,
    )
    assert result["maximum_relief_height"] == pytest.approx(
        0.0,
    )


def test_mapper_rejects_wrong_projection_type():
    with pytest.raises(
        TypeError,
        match="projection",
    ):
        AtlasPortraitContactDistanceReliefMapper.map(
            object(),
        )
