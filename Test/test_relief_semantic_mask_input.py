import numpy as np
import pytest
from PIL import Image

from CORE.atlas_relief_semantic_mask_input import (
    AtlasReliefSemanticMaskInput,
)


def test_load_reads_grayscale_mask_as_boolean_array(tmp_path):
    path = tmp_path / "vegetation_mask.png"
    Image.fromarray(
        np.array(
            [
                [0, 255, 128],
                [127, 129, 1],
            ],
            dtype=np.uint8,
        ),
        mode="L",
    ).save(path)

    result = AtlasReliefSemanticMaskInput.load(
        path,
        threshold=128,
    )

    assert result["type"] == "relief_semantic_mask_input"
    assert result["path"] == str(path)
    assert result["shape"] == (2, 3)
    assert result["threshold"] == 128

    np.testing.assert_array_equal(
        result["mask"],
        np.array(
            [
                [False, True, True],
                [False, True, False],
            ],
            dtype=bool,
        ),
    )


def test_load_uses_rgb_luminance(tmp_path):
    path = tmp_path / "tomb_facade_mask.png"
    Image.fromarray(
        np.array(
            [
                [[255, 255, 255], [0, 0, 0]],
                [[255, 0, 0], [0, 255, 0]],
            ],
            dtype=np.uint8,
        ),
        mode="RGB",
    ).save(path)

    result = AtlasReliefSemanticMaskInput.load(
        path,
        threshold=128,
    )

    np.testing.assert_array_equal(
        result["mask"],
        np.array(
            [
                [True, False],
                [False, True],
            ],
            dtype=bool,
        ),
    )


def test_load_rejects_unexpected_shape(tmp_path):
    path = tmp_path / "mask.png"
    Image.fromarray(
        np.full((2, 3), 255, dtype=np.uint8),
        mode="L",
    ).save(path)

    with pytest.raises(ValueError, match="shape"):
        AtlasReliefSemanticMaskInput.load(
            path,
            expected_shape=(3, 2),
        )


def test_load_rejects_threshold_outside_uint8_range(tmp_path):
    path = tmp_path / "mask.png"
    Image.fromarray(
        np.full((1, 1), 255, dtype=np.uint8),
        mode="L",
    ).save(path)

    with pytest.raises(ValueError, match="threshold"):
        AtlasReliefSemanticMaskInput.load(
            path,
            threshold=256,
        )
