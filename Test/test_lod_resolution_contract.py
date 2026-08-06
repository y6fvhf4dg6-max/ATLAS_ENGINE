from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_lod_level_catalog import (
    LOD_2,
    AtlasLoDLevel,
)
from CORE.atlas_lod_resolution_contract import (
    AtlasLoDResolutionInput,
    AtlasLoDResolutionResult,
)


def _input(**overrides):
    values = {
        "product_size_mm": 150.0,
        "scale_ratio": 3000.0,
        "nozzle_diameter_mm": 0.4,
        "layer_height_mm": 0.2,
        "minimum_wall_thickness_mm": 0.8,
        "landmark_importance": 0.75,
        "viewing_distance_mm": 600.0,
        "available_color_count": 4,
    }
    values.update(overrides)

    return AtlasLoDResolutionInput(
        **values
    )


def test_resolution_input_normalizes_numeric_fields():
    contract = _input(
        product_size_mm=150,
        scale_ratio=3000,
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        minimum_wall_thickness_mm=0.8,
        landmark_importance=0.75,
        viewing_distance_mm=600,
        available_color_count=4,
    )

    assert contract.product_size_mm == pytest.approx(
        150.0
    )
    assert contract.scale_ratio == pytest.approx(
        3000.0
    )
    assert contract.nozzle_diameter_mm == pytest.approx(
        0.4
    )
    assert contract.layer_height_mm == pytest.approx(
        0.2
    )
    assert (
        contract.minimum_wall_thickness_mm
        == pytest.approx(0.8)
    )
    assert contract.landmark_importance == pytest.approx(
        0.75
    )
    assert contract.viewing_distance_mm == pytest.approx(
        600.0
    )
    assert contract.available_color_count == 4


def test_resolution_input_is_immutable():
    contract = _input()

    with pytest.raises(
        FrozenInstanceError,
    ):
        contract.product_size_mm = 200.0


@pytest.mark.parametrize(
    (
        "field",
        "value",
    ),
    (
        (
            "product_size_mm",
            0.0,
        ),
        (
            "product_size_mm",
            float("nan"),
        ),
        (
            "scale_ratio",
            0.0,
        ),
        (
            "scale_ratio",
            float("inf"),
        ),
        (
            "nozzle_diameter_mm",
            0.0,
        ),
        (
            "layer_height_mm",
            -0.1,
        ),
        (
            "minimum_wall_thickness_mm",
            0.0,
        ),
        (
            "landmark_importance",
            -0.01,
        ),
        (
            "landmark_importance",
            1.01,
        ),
        (
            "viewing_distance_mm",
            0.0,
        ),
        (
            "available_color_count",
            0,
        ),
        (
            "available_color_count",
            True,
        ),
        (
            "available_color_count",
            2.5,
        ),
    ),
)
def test_resolution_input_rejects_invalid_fields(
    field,
    value,
):
    with pytest.raises(
        ValueError,
        match=field,
    ):
        _input(
            **{
                field: value,
            }
        )


def test_resolution_result_groups_level_and_evidence():
    source = _input()

    result = AtlasLoDResolutionResult(
        level=LOD_2,
        source=source,
        limiting_factors=(
            "nozzle_diameter",
            "viewing_distance",
        ),
        supporting_factors=(
            "landmark_importance",
        ),
    )

    assert isinstance(
        result.level,
        AtlasLoDLevel,
    )
    assert result.level is LOD_2
    assert result.source is source
    assert result.limiting_factors == (
        "nozzle_diameter",
        "viewing_distance",
    )
    assert result.supporting_factors == (
        "landmark_importance",
    )


def test_resolution_result_normalizes_factor_names():
    result = AtlasLoDResolutionResult(
        level=LOD_2,
        source=_input(),
        limiting_factors=(
            "  Nozzle Diameter  ",
        ),
        supporting_factors=(
            "Landmark Importance",
        ),
    )

    assert result.limiting_factors == (
        "nozzle_diameter",
    )
    assert result.supporting_factors == (
        "landmark_importance",
    )


def test_resolution_result_is_immutable():
    result = AtlasLoDResolutionResult(
        level=LOD_2,
        source=_input(),
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.level = None


@pytest.mark.parametrize(
    (
        "field",
        "value",
    ),
    (
        (
            "level",
            object(),
        ),
        (
            "source",
            object(),
        ),
        (
            "limiting_factors",
            (
                "scale",
                "scale",
            ),
        ),
        (
            "supporting_factors",
            (
                " ",
            ),
        ),
    ),
)
def test_resolution_result_rejects_invalid_contract(
    field,
    value,
):
    values = {
        "level": LOD_2,
        "source": _input(),
        "limiting_factors": (),
        "supporting_factors": (),
    }
    values[field] = value

    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field,
    ):
        AtlasLoDResolutionResult(
            **values
        )
