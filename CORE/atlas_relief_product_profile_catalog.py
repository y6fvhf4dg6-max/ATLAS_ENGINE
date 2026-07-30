from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)


ROCK_CARVED_LANDMARK = AtlasReliefProductProfile(
    name="rock-carved-landmark",
    form_sigma=3.2,
    detail_sigma=0.85,
    form_weight=1.0,
    detail_weight=0.42,
    micro_detail_weight=0.015,
    micro_detail_limit=0.02,
    depth_lower_percentile=3.0,
    depth_upper_percentile=97.0,
    depth_gamma=1.05,
    background_depth_range=(0.0, 0.40),
    foreground_depth_range=(0.60, 1.0),
    relief_height_mm=1.8,
    smoothing_sigma=0.30,
    smoothing_radius=1,
)
