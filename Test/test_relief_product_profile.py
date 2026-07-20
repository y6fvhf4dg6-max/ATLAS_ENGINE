import math

import pytest

from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)


def test_profile_preserves_product_settings():
    profile = AtlasReliefProductProfile(
        name="memorial-soft",
        form_sigma=6.0,
        detail_sigma=1.5,
        form_weight=1.0,
        detail_weight=0.30,
        micro_detail_weight=0.05,
        micro_detail_limit=0.03,
        depth_lower_percentile=2.0,
        depth_upper_percentile=98.0,
        depth_gamma=1.10,
        background_depth_range=(0.0, 0.35),
        foreground_depth_range=(0.60, 1.0),
        relief_height_mm=1.80,
        smoothing_sigma=0.60,
        smoothing_radius=2,
    )

    assert profile.name == "memorial-soft"
    assert profile.form_sigma == 6.0
    assert profile.detail_sigma == 1.5
    assert profile.form_weight == 1.0
    assert profile.detail_weight == 0.30
    assert profile.micro_detail_weight == 0.05
    assert profile.micro_detail_limit == 0.03
    assert profile.depth_lower_percentile == 2.0
    assert profile.depth_upper_percentile == 98.0
    assert profile.depth_gamma == 1.10
    assert profile.background_depth_range == (
        0.0,
        0.35,
    )
    assert profile.foreground_depth_range == (
        0.60,
        1.0,
    )
    assert profile.relief_height_mm == 1.80
    assert profile.smoothing_sigma == 0.60
    assert profile.smoothing_radius == 2


def test_profile_converts_numeric_values():
    profile = AtlasReliefProductProfile(
        name="portrait",
        form_sigma=6,
        detail_sigma=2,
        form_weight=1,
        detail_weight=0,
        micro_detail_weight=0,
        micro_detail_limit=0,
        depth_lower_percentile=1,
        depth_upper_percentile=99,
        depth_gamma=1,
        background_depth_range=(0, 0.4),
        foreground_depth_range=(0.6, 1),
        relief_height_mm=2,
        smoothing_sigma=1,
        smoothing_radius=3.0,
    )

    assert profile.form_sigma == 6.0
    assert profile.detail_sigma == 2.0
    assert profile.relief_height_mm == 2.0
    assert profile.smoothing_sigma == 1.0
    assert profile.smoothing_radius == 3


def test_profile_strips_name_whitespace():
    profile = AtlasReliefProductProfile(
        name="  memorial-soft  ",
        form_sigma=6.0,
        detail_sigma=1.5,
    )

    assert profile.name == "memorial-soft"


def test_profile_produces_pipeline_arguments():
    profile = AtlasReliefProductProfile(
        name="caricature",
        form_sigma=5.0,
        detail_sigma=1.25,
        form_weight=1.10,
        detail_weight=0.40,
        micro_detail_weight=0.08,
        micro_detail_limit=0.04,
        depth_lower_percentile=1.5,
        depth_upper_percentile=98.5,
        depth_gamma=0.95,
        background_depth_range=(0.0, 0.30),
        foreground_depth_range=(0.65, 1.0),
        relief_height_mm=2.20,
        smoothing_sigma=0.40,
        smoothing_radius=2,
    )

    assert profile.to_pipeline_kwargs() == {
        "form_sigma": 5.0,
        "detail_sigma": 1.25,
        "form_weight": 1.10,
        "detail_weight": 0.40,
        "micro_detail_weight": 0.08,
        "micro_detail_limit": 0.04,
        "depth_lower_percentile": 1.5,
        "depth_upper_percentile": 98.5,
        "depth_gamma": 0.95,
        "background_depth_range": (
            0.0,
            0.30,
        ),
        "foreground_depth_range": (
            0.65,
            1.0,
        ),
        "relief_height_mm": 2.20,
        "smoothing_sigma": 0.40,
        "smoothing_radius": 2,
    }


def test_profile_pipeline_arguments_exclude_name():
    profile = AtlasReliefProductProfile(
        name="portrait",
        form_sigma=6.0,
        detail_sigma=1.5,
    )

    assert "name" not in profile.to_pipeline_kwargs()


def test_profile_is_immutable():
    profile = AtlasReliefProductProfile(
        name="portrait",
        form_sigma=6.0,
        detail_sigma=1.5,
    )

    with pytest.raises(AttributeError):
        profile.form_sigma = 4.0


@pytest.mark.parametrize(
    "arguments",
    [
        {
            "name": "",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
        },
        {
            "name": "   ",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
        },
        {
            "name": "portrait",
            "form_sigma": 0.0,
            "detail_sigma": 1.5,
        },
        {
            "name": "portrait",
            "form_sigma": math.nan,
            "detail_sigma": 1.5,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": -1.0,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "detail_weight": -0.1,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "micro_detail_limit": 1.1,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "depth_lower_percentile": 99.0,
            "depth_upper_percentile": 99.0,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "depth_gamma": 0.0,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "background_depth_range": (
                0.4,
                0.2,
            ),
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "foreground_depth_range": (
                -0.1,
                1.0,
            ),
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "background_depth_range": (
                0.0,
                0.70,
            ),
            "foreground_depth_range": (
                0.60,
                1.0,
            ),
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "relief_height_mm": 0.0,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "smoothing_sigma": -0.1,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "smoothing_radius": 2,
        },
        {
            "name": "portrait",
            "form_sigma": 6.0,
            "detail_sigma": 1.5,
            "smoothing_sigma": 0.5,
            "smoothing_radius": 0,
        },
    ],
)
def test_profile_rejects_invalid_values(arguments):
    with pytest.raises(ValueError):
        AtlasReliefProductProfile(**arguments)
