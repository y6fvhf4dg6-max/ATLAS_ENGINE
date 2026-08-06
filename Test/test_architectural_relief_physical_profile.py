from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_architectural_relief_physical_profile import (
    AtlasArchitecturalReliefPhysicalProfile,
)


def test_normalizes_profile_name_and_numeric_fields():
    profile = AtlasArchitecturalReliefPhysicalProfile(
        name="  Architectural Premium V1  ",
        base_thickness_mm=1,
        relief_height_mm=2.4,
        target_sample_spacing_mm=0.25,
    )

    assert profile.name == "Architectural Premium V1"
    assert profile.base_thickness_mm == pytest.approx(
        1.0
    )
    assert profile.relief_height_mm == pytest.approx(
        2.4
    )
    assert (
        profile.target_sample_spacing_mm
        == pytest.approx(0.25)
    )
    assert profile.total_height_mm == pytest.approx(
        3.4
    )


def test_resolves_sampling_and_mesh_contracts():
    profile = AtlasArchitecturalReliefPhysicalProfile(
        name="architectural-premium-v1",
        base_thickness_mm=1.0,
        relief_height_mm=2.4,
        target_sample_spacing_mm=0.25,
    )

    result = profile.resolve(
        width_mm=80.0,
        depth_mm=50.0,
    )

    assert result["type"] == (
        "architectural_relief_physical_plan"
    )
    assert result["profile"] is profile
    assert result["width_mm"] == pytest.approx(
        80.0
    )
    assert result["depth_mm"] == pytest.approx(
        50.0
    )
    assert result["total_height_mm"] == pytest.approx(
        3.4
    )

    sampling_plan = result["sampling_plan"]

    assert sampling_plan.width_mm == pytest.approx(
        80.0
    )
    assert sampling_plan.depth_mm == pytest.approx(
        50.0
    )
    assert (
        sampling_plan.target_sample_spacing_mm
        == pytest.approx(0.25)
    )
    assert sampling_plan.column_count == 321
    assert sampling_plan.row_count == 201

    assert result["pipeline_kwargs"] == {
        "base_thickness_mm": 1.0,
        "relief_height_mm": 2.4,
        "target_rows": 201,
        "target_columns": 321,
    }

    assert result["mesh_kwargs"] == {
        "width_mm": 80.0,
        "depth_mm": 50.0,
        "base_thickness_mm": 1.0,
        "relief_height_mm": 2.4,
    }


def test_resolution_uses_effective_sample_spacing():
    profile = AtlasArchitecturalReliefPhysicalProfile(
        name="architectural",
        base_thickness_mm=0.9,
        relief_height_mm=2.0,
        target_sample_spacing_mm=0.30,
    )

    result = profile.resolve(
        width_mm=1.0,
        depth_mm=1.0,
    )

    assert result[
        "effective_spacing_x_mm"
    ] <= 0.30
    assert result[
        "effective_spacing_y_mm"
    ] <= 0.30
    assert result["triangle_count"] == (
        result["sampling_plan"]
        .total_triangle_count
    )


def test_profile_is_immutable():
    profile = AtlasArchitecturalReliefPhysicalProfile(
        name="architectural",
        base_thickness_mm=1.0,
        relief_height_mm=2.0,
        target_sample_spacing_mm=0.25,
    )

    with pytest.raises(FrozenInstanceError):
        profile.base_thickness_mm = 1.2


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("name", "   "),
        ("base_thickness_mm", 0.0),
        ("base_thickness_mm", -0.1),
        ("base_thickness_mm", float("nan")),
        ("relief_height_mm", 0.0),
        ("relief_height_mm", -0.1),
        ("relief_height_mm", float("inf")),
        ("target_sample_spacing_mm", 0.0),
        ("target_sample_spacing_mm", -0.1),
        (
            "target_sample_spacing_mm",
            float("nan"),
        ),
    ],
)
def test_profile_rejects_invalid_values(
    field,
    value,
):
    kwargs = {
        "name": "architectural",
        "base_thickness_mm": 1.0,
        "relief_height_mm": 2.0,
        "target_sample_spacing_mm": 0.25,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=field,
    ):
        AtlasArchitecturalReliefPhysicalProfile(
            **kwargs
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("width_mm", 0.0),
        ("width_mm", -1.0),
        ("width_mm", float("nan")),
        ("depth_mm", 0.0),
        ("depth_mm", -1.0),
        ("depth_mm", float("inf")),
    ],
)
def test_resolution_rejects_invalid_dimensions(
    field,
    value,
):
    profile = AtlasArchitecturalReliefPhysicalProfile(
        name="architectural",
        base_thickness_mm=1.0,
        relief_height_mm=2.0,
        target_sample_spacing_mm=0.25,
    )

    kwargs = {
        "width_mm": 80.0,
        "depth_mm": 50.0,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=field,
    ):
        profile.resolve(
            **kwargs
        )
