from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_lod_level_catalog import (
    LOD_0,
    LOD_1,
    LOD_2,
    LOD_3,
    LOD_4,
    AtlasLoDLevel,
    AtlasLoDLevelCatalog,
)


def test_catalog_exposes_five_official_levels():
    levels = AtlasLoDLevelCatalog.levels()

    assert levels == (
        LOD_0,
        LOD_1,
        LOD_2,
        LOD_3,
        LOD_4,
    )
    assert tuple(
        level.level
        for level in levels
    ) == (
        0,
        1,
        2,
        3,
        4,
    )


@pytest.mark.parametrize(
    (
        "level",
        "name",
        "included_features",
    ),
    (
        (
            LOD_0,
            "footprint_mass",
            (
                "footprint",
                "base_mass",
            ),
        ),
        (
            LOD_1,
            "primary_form",
            (
                "footprint",
                "base_mass",
                "main_body",
                "primary_roof",
            ),
        ),
        (
            LOD_2,
            "major_components",
            (
                "footprint",
                "base_mass",
                "main_body",
                "primary_roof",
                "tower",
                "dome",
                "apse",
                "major_component",
            ),
        ),
        (
            LOD_3,
            "structural_detail",
            (
                "footprint",
                "base_mass",
                "main_body",
                "primary_roof",
                "tower",
                "dome",
                "apse",
                "major_component",
                "facade_opening",
                "structural_detail",
            ),
        ),
        (
            LOD_4,
            "ornament_relief",
            (
                "footprint",
                "base_mass",
                "main_body",
                "primary_roof",
                "tower",
                "dome",
                "apse",
                "major_component",
                "facade_opening",
                "structural_detail",
                "ornament",
                "architectural_relief",
            ),
        ),
    ),
)
def test_official_lod_level_contract(
    level,
    name,
    included_features,
):
    assert isinstance(
        level,
        AtlasLoDLevel,
    )
    assert level.name == name
    assert level.included_features == (
        included_features
    )


def test_catalog_resolves_levels_by_integer():
    assert AtlasLoDLevelCatalog.resolve(0) is LOD_0
    assert AtlasLoDLevelCatalog.resolve(1) is LOD_1
    assert AtlasLoDLevelCatalog.resolve(2) is LOD_2
    assert AtlasLoDLevelCatalog.resolve(3) is LOD_3
    assert AtlasLoDLevelCatalog.resolve(4) is LOD_4


@pytest.mark.parametrize(
    "value",
    (
        -1,
        5,
        None,
        True,
        "",
        "lod2",
        2.5,
    ),
)
def test_catalog_rejects_invalid_level_values(
    value,
):
    with pytest.raises(
        ValueError,
        match="level",
    ):
        AtlasLoDLevelCatalog.resolve(
            value
        )


def test_level_supports_feature_queries():
    assert LOD_0.supports(
        "footprint"
    ) is True
    assert LOD_0.supports(
        "primary_roof"
    ) is False
    assert LOD_2.supports(
        "dome"
    ) is True
    assert LOD_3.supports(
        "facade_opening"
    ) is True
    assert LOD_4.supports(
        "architectural_relief"
    ) is True


def test_level_normalizes_feature_queries():
    assert LOD_4.supports(
        "  Architectural Relief  "
    ) is True
    assert LOD_3.supports(
        "Facade Opening"
    ) is True


def test_levels_are_cumulative():
    levels = AtlasLoDLevelCatalog.levels()

    for lower, higher in zip(
        levels,
        levels[1:],
    ):
        assert set(
            lower.included_features
        ).issubset(
            higher.included_features
        )


def test_level_contract_is_immutable():
    with pytest.raises(
        FrozenInstanceError,
    ):
        LOD_2.name = "changed"


@pytest.mark.parametrize(
    (
        "kwargs",
        "message",
    ),
    (
        (
            {
                "level": -1,
                "name": "invalid",
                "included_features": (
                    "footprint",
                ),
            },
            "level",
        ),
        (
            {
                "level": 0,
                "name": " ",
                "included_features": (
                    "footprint",
                ),
            },
            "name",
        ),
        (
            {
                "level": 0,
                "name": "valid",
                "included_features": (),
            },
            "included_features",
        ),
        (
            {
                "level": 0,
                "name": "valid",
                "included_features": (
                    "footprint",
                    "footprint",
                ),
            },
            "included_features",
        ),
    ),
)
def test_level_rejects_invalid_contract(
    kwargs,
    message,
):
    with pytest.raises(
        ValueError,
        match=message,
    ):
        AtlasLoDLevel(
            **kwargs
        )
