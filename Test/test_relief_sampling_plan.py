import math

import pytest

from CORE.atlas_relief_sampling_plan import (
    AtlasReliefSamplingPlan,
)


def test_plan_uses_physical_sample_spacing():
    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    assert plan.column_count == 5
    assert plan.row_count == 4
    assert plan.sample_count == 20


def test_plan_never_exceeds_requested_sample_spacing():
    plan = AtlasReliefSamplingPlan(
        width_mm=41.0,
        depth_mm=31.0,
        target_sample_spacing_mm=10.0,
    )

    assert plan.column_count == 6
    assert plan.row_count == 5

    assert plan.effective_spacing_x_mm == pytest.approx(
        8.2
    )
    assert plan.effective_spacing_y_mm == pytest.approx(
        7.75
    )

    assert (
        plan.effective_spacing_x_mm
        <= plan.target_sample_spacing_mm
    )
    assert (
        plan.effective_spacing_y_mm
        <= plan.target_sample_spacing_mm
    )


def test_plan_calculates_expected_triangle_counts():
    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    assert plan.top_triangle_count == 24
    assert plan.bottom_triangle_count == 24
    assert plan.perimeter_triangle_count == 28
    assert plan.total_triangle_count == 76


def test_plan_produces_pipeline_target_arguments():
    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    assert plan.to_pipeline_kwargs() == {
        "target_rows": 4,
        "target_columns": 5,
    }


def test_plan_is_immutable():
    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    with pytest.raises(AttributeError):
        plan.width_mm = 50.0


@pytest.mark.parametrize(
    "arguments",
    [
        {
            "width_mm": 0.0,
            "depth_mm": 30.0,
            "target_sample_spacing_mm": 1.0,
        },
        {
            "width_mm": -1.0,
            "depth_mm": 30.0,
            "target_sample_spacing_mm": 1.0,
        },
        {
            "width_mm": 40.0,
            "depth_mm": 0.0,
            "target_sample_spacing_mm": 1.0,
        },
        {
            "width_mm": 40.0,
            "depth_mm": -1.0,
            "target_sample_spacing_mm": 1.0,
        },
        {
            "width_mm": 40.0,
            "depth_mm": 30.0,
            "target_sample_spacing_mm": 0.0,
        },
        {
            "width_mm": 40.0,
            "depth_mm": 30.0,
            "target_sample_spacing_mm": -1.0,
        },
        {
            "width_mm": math.nan,
            "depth_mm": 30.0,
            "target_sample_spacing_mm": 1.0,
        },
        {
            "width_mm": 40.0,
            "depth_mm": math.inf,
            "target_sample_spacing_mm": 1.0,
        },
        {
            "width_mm": 40.0,
            "depth_mm": 30.0,
            "target_sample_spacing_mm": math.nan,
        },
    ],
)
def test_plan_rejects_invalid_physical_values(
    arguments,
):
    with pytest.raises(ValueError):
        AtlasReliefSamplingPlan(**arguments)


def test_plan_converts_numeric_values_to_float():
    plan = AtlasReliefSamplingPlan(
        width_mm=40,
        depth_mm=30,
        target_sample_spacing_mm=10,
    )

    assert plan.width_mm == 40.0
    assert plan.depth_mm == 30.0
    assert plan.target_sample_spacing_mm == 10.0
