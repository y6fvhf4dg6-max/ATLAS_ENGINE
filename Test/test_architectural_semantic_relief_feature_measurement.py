import numpy as np
import pytest

from CORE.atlas_architectural_relief_detail_scale_filter import (
    AtlasArchitecturalReliefDetailScaleProfile,
)
from CORE.atlas_architectural_semantic_relief_feature_measurement import (
    AtlasArchitecturalSemanticReliefFeatureMeasurement,
)


def test_measures_named_semantic_regions_from_real_height_map_detail():
    height_map = np.zeros(
        (10, 12),
        dtype=np.float64,
    )

    # Retainable architectural structure.
    height_map[3, 2:8] = 0.50

    # Tiny isolated structure that should fall below the
    # configured physical feature threshold.
    height_map[7, 10] = 0.50

    archivolt_mask = np.zeros_like(
        height_map,
        dtype=bool,
    )
    archivolt_mask[2:5, 1:9] = True

    panel_mask = np.zeros_like(
        height_map,
        dtype=bool,
    )
    panel_mask[6:9, 9:12] = True

    result = (
        AtlasArchitecturalSemanticReliefFeatureMeasurement
        .measure(
            detail_map=height_map,
            feature_masks={
                "archivolt": archivolt_mask,
                "panel": panel_mask,
            },
            width_mm=12.0,
            depth_mm=10.0,
            detail_profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=2.5,
                    activity_threshold=0.10,
                    minimum_density=0.50,
                )
            ),
        )
    )

    assert result["type"] == (
        "architectural_semantic_relief_feature_measurement"
    )

    assert set(result["features"]) == {
        "archivolt",
        "panel",
    }

    archivolt = result["features"]["archivolt"]
    panel = result["features"]["panel"]

    assert archivolt["active_component_count"] >= 1
    assert archivolt["retained_component_count"] >= 1
    assert archivolt["feature_retained"] is True

    assert panel["active_component_count"] == 1
    assert panel["retained_component_count"] == 0
    assert panel["culled_component_count"] == 1
    assert panel["feature_retained"] is False


def test_measurement_does_not_count_detail_outside_feature_mask():
    height_map = np.zeros(
        (8, 8),
        dtype=np.float64,
    )

    # Strong detail exists, but entirely outside the target ROI.
    height_map[1, 1:7] = 0.80

    target_mask = np.zeros_like(
        height_map,
        dtype=bool,
    )
    target_mask[5:7, 5:7] = True

    result = (
        AtlasArchitecturalSemanticReliefFeatureMeasurement
        .measure(
            detail_map=height_map,
            feature_masks={
                "target": target_mask,
            },
            width_mm=8.0,
            depth_mm=8.0,
            detail_profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=1.0,
                    activity_threshold=0.10,
                    minimum_density=0.25,
                )
            ),
        )
    )

    target = result["features"]["target"]

    assert target["active_component_count"] == 0
    assert target["retained_component_count"] == 0
    assert target["culled_component_count"] == 0
    assert target["feature_retained"] is False


def test_reports_retained_active_pixel_ratio_from_physical_filter():
    detail = np.zeros(
        (5, 8),
        dtype=np.float64,
    )

    # Four-pixel retainable line.
    detail[1, 1:5] = 0.60

    # One isolated pixel that should be culled.
    detail[3, 6] = 0.60

    mask = np.ones_like(
        detail,
        dtype=bool,
    )

    result = (
        AtlasArchitecturalSemanticReliefFeatureMeasurement
        .measure(
            detail_map=detail,
            feature_masks={
                "feature": mask,
            },
            width_mm=8.0,
            depth_mm=5.0,
            detail_profile=(
                AtlasArchitecturalReliefDetailScaleProfile(
                    minimum_feature_mm=2.0,
                    activity_threshold=0.10,
                    minimum_density=0.50,
                )
            ),
        )
    )

    feature = result["features"]["feature"]

    assert feature["active_pixel_count"] == 5
    assert feature["retained_pixel_count"] == 4
    assert feature["retained_active_pixel_ratio"] == pytest.approx(
        4.0 / 5.0
    )
