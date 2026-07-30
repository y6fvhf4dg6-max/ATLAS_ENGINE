import numpy as np
import pytest

from CORE.atlas_relief_semantic_material_map import (
    AtlasReliefSemanticMaterialMap,
)


def test_build_assigns_named_material_ids_and_default_region():
    vegetation = np.array(
        [
            [False, True, True],
            [False, False, False],
        ],
        dtype=bool,
    )
    tomb_facade = np.array(
        [
            [False, False, False],
            [True, True, False],
        ],
        dtype=bool,
    )

    result = AtlasReliefSemanticMaterialMap.build(
        shape=(2, 3),
        region_masks={
            "vegetation": vegetation,
            "tomb_facade": tomb_facade,
        },
        default_material="rock",
    )

    assert result["type"] == "relief_semantic_material_map"
    assert result["shape"] == (2, 3)
    assert result["material_names"] == (
        "rock",
        "vegetation",
        "tomb_facade",
    )

    np.testing.assert_array_equal(
        result["material_id_map"],
        np.array(
            [
                [0, 1, 1],
                [2, 2, 0],
            ],
            dtype=np.uint8,
        ),
    )


def test_build_rejects_overlapping_region_masks():
    first = np.array(
        [[True, False]],
        dtype=bool,
    )
    second = np.array(
        [[True, False]],
        dtype=bool,
    )

    with pytest.raises(
        ValueError,
        match="overlap",
    ):
        AtlasReliefSemanticMaterialMap.build(
            shape=(1, 2),
            region_masks={
                "vegetation": first,
                "tomb_facade": second,
            },
            default_material="rock",
        )


def test_build_rejects_mask_with_wrong_shape():
    with pytest.raises(
        ValueError,
        match="shape",
    ):
        AtlasReliefSemanticMaterialMap.build(
            shape=(2, 3),
            region_masks={
                "vegetation": np.zeros(
                    (3, 2),
                    dtype=bool,
                ),
            },
            default_material="rock",
        )
