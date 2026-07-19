from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from CORE.atlas_relief_image_input import (
    AtlasReliefImageInput,
)


def _save_image(
    path: Path,
    *,
    mode: str,
    data,
    size: tuple[int, int],
    exif=None,
) -> None:
    image = Image.new(
        mode,
        size,
    )
    image.putdata(data)

    save_kwargs = {}

    if exif is not None:
        save_kwargs["exif"] = exif

    image.save(
        path,
        **save_kwargs,
    )


def test_loads_grayscale_image_as_float64_luminance(
    tmp_path,
):
    path = tmp_path / "grayscale.png"

    _save_image(
        path,
        mode="L",
        size=(2, 2),
        data=[
            0,
            64,
            128,
            255,
        ],
    )

    result = AtlasReliefImageInput.load(path)

    assert result["luminance"].dtype == np.float64
    assert result["luminance"].shape == (2, 2)
    assert result["source_mode"] == "L"
    assert result["width_px"] == 2
    assert result["height_px"] == 2

    assert result["luminance"][0, 0] == 0.0
    assert result["luminance"][1, 1] == 1.0


def test_rgb_luminance_uses_linear_light_rec709(
    tmp_path,
):
    path = tmp_path / "rgb.png"

    _save_image(
        path,
        mode="RGB",
        size=(3, 1),
        data=[
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
        ],
    )

    result = AtlasReliefImageInput.load(path)
    luminance = result["luminance"]

    assert luminance.shape == (1, 3)
    assert luminance[0, 0] == pytest.approx(
        0.2126
    )
    assert luminance[0, 1] == pytest.approx(
        0.7152
    )
    assert luminance[0, 2] == pytest.approx(
        0.0722
    )


def test_mid_gray_is_linearized_before_luminance(
    tmp_path,
):
    path = tmp_path / "mid-gray.png"

    _save_image(
        path,
        mode="RGB",
        size=(1, 1),
        data=[
            (128, 128, 128),
        ],
    )

    result = AtlasReliefImageInput.load(path)

    srgb = 128.0 / 255.0
    expected = (
        (srgb + 0.055)
        / 1.055
    ) ** 2.4

    assert result["luminance"][0, 0] == pytest.approx(
        expected
    )


def test_rgba_alpha_composites_over_background_luminance(
    tmp_path,
):
    path = tmp_path / "alpha.png"

    _save_image(
        path,
        mode="RGBA",
        size=(2, 1),
        data=[
            (255, 255, 255, 255),
            (255, 255, 255, 0),
        ],
    )

    result = AtlasReliefImageInput.load(
        path,
        alpha_background_luminance=0.25,
    )

    assert result["luminance"][0, 0] == pytest.approx(
        1.0
    )
    assert result["luminance"][0, 1] == pytest.approx(
        0.25
    )
    assert result["has_alpha"] is True


def test_rgba_partial_alpha_composites_in_linear_space(
    tmp_path,
):
    path = tmp_path / "partial-alpha.png"

    _save_image(
        path,
        mode="RGBA",
        size=(1, 1),
        data=[
            (255, 255, 255, 128),
        ],
    )

    result = AtlasReliefImageInput.load(
        path,
        alpha_background_luminance=0.0,
    )

    assert result["luminance"][0, 0] == pytest.approx(
        128.0 / 255.0
    )


def test_exif_orientation_is_applied(
    tmp_path,
):
    path = tmp_path / "oriented.jpg"

    image = Image.new(
        "RGB",
        (2, 3),
    )
    image.putdata(
        [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 255),
            (0, 0, 0),
            (128, 128, 128),
        ]
    )

    exif = image.getexif()
    exif[274] = 6

    image.save(
        path,
        quality=100,
        subsampling=0,
        exif=exif,
    )

    result = AtlasReliefImageInput.load(path)

    assert result["width_px"] == 3
    assert result["height_px"] == 2
    assert result["orientation_applied"] is True


def test_load_is_deterministic(
    tmp_path,
):
    path = tmp_path / "deterministic.png"

    _save_image(
        path,
        mode="RGB",
        size=(2, 2),
        data=[
            (10, 20, 30),
            (40, 50, 60),
            (70, 80, 90),
            (100, 110, 120),
        ],
    )

    first = AtlasReliefImageInput.load(path)
    second = AtlasReliefImageInput.load(path)

    assert np.array_equal(
        first["luminance"],
        second["luminance"],
    )


def test_result_luminance_is_independent_between_loads(
    tmp_path,
):
    path = tmp_path / "independent.png"

    _save_image(
        path,
        mode="L",
        size=(2, 2),
        data=[
            0,
            64,
            128,
            255,
        ],
    )

    first = AtlasReliefImageInput.load(path)
    first["luminance"][0, 0] = 0.75

    second = AtlasReliefImageInput.load(path)

    assert second["luminance"][0, 0] == 0.0


@pytest.mark.parametrize(
    "value",
    [
        -0.01,
        1.01,
        float("nan"),
        float("inf"),
        "invalid",
        None,
    ],
)
def test_rejects_invalid_alpha_background_luminance(
    tmp_path,
    value,
):
    path = tmp_path / "alpha-background.png"

    _save_image(
        path,
        mode="RGBA",
        size=(1, 1),
        data=[
            (255, 255, 255, 0),
        ],
    )

    with pytest.raises(ValueError):
        AtlasReliefImageInput.load(
            path,
            alpha_background_luminance=value,
        )


def test_rejects_missing_file(tmp_path):
    with pytest.raises(
        ValueError,
        match="Image file does not exist",
    ):
        AtlasReliefImageInput.load(
            tmp_path / "missing.png"
        )


def test_rejects_directory_path(tmp_path):
    with pytest.raises(
        ValueError,
        match="Image path must be a file",
    ):
        AtlasReliefImageInput.load(tmp_path)


def test_rejects_corrupt_image(tmp_path):
    path = tmp_path / "corrupt.png"
    path.write_bytes(b"not-an-image")

    with pytest.raises(
        ValueError,
        match="Unable to read image file",
    ):
        AtlasReliefImageInput.load(path)
