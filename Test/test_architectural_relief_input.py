from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from CORE.atlas_architectural_relief_input import (
    AtlasArchitecturalReliefInput,
    AtlasArchitecturalReliefSemanticMaskSpec,
)
from CORE.atlas_relief_product_profile_catalog import (
    ROCK_CARVED_LANDMARK,
)
from CORE.atlas_rock_relief_preprocessing_preset import (
    DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
)


def _semantic_mask_spec(tmp_path):
    return AtlasArchitecturalReliefSemanticMaskSpec(
        expected_shape=(99, 240),
        default_material="rock",
        mask_paths={
            "vegetation": (
                tmp_path / "vegetation.png"
            ),
            "tomb_facade": (
                tmp_path / "tomb_facade.png"
            ),
        },
        threshold=128,
    )


def test_architectural_relief_input_groups_complete_source_contract(
    tmp_path,
):
    source_path = tmp_path / "dalyan.png"

    contract = AtlasArchitecturalReliefInput(
        image_path=source_path,
        width_mm=80.0,
        depth_mm=50.0,
        architectural_kind="rock carved landmark",
        product_profile=ROCK_CARVED_LANDMARK,
        preprocessors=(
            DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
        ),
        semantic_masks=_semantic_mask_spec(
            tmp_path
        ),
    )

    assert contract.image_path == source_path
    assert contract.width_mm == 80.0
    assert contract.depth_mm == 50.0
    assert (
        contract.architectural_kind
        == "rock_carved_landmark"
    )
    assert (
        contract.product_profile
        is ROCK_CARVED_LANDMARK
    )
    assert contract.preprocessors == (
        DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
    )
    assert contract.semantic_masks.default_material == "rock"


def test_contract_builds_deterministic_pipeline_request(
    tmp_path,
):
    source_path = tmp_path / "dalyan.png"

    contract = AtlasArchitecturalReliefInput(
        image_path=source_path,
        width_mm=80.0,
        depth_mm=50.0,
        architectural_kind="rock_carved_landmark",
        product_profile=ROCK_CARVED_LANDMARK,
        preprocessors=(
            DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
        ),
        semantic_masks=_semantic_mask_spec(
            tmp_path
        ),
    )

    request = contract.to_pipeline_request()

    assert request == {
        "image_path": source_path,
        "pipeline_kwargs": {
            "width_mm": 80.0,
            "depth_mm": 50.0,
            "product_profile": ROCK_CARVED_LANDMARK,
            "preprocessors": (
                DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
            ),
        },
        "semantic_mask_kwargs": {
            "mask_paths": {
                "vegetation": (
                    tmp_path / "vegetation.png"
                ),
                "tomb_facade": (
                    tmp_path / "tomb_facade.png"
                ),
            },
            "expected_shape": (99, 240),
            "default_material": "rock",
            "threshold": 128,
        },
        "architectural_kind": (
            "rock_carved_landmark"
        ),
    }


def test_semantic_masks_are_optional():
    contract = AtlasArchitecturalReliefInput(
        image_path=Path("source.png"),
        width_mm=100.0,
        depth_mm=60.0,
        architectural_kind="facade",
        product_profile=ROCK_CARVED_LANDMARK,
    )

    request = contract.to_pipeline_request()

    assert contract.preprocessors == ()
    assert contract.semantic_masks is None
    assert request["semantic_mask_kwargs"] is None


def test_contract_and_semantic_mask_spec_are_immutable(
    tmp_path,
):
    semantic_masks = _semantic_mask_spec(
        tmp_path
    )
    contract = AtlasArchitecturalReliefInput(
        image_path=Path("source.png"),
        width_mm=80.0,
        depth_mm=50.0,
        architectural_kind="rock_carved_landmark",
        product_profile=ROCK_CARVED_LANDMARK,
        semantic_masks=semantic_masks,
    )

    with pytest.raises(FrozenInstanceError):
        contract.width_mm = 90.0

    with pytest.raises(FrozenInstanceError):
        semantic_masks.threshold = 64


@pytest.mark.parametrize(
    (
        "field_name",
        "field_value",
        "message",
    ),
    (
        (
            "width_mm",
            0.0,
            "width_mm",
        ),
        (
            "depth_mm",
            -1.0,
            "depth_mm",
        ),
        (
            "architectural_kind",
            " ",
            "architectural_kind",
        ),
    ),
)
def test_rejects_invalid_primary_fields(
    field_name,
    field_value,
    message,
):
    values = {
        "image_path": Path("source.png"),
        "width_mm": 80.0,
        "depth_mm": 50.0,
        "architectural_kind": "facade",
        "product_profile": (
            ROCK_CARVED_LANDMARK
        ),
    }
    values[field_name] = field_value

    with pytest.raises(
        ValueError,
        match=message,
    ):
        AtlasArchitecturalReliefInput(
            **values
        )


def test_rejects_invalid_product_profile():
    with pytest.raises(
        TypeError,
        match="product_profile",
    ):
        AtlasArchitecturalReliefInput(
            image_path=Path("source.png"),
            width_mm=80.0,
            depth_mm=50.0,
            architectural_kind="facade",
            product_profile=object(),
        )


def test_semantic_mask_spec_rejects_empty_paths():
    with pytest.raises(
        ValueError,
        match="mask_paths",
    ):
        AtlasArchitecturalReliefSemanticMaskSpec(
            expected_shape=(99, 240),
            default_material="rock",
            mask_paths={},
        )
