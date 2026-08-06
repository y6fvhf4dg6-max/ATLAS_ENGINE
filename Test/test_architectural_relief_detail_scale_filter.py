from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_architectural_relief_detail_scale_filter import (
    AtlasArchitecturalReliefDetailScaleFilter,
    AtlasArchitecturalReliefDetailScaleProfile,
)


def test_reports_physical_pixel_pitch():
    detail = np.zeros(
        (4, 6),
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefDetailScaleFilter
        .filter(
            detail_map=detail,
            width_mm=6.0,
            depth_mm=4.0,
            profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=1.5,
                    activity_threshold=0.10,
                    minimum_density=0.50,
                )
            ),
        )
    )

    assert result["pixel_pitch_x_mm"] == pytest.approx(
        1.0
    )
    assert result["pixel_pitch_y_mm"] == pytest.approx(
        1.0
    )


def test_culls_component_below_physical_feature_size():
    detail = np.zeros(
        (5, 7),
        dtype=np.float64,
    )
    detail[2, 3] = 0.8

    result = (
        AtlasArchitecturalReliefDetailScaleFilter
        .filter(
            detail_map=detail,
            width_mm=7.0,
            depth_mm=5.0,
            profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=1.5,
                    activity_threshold=0.10,
                    minimum_density=0.50,
                )
            ),
        )
    )

    assert result["retention_map"][2, 3] == 0.0
    assert result["filtered_detail"][2, 3] == 0.0
    assert result["culled_component_count"] == 1
    assert result["retained_component_count"] == 0


def test_retains_long_architectural_line():
    detail = np.zeros(
        (5, 7),
        dtype=np.float64,
    )
    detail[2, 1:5] = 0.6

    result = (
        AtlasArchitecturalReliefDetailScaleFilter
        .filter(
            detail_map=detail,
            width_mm=7.0,
            depth_mm=5.0,
            profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=2.5,
                    activity_threshold=0.10,
                    minimum_density=0.50,
                )
            ),
        )
    )

    np.testing.assert_array_equal(
        result["retention_map"][2, 1:5],
        np.ones(
            4,
            dtype=np.float64,
        ),
    )
    np.testing.assert_allclose(
        result["filtered_detail"][2, 1:5],
        0.6,
    )
    assert result["retained_component_count"] == 1
    assert result["culled_component_count"] == 0


def test_sparse_component_is_removed_by_density_threshold():
    detail = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    detail[1, 1] = 0.7
    detail[1, 2] = 0.7
    detail[2, 2] = 0.7
    detail[3, 2] = 0.7
    detail[3, 3] = 0.7

    result = (
        AtlasArchitecturalReliefDetailScaleFilter
        .filter(
            detail_map=detail,
            width_mm=5.0,
            depth_mm=5.0,
            profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=2.0,
                    activity_threshold=0.10,
                    minimum_density=0.60,
                )
            ),
        )
    )

    assert result["component_reports"][0][
        "density_ratio"
    ] == pytest.approx(
        5.0 / 9.0
    )
    assert result["component_reports"][0][
        "retained"
    ] is False
    assert np.count_nonzero(
        result["filtered_detail"]
    ) == 0


def test_signed_detail_values_are_preserved():
    detail = np.zeros(
        (3, 5),
        dtype=np.float64,
    )
    detail[1, 1:4] = np.array(
        [-0.4, 0.6, -0.8],
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefDetailScaleFilter
        .filter(
            detail_map=detail,
            width_mm=5.0,
            depth_mm=3.0,
            profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=2.0,
                    activity_threshold=0.10,
                    minimum_density=0.50,
                )
            ),
        )
    )

    np.testing.assert_array_equal(
        result["filtered_detail"][1, 1:4],
        detail[1, 1:4],
    )


def test_rejects_non_positive_physical_dimensions():
    with pytest.raises(
        ValueError,
        match="width_mm",
    ):
        AtlasArchitecturalReliefDetailScaleFilter.filter(
            detail_map=np.zeros(
                (2, 2),
                dtype=np.float64,
            ),
            width_mm=0.0,
            depth_mm=2.0,
            profile=(
                AtlasArchitecturalReliefDetailScaleProfile()
            ),
        )


def test_profile_is_immutable():
    profile = (
        AtlasArchitecturalReliefDetailScaleProfile()
    )

    with pytest.raises(FrozenInstanceError):
        profile.minimum_feature_mm = 2.0


@pytest.mark.parametrize(
    "field,value",
    [
        ("minimum_feature_mm", 0.0),
        ("minimum_feature_mm", -0.1),
        ("minimum_feature_mm", float("nan")),
        ("activity_threshold", -0.1),
        ("activity_threshold", float("inf")),
        ("minimum_density", 0.0),
        ("minimum_density", 1.1),
        ("minimum_density", float("nan")),
    ],
)
def test_profile_rejects_invalid_values(
    field,
    value,
):
    kwargs = {
        "minimum_feature_mm": 0.8,
        "activity_threshold": 0.02,
        "minimum_density": 0.25,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=field,
    ):
        AtlasArchitecturalReliefDetailScaleProfile(
            **kwargs
        )


def test_filter_does_not_mutate_input():
    detail = np.array(
        [
            [0.0, 0.2, 0.0],
            [0.0, 0.4, 0.0],
        ],
        dtype=np.float64,
    )
    original = detail.copy()

    AtlasArchitecturalReliefDetailScaleFilter.filter(
        detail_map=detail,
        width_mm=3.0,
        depth_mm=2.0,
        profile=(
            AtlasArchitecturalReliefDetailScaleProfile()
        ),
    )

    np.testing.assert_array_equal(
        detail,
        original,
    )
