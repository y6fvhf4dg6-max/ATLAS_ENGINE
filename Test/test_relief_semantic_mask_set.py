from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from CORE.atlas_relief_semantic_mask_set import (
    AtlasReliefSemanticMaskSet,
)


def save_mask(
    path: Path,
    values: np.ndarray,
) -> None:
    Image.fromarray(
        np.asarray(values, dtype=np.uint8),
        mode="L",
    ).save(path)


def test_loads_named_masks_and_builds_material_map(
    tmp_path: Path,
) -> None:
    vegetation_path = tmp_path / "vegetation.png"
    tomb_facade_path = tmp_path / "tomb_facade.png"

    save_mask(
        vegetation_path,
        np.array(
            [
                [255, 0, 0],
                [0, 0, 0],
            ],
            dtype=np.uint8,
        ),
    )
    save_mask(
        tomb_facade_path,
        np.array(
            [
                [0, 0, 0],
                [0, 255, 0],
            ],
            dtype=np.uint8,
        ),
    )

    result = AtlasReliefSemanticMaskSet.load(
        mask_paths={
            "vegetation": vegetation_path,
            "tomb_facade": tomb_facade_path,
        },
        expected_shape=(2, 3),
        default_material="rock",
    )

    assert result["type"] == "relief_semantic_mask_set"
    assert result["shape"] == (2, 3)
    assert result["material_names"] == (
        "rock",
        "vegetation",
        "tomb_facade",
    )
    assert result["mask_paths"] == {
        "vegetation": str(vegetation_path),
        "tomb_facade": str(tomb_facade_path),
    }
    assert result["region_masks"]["vegetation"].dtype == bool
    assert result["region_masks"]["tomb_facade"].dtype == bool
    assert np.array_equal(
        result["material_id_map"],
        np.array(
            [
                [1, 0, 0],
                [0, 2, 0],
            ],
            dtype=np.uint8,
        ),
    )


def test_rejects_overlapping_masks(
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "first.png"
    second_path = tmp_path / "second.png"

    values = np.array(
        [
            [255, 0],
            [0, 0],
        ],
        dtype=np.uint8,
    )

    save_mask(first_path, values)
    save_mask(second_path, values)

    with pytest.raises(
        ValueError,
        match="region masks overlap",
    ):
        AtlasReliefSemanticMaskSet.load(
            mask_paths={
                "first": first_path,
                "second": second_path,
            },
            expected_shape=(2, 2),
            default_material="rock",
        )


def test_rejects_empty_mask_mapping() -> None:
    with pytest.raises(
        ValueError,
        match="mask_paths must not be empty",
    ):
        AtlasReliefSemanticMaskSet.load(
            mask_paths={},
            expected_shape=(2, 2),
            default_material="rock",
        )
