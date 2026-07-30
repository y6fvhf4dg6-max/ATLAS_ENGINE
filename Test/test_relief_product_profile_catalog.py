from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)
from CORE.atlas_relief_product_profile_catalog import (
    ROCK_CARVED_LANDMARK,
)


def test_rock_carved_landmark_profile_contract():
    assert isinstance(
        ROCK_CARVED_LANDMARK,
        AtlasReliefProductProfile,
    )
    assert ROCK_CARVED_LANDMARK.name == (
        "rock-carved-landmark"
    )
    assert ROCK_CARVED_LANDMARK.form_sigma == 3.2
    assert ROCK_CARVED_LANDMARK.detail_sigma == 0.85
    assert ROCK_CARVED_LANDMARK.form_weight == 1.0
    assert ROCK_CARVED_LANDMARK.detail_weight == 0.42
    assert (
        ROCK_CARVED_LANDMARK.micro_detail_weight
        == 0.015
    )
    assert (
        ROCK_CARVED_LANDMARK.micro_detail_limit
        == 0.02
    )
    assert (
        ROCK_CARVED_LANDMARK.depth_lower_percentile
        == 3.0
    )
    assert (
        ROCK_CARVED_LANDMARK.depth_upper_percentile
        == 97.0
    )
    assert ROCK_CARVED_LANDMARK.depth_gamma == 1.05
    assert (
        ROCK_CARVED_LANDMARK.relief_height_mm
        == 1.8
    )
    assert (
        ROCK_CARVED_LANDMARK.smoothing_sigma
        == 0.30
    )
    assert (
        ROCK_CARVED_LANDMARK.smoothing_radius
        == 1
    )
