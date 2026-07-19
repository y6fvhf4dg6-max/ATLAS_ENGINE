from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


DEFAULT_HEIGHT = 48
DEFAULT_WIDTH = 40


def build_synthetic_portrait_arrays(
    *,
    height: int = DEFAULT_HEIGHT,
    width: int = DEFAULT_WIDTH,
) -> dict[str, np.ndarray]:
    if height < 2:
        raise ValueError(
            "height must be at least 2."
        )

    if width < 2:
        raise ValueError(
            "width must be at least 2."
        )

    y, x = np.mgrid[
        0:height,
        0:width,
    ].astype(np.float64)

    center_x = float(width) * 0.50
    center_y = float(height) * (
        22.0 / 48.0
    )

    face = np.exp(
        -(
            (
                (
                    x - center_x
                )
                / (
                    float(width)
                    * 0.25
                )
            )
            ** 2
            + (
                (
                    y - center_y
                )
                / (
                    float(height)
                    * (
                        15.0 / 48.0
                    )
                )
            )
            ** 2
        )
    )

    nose = np.exp(
        -(
            (
                (
                    x - center_x
                )
                / (
                    float(width)
                    * (
                        2.8 / 40.0
                    )
                )
            )
            ** 2
            + (
                (
                    y
                    - float(height)
                    * (
                        23.0 / 48.0
                    )
                )
                / (
                    float(height)
                    * (
                        5.0 / 48.0
                    )
                )
            )
            ** 2
        )
    )

    eye_y = float(height) * (
        18.0 / 48.0
    )

    left_eye_x = float(width) * (
        15.5 / 40.0
    )

    right_eye_x = float(width) * (
        24.5 / 40.0
    )

    eye_scale_x = float(width) * (
        2.0 / 40.0
    )

    eye_scale_y = float(height) * (
        1.2 / 48.0
    )

    eyes = (
        np.exp(
            -(
                (
                    (
                        x - left_eye_x
                    )
                    / eye_scale_x
                )
                ** 2
                + (
                    (
                        y - eye_y
                    )
                    / eye_scale_y
                )
                ** 2
            )
        )
        + np.exp(
            -(
                (
                    (
                        x - right_eye_x
                    )
                    / eye_scale_x
                )
                ** 2
                + (
                    (
                        y - eye_y
                    )
                    / eye_scale_y
                )
                ** 2
            )
        )
    )

    luminance = np.clip(
        0.18
        + 0.62 * face
        + 0.18 * nose
        - 0.12 * eyes,
        0.0,
        1.0,
    )

    mask = np.clip(
        (face - 0.12) / 0.55,
        0.0,
        1.0,
    )

    return {
        "luminance": luminance,
        "mask": mask,
    }


def write_synthetic_portrait_fixture(
    directory: Any,
    *,
    image_filename: str = (
        "synthetic_portrait.png"
    ),
    mask_filename: str = (
        "synthetic_portrait_mask.png"
    ),
    height: int = DEFAULT_HEIGHT,
    width: int = DEFAULT_WIDTH,
) -> dict[str, Path]:
    output_directory = Path(directory)

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    arrays = (
        build_synthetic_portrait_arrays(
            height=height,
            width=width,
        )
    )

    image_path = (
        output_directory / image_filename
    )

    mask_path = (
        output_directory / mask_filename
    )

    Image.fromarray(
        np.rint(
            arrays["luminance"] * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(image_path)

    Image.fromarray(
        np.rint(
            arrays["mask"] * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(mask_path)

    return {
        "image_path": image_path,
        "mask_path": mask_path,
    }
