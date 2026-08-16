from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_semantic_relief_repetition import (
    AtlasSemanticReliefRepetition,
)


def test_semantic_relief_repetition_normalizes_instance_pattern():
    repetition = AtlasSemanticReliefRepetition(
        repeat_group_id=" Nave Windows ",
        quantity=12,
        spacing_mm=(8, 0, 0),
        interchangeable=True,
    )

    assert repetition.repeat_group_id == "nave_windows"
    assert repetition.quantity == 12
    assert repetition.spacing_mm == (8.0, 0.0, 0.0)
    assert repetition.interchangeable is True

    with pytest.raises(FrozenInstanceError):
        repetition.quantity = 8

@pytest.mark.parametrize(
    "quantity",
    (True, 0, -1, 1.5, "12"),
)
def test_semantic_relief_repetition_rejects_invalid_quantity(
    quantity,
):
    with pytest.raises(ValueError, match="quantity"):
        AtlasSemanticReliefRepetition(
            repeat_group_id="Nave Windows",
            quantity=quantity,
            spacing_mm=(8.0, 0.0, 0.0),
            interchangeable=True,
        )

@pytest.mark.parametrize(
    "interchangeable",
    (1, 0, "yes", None),
)
def test_semantic_relief_repetition_rejects_invalid_interchangeable(
    interchangeable,
):
    with pytest.raises(ValueError, match="interchangeable"):
        AtlasSemanticReliefRepetition(
            repeat_group_id="Nave Windows",
            quantity=12,
            spacing_mm=(8.0, 0.0, 0.0),
            interchangeable=interchangeable,
        )

def test_semantic_relief_repetition_rejects_zero_spacing_for_multiple_instances():
    with pytest.raises(ValueError, match="spacing_mm"):
        AtlasSemanticReliefRepetition(
            repeat_group_id="Nave Windows",
            quantity=12,
            spacing_mm=(0.0, 0.0, 0.0),
            interchangeable=True,
        )

@pytest.mark.parametrize(
    "spacing_mm",
    (
        (8.0, 0.0),
        (8.0, float("nan"), 0.0),
        "8,0,0",
    ),
)
def test_semantic_relief_repetition_rejects_malformed_spacing(
    spacing_mm,
):
    with pytest.raises(ValueError, match="spacing_mm"):
        AtlasSemanticReliefRepetition(
            repeat_group_id="Nave Windows",
            quantity=12,
            spacing_mm=spacing_mm,
            interchangeable=True,
        )


def test_semantic_relief_repetition_allows_zero_spacing_for_single_instance():
    repetition = AtlasSemanticReliefRepetition(
        repeat_group_id="Unique Portal",
        quantity=1,
        spacing_mm=(0.0, 0.0, 0.0),
        interchangeable=False,
    )

    assert repetition.spacing_mm == (0.0, 0.0, 0.0)
