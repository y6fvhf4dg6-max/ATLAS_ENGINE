from pathlib import Path

import numpy as np
import pytest

from CORE.atlas_relief_mask_input import (
    AtlasReliefMaskInput,
)


def test_loads_grayscale_mask_as_normalized_float64(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "mask.png"

    image = Image.new(
        "L",
        (3, 2),
    )
    image.putdata(
        [
            0,
            128,
            255,
            64,
            192,
            32,
        ]
    )
    image.save(path)

    result = AtlasReliefMaskInput.load(path)

    mask = result["mask"]

    assert result["type"] == "relief_mask_input"
    assert mask.shape == (2, 3)
    assert mask.dtype == np.float64
    assert mask[0, 0] == pytest.approx(0.0)
    assert mask[0, 1] == pytest.approx(
        128.0 / 255.0
    )
    assert mask[0, 2] == pytest.approx(1.0)


def test_converts_rgb_mask_to_luminance(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "rgb-mask.png"

    image = Image.new(
        "RGB",
        (2, 1),
    )
    image.putdata(
        [
            (255, 255, 255),
            (0, 0, 0),
        ]
    )
    image.save(path)

    result = AtlasReliefMaskInput.load(path)

    assert result["mask"][0, 0] == pytest.approx(
        1.0
    )
    assert result["mask"][0, 1] == pytest.approx(
        0.0
    )


def test_uses_alpha_channel_when_requested(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "alpha-mask.png"

    image = Image.new(
        "RGBA",
        (3, 1),
    )
    image.putdata(
        [
            (255, 0, 0, 0),
            (255, 0, 0, 128),
            (255, 0, 0, 255),
        ]
    )
    image.save(path)

    result = AtlasReliefMaskInput.load(
        path,
        use_alpha=True,
    )

    assert result["mask"][0, 0] == pytest.approx(
        0.0
    )
    assert result["mask"][0, 1] == pytest.approx(
        128.0 / 255.0
    )
    assert result["mask"][0, 2] == pytest.approx(
        1.0
    )


def test_rejects_use_alpha_for_image_without_alpha(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "no-alpha.png"

    Image.new(
        "RGB",
        (2, 2),
        (255, 255, 255),
    ).save(path)

    with pytest.raises(ValueError):
        AtlasReliefMaskInput.load(
            path,
            use_alpha=True,
        )


def test_records_mask_metadata(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "metadata.png"

    Image.new(
        "L",
        (4, 3),
        128,
    ).save(path)

    result = AtlasReliefMaskInput.load(path)

    assert result["source_path"] == str(
        path.resolve()
    )
    assert result["source_mode"] == "L"
    assert result["width_pixels"] == 4
    assert result["height_pixels"] == 3
    assert result["use_alpha"] is False


def test_load_is_deterministic(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "deterministic.png"

    image = Image.new(
        "L",
        (4, 4),
    )
    image.putdata(
        list(range(16))
    )
    image.save(path)

    first = AtlasReliefMaskInput.load(path)
    second = AtlasReliefMaskInput.load(path)

    assert np.array_equal(
        first["mask"],
        second["mask"],
    )


def test_result_does_not_share_mutable_mask_state(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "isolated.png"

    Image.new(
        "L",
        (2, 2),
        128,
    ).save(path)

    first = AtlasReliefMaskInput.load(path)
    second = AtlasReliefMaskInput.load(path)

    first["mask"][0, 0] = 0.0

    assert second["mask"][0, 0] == pytest.approx(
        128.0 / 255.0
    )


@pytest.mark.parametrize(
    "path_value",
    [
        None,
        "",
        123,
        Path("missing-mask.png"),
    ],
)
def test_rejects_invalid_or_missing_paths(path_value):
    with pytest.raises(ValueError):
        AtlasReliefMaskInput.load(path_value)


def test_rejects_unsupported_image_mode(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "palette-mask.png"

    Image.new(
        "P",
        (2, 2),
    ).save(path)

    with pytest.raises(ValueError):
        AtlasReliefMaskInput.load(path)
