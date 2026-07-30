from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_relief_product_profile_catalog import (
    ROCK_CARVED_LANDMARK,
)
from CORE.atlas_rock_relief_preprocessing_preset import (
    DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
)
from CORE.atlas_rock_relief_production_preset import (
    DALYAN_ROCK_TOMBS_PRODUCTION_PRESET,
    AtlasRockReliefProductionPreset,
)


def test_dalyan_production_preset_combines_profile_and_preprocessors():
    preset = DALYAN_ROCK_TOMBS_PRODUCTION_PRESET

    assert isinstance(
        preset,
        AtlasRockReliefProductionPreset,
    )
    assert preset.name == "dalyan-rock-tombs"
    assert preset.product_profile is ROCK_CARVED_LANDMARK
    assert preset.preprocessors == (
        DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
    )


def test_production_preset_is_immutable():
    with pytest.raises(FrozenInstanceError):
        DALYAN_ROCK_TOMBS_PRODUCTION_PRESET.name = "changed"


def test_production_preset_rejects_blank_name():
    with pytest.raises(
        ValueError,
        match="name must not be blank",
    ):
        AtlasRockReliefProductionPreset(
            name=" ",
            product_profile=ROCK_CARVED_LANDMARK,
            preprocessors=(
                DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
            ),
        )


def test_production_preset_build_from_image_routes_locked_configuration(
    monkeypatch,
) -> None:
    captured = {}
    expected_result = object()

    def fake_build_from_image(
        image_path,
        **kwargs,
    ):
        captured["image_path"] = image_path
        captured["kwargs"] = kwargs
        return expected_result

    monkeypatch.setattr(
        "CORE.atlas_rock_relief_production_preset."
        "AtlasReliefPipeline.build_from_image",
        fake_build_from_image,
    )

    result = DALYAN_ROCK_TOMBS_PRODUCTION_PRESET.build_from_image(
        "source.png",
        width_mm=80.0,
        depth_mm=50.0,
    )

    assert result is expected_result
    assert captured["image_path"] == "source.png"
    assert captured["kwargs"] == {
        "width_mm": 80.0,
        "depth_mm": 50.0,
        "product_profile": ROCK_CARVED_LANDMARK,
        "preprocessors": (
            DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
        ),
    }
