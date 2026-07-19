from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import (
    Image,
    ImageOps,
    UnidentifiedImageError,
)


class AtlasReliefImageInput:
    """
    Deterministic image input layer for the ATLAS
    Relief Engine.

    Loads supported raster images and converts their
    pixels into linear-light Rec.709 luminance values.

    This class does not interpret luminance as depth.
    """

    _SUPPORTED_MODES = {
        "L",
        "RGB",
        "RGBA",
    }

    @staticmethod
    def load(
        image_path: str | Path,
        *,
        alpha_background_luminance: float = 1.0,
    ) -> dict[str, Any]:
        path = Path(image_path)

        background_luminance = (
            AtlasReliefImageInput
            ._validate_background_luminance(
                alpha_background_luminance
            )
        )

        if not path.exists():
            raise ValueError(
                "Image file does not exist."
            )

        if not path.is_file():
            raise ValueError(
                "Image path must be a file."
            )

        try:
            with Image.open(path) as source:
                source.load()

                source_mode = source.mode
                source_format = source.format

                orientation = (
                    source.getexif().get(274, 1)
                )
                orientation_applied = (
                    orientation not in (
                        None,
                        1,
                    )
                )

                oriented = ImageOps.exif_transpose(
                    source
                )

                if (
                    oriented.mode
                    not in (
                        AtlasReliefImageInput
                        ._SUPPORTED_MODES
                    )
                ):
                    raise ValueError(
                        "Unsupported image mode: "
                        f"{oriented.mode}."
                    )

                luminance, has_alpha = (
                    AtlasReliefImageInput
                    ._to_luminance(
                        oriented,
                        alpha_background_luminance=(
                            background_luminance
                        ),
                    )
                )

                width_px, height_px = oriented.size

        except ValueError:
            raise
        except (
            OSError,
            UnidentifiedImageError,
        ) as exc:
            raise ValueError(
                "Unable to read image file."
            ) from exc

        if (
            luminance.ndim != 2
            or luminance.shape
            != (
                height_px,
                width_px,
            )
        ):
            raise ValueError(
                "Image luminance conversion produced "
                "an invalid shape."
            )

        if not np.isfinite(luminance).all():
            raise ValueError(
                "Image luminance contains non-finite "
                "values."
            )

        luminance = np.clip(
            luminance,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=True,
        )

        return {
            "type": "relief_image_input",
            "source_path": str(path),
            "source_format": source_format,
            "source_mode": source_mode,
            "width_px": int(width_px),
            "height_px": int(height_px),
            "has_alpha": has_alpha,
            "orientation_applied": (
                orientation_applied
            ),
            "alpha_background_luminance": (
                background_luminance
            ),
            "luminance": luminance,
        }

    @staticmethod
    def _validate_background_luminance(
        value: Any,
    ) -> float:
        try:
            numeric_value = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "alpha_background_luminance must "
                "be numeric."
            ) from exc

        if not math.isfinite(numeric_value):
            raise ValueError(
                "alpha_background_luminance must "
                "be finite."
            )

        if not 0.0 <= numeric_value <= 1.0:
            raise ValueError(
                "alpha_background_luminance must "
                "be within the 0.0..1.0 range."
            )

        return numeric_value

    @staticmethod
    def _to_luminance(
        image: Image.Image,
        *,
        alpha_background_luminance: float,
    ) -> tuple[np.ndarray, bool]:
        if image.mode == "L":
            grayscale = np.asarray(
                image,
                dtype=np.float64,
            )

            return (
                grayscale / 255.0,
                False,
            )

        pixels = np.asarray(
            image,
            dtype=np.float64,
        )

        rgb_srgb = pixels[
            ...,
            :3,
        ] / 255.0

        rgb_linear = (
            AtlasReliefImageInput
            ._srgb_to_linear(
                rgb_srgb
            )
        )

        luminance = (
            rgb_linear[..., 0] * 0.2126
            + rgb_linear[..., 1] * 0.7152
            + rgb_linear[..., 2] * 0.0722
        )

        if image.mode == "RGBA":
            alpha = (
                pixels[..., 3]
                / 255.0
            )

            luminance = (
                luminance * alpha
                + alpha_background_luminance
                * (1.0 - alpha)
            )

            return (
                luminance,
                True,
            )

        return (
            luminance,
            False,
        )

    @staticmethod
    def _srgb_to_linear(
        values: np.ndarray,
    ) -> np.ndarray:
        return np.where(
            values <= 0.04045,
            values / 12.92,
            (
                (values + 0.055)
                / 1.055
            ) ** 2.4,
        )
