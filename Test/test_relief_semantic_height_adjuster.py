import numpy as np

from CORE.atlas_relief_semantic_height_adjuster import (
    AtlasReliefSemanticHeightAdjuster,
)


def test_adjusts_height_map_by_material() -> None:
    height_map = np.array(
        [
            [0.20, 0.40, 0.60],
            [0.30, 0.50, 0.70],
        ],
        dtype=np.float64,
    )

    material_id_map = np.array(
        [
            [0, 1, 2],
            [0, 1, 2],
        ],
        dtype=np.uint8,
    )

    result = AtlasReliefSemanticHeightAdjuster.apply(
        height_map=height_map,
        material_id_map=material_id_map,
        material_names=(
            "rock",
            "vegetation",
            "tomb_facade",
        ),
        height_scales={
            "rock": 1.0,
            "vegetation": 0.75,
            "tomb_facade": 1.15,
        },
    )

    expected = np.array(
        [
            [0.20, 0.30, 0.69],
            [0.30, 0.375, 0.805],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_rejects_mismatched_shapes() -> None:
    height_map = np.zeros((2, 3), dtype=np.float64)
    material_id_map = np.zeros((3, 2), dtype=np.uint8)

    try:
        AtlasReliefSemanticHeightAdjuster.apply(
            height_map=height_map,
            material_id_map=material_id_map,
            material_names=("rock",),
            height_scales={"rock": 1.0},
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")
