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


def test_pipeline_supports_contrast_remapping():
    values = np.array(
        [
            [0.0, 0.25, 0.50],
            [0.75, 0.90, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build(
        values,
        width_mm=20.0,
        depth_mm=10.0,
        black_point=0.25,
        white_point=0.75,
        gamma=1.0,
    )

    contrast = result[
        "contrast_height_map"
    ]

    assert contrast[0, 0] == pytest.approx(0.0)
    assert contrast[0, 1] == pytest.approx(0.0)
    assert contrast[0, 2] == pytest.approx(0.5)
    assert contrast[1, 0] == pytest.approx(1.0)
    assert contrast[1, 2] == pytest.approx(1.0)


def test_pipeline_gamma_changes_processed_relief():
    values = [
        [0.0, 0.5, 1.0],
        [0.0, 0.5, 1.0],
    ]

    normal = AtlasReliefPipeline.build(
        values,
        width_mm=10.0,
        depth_mm=5.0,
        gamma=1.0,
    )

    shaped = AtlasReliefPipeline.build(
        values,
        width_mm=10.0,
        depth_mm=5.0,
        gamma=2.0,
    )

    assert shaped[
        "contrast_height_map"
    ][0, 1] == pytest.approx(0.25)

    assert not np.array_equal(
        normal["processed_height_map"],
        shaped["processed_height_map"],
    )


def test_pipeline_records_contrast_settings():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=10.0,
        depth_mm=10.0,
        black_point=0.10,
        white_point=0.90,
        gamma=0.75,
    )

    settings = result["settings"]

    assert settings["black_point"] == pytest.approx(
        0.10
    )
    assert settings["white_point"] == pytest.approx(
        0.90
    )
    assert settings["gamma"] == pytest.approx(
        0.75
    )


@pytest.mark.parametrize(
    "black_point,white_point,gamma",
    [
        (-0.1, 1.0, 1.0),
        (0.0, 1.1, 1.0),
        (0.8, 0.2, 1.0),
        (0.0, 1.0, 0.0),
    ],
)
def test_pipeline_rejects_invalid_contrast_settings(
    black_point,
    white_point,
    gamma,
):
    with pytest.raises(ValueError):
        AtlasReliefPipeline.build(
            _values(),
            width_mm=10.0,
            depth_mm=10.0,
            black_point=black_point,
            white_point=white_point,
            gamma=gamma,
        )


def test_pipeline_forwards_slope_risk_thresholds():
    result = AtlasReliefPipeline.build(
        [
            [0.5, 1.0],
            [0.0, 0.5],
        ],
        width_mm=1.0,
        depth_mm=1.0,
        relief_height_mm=2.0,
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
        warning_slope_area_percent=100.0,
        critical_slope_area_percent=100.0,
    )

    report = result["quality_report"]

    assert report["warning_slope_area_percent"] == 100.0
    assert report["critical_slope_area_percent"] == 100.0
    assert report["print_risk_status"] == "WARN"


def test_pipeline_records_slope_risk_settings():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
        warning_slope_degrees=48.0,
        critical_slope_degrees=72.0,
        warning_slope_area_percent=3.0,
        critical_slope_area_percent=1.0,
    )

    settings = result["settings"]

    assert settings["warning_slope_degrees"] == 48.0
    assert settings["critical_slope_degrees"] == 72.0
    assert settings["warning_slope_area_percent"] == 3.0
    assert settings["critical_slope_area_percent"] == 1.0


def test_pipeline_preserves_default_slope_risk_settings():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
    )

    settings = result["settings"]

    assert settings["warning_slope_degrees"] == 55.0
    assert settings["critical_slope_degrees"] == 75.0
    assert settings["warning_slope_area_percent"] == 0.0
    assert settings["critical_slope_area_percent"] == 0.0


def test_pipeline_accepts_relief_risk_profile():
    from CORE.atlas_relief_risk_profile import (
        AtlasReliefRiskProfile,
    )

    profile = AtlasReliefRiskProfile(
        warning_slope_degrees=47.0,
        critical_slope_degrees=71.0,
        warning_slope_area_percent=4.0,
        critical_slope_area_percent=2.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
        risk_profile=profile,
    )

    assert result["settings"]["warning_slope_degrees"] == 47.0
    assert result["settings"]["critical_slope_degrees"] == 71.0
    assert (
        result["settings"]["warning_slope_area_percent"]
        == 4.0
    )
    assert (
        result["settings"]["critical_slope_area_percent"]
        == 2.0
    )


def test_pipeline_risk_profile_overrides_scalar_risk_arguments():
    from CORE.atlas_relief_risk_profile import (
        AtlasReliefRiskProfile,
    )

    profile = AtlasReliefRiskProfile(
        warning_slope_degrees=46.0,
        critical_slope_degrees=70.0,
        warning_slope_area_percent=5.0,
        critical_slope_area_percent=3.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
        warning_slope_degrees=55.0,
        critical_slope_degrees=75.0,
        warning_slope_area_percent=0.0,
        critical_slope_area_percent=0.0,
        risk_profile=profile,
    )

    assert result["settings"]["warning_slope_degrees"] == 46.0
    assert result["settings"]["critical_slope_degrees"] == 70.0
    assert (
        result["settings"]["warning_slope_area_percent"]
        == 5.0
    )
    assert (
        result["settings"]["critical_slope_area_percent"]
        == 3.0
    )


def test_pipeline_records_risk_profile_name():
    from CORE.atlas_relief_risk_profile import (
        AtlasReliefRiskProfile,
    )

    profile = AtlasReliefRiskProfile(
        name="prototype-safe",
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
        risk_profile=profile,
    )

    assert (
        result["settings"]["risk_profile_name"]
        == "prototype-safe"
    )


def test_pipeline_records_no_profile_name_by_default():
    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
    )

    assert result["settings"]["risk_profile_name"] is None


def test_pipeline_accepts_physical_sampling_plan():
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=30.0,
        sampling_plan=plan,
    )

    assert result["processed_height_map"].shape == (
        4,
        5,
    )
    assert result["mesh"]["row_count"] == 4
    assert result["mesh"]["column_count"] == 5


def test_pipeline_records_sampling_plan_metadata():
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=41.0,
        depth_mm=31.0,
        target_sample_spacing_mm=10.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=41.0,
        depth_mm=31.0,
        sampling_plan=plan,
    )

    settings = result["settings"]

    assert settings[
        "target_sample_spacing_mm"
    ] == 10.0
    assert settings[
        "effective_spacing_x_mm"
    ] == pytest.approx(8.2)
    assert settings[
        "effective_spacing_y_mm"
    ] == pytest.approx(7.75)
    assert settings["sample_count"] == 30
    assert (
        settings["expected_triangle_count"]
        == plan.total_triangle_count
    )


def test_pipeline_sampling_metadata_is_none_by_default():
    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=30.0,
    )

    settings = result["settings"]

    assert settings[
        "target_sample_spacing_mm"
    ] is None
    assert settings[
        "effective_spacing_x_mm"
    ] is None
    assert settings[
        "effective_spacing_y_mm"
    ] is None
    assert settings["sample_count"] is None
    assert settings[
        "expected_triangle_count"
    ] is None


def test_pipeline_rejects_sampling_plan_with_explicit_target_size():
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "sampling_plan cannot be combined with "
            "target_rows or target_columns"
        ),
    ):
        AtlasReliefPipeline.build(
            [
                [0.0, 0.5],
                [0.5, 1.0],
            ],
            width_mm=40.0,
            depth_mm=30.0,
            target_rows=4,
            target_columns=5,
            sampling_plan=plan,
        )


@pytest.mark.parametrize(
    "width_mm,depth_mm",
    [
        (41.0, 30.0),
        (40.0, 31.0),
    ],
)
def test_pipeline_rejects_sampling_plan_dimension_mismatch(
    width_mm,
    depth_mm,
):
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "sampling_plan dimensions must match "
            "pipeline dimensions"
        ),
    ):
        AtlasReliefPipeline.build(
            [
                [0.0, 0.5],
                [0.5, 1.0],
            ],
            width_mm=width_mm,
            depth_mm=depth_mm,
            sampling_plan=plan,
        )
