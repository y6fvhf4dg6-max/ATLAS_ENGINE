from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from PIL import ImageOps


class AtlasReliefMaskInput:
    """
    Loads an external mask image as a deterministic
    normalized float64 array in the 0.0..1.0 range.
    """

    SUPPORTED_MODES = {
        "L",
        "RGB",
        "RGBA",
    }

    @staticmethod
    def load(
        path_value: Any,
        *,
        use_alpha: bool = False,
    ) -> dict[str, Any]:
        source_path = (
            AtlasReliefMaskInput
            ._validate_path(path_value)
        )

        try:
            with Image.open(source_path) as image:
                oriented = ImageOps.exif_transpose(image)
                source_mode = oriented.mode

                if (
                    source_mode
                    not in AtlasReliefMaskInput
                    .SUPPORTED_MODES
                ):
                    raise ValueError(
                        "Unsupported mask image mode."
                    )

                if use_alpha:
                    if source_mode != "RGBA":
                        raise ValueError(
                            "use_alpha requires an "
                            "RGBA image."
                        )

                    alpha = np.asarray(
                        oriented.getchannel("A"),
                        dtype=np.float64,
                    )

                    mask = alpha / 255.0
                elif source_mode == "L":
                    mask = np.asarray(
                        oriented,
                        dtype=np.float64,
                    ) / 255.0
                else:
                    rgb = np.asarray(
                        oriented.convert("RGB"),
                        dtype=np.float64,
                    ) / 255.0

                    mask = (
                        0.2126 * rgb[..., 0]
                        + 0.7152 * rgb[..., 1]
                        + 0.0722 * rgb[..., 2]
                    )

                width_pixels, height_pixels = (
                    oriented.size
                )

        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(
                "Mask image could not be loaded."
            ) from exc

        mask = np.clip(
            mask,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=True,
        )

        return {
            "type": "relief_mask_input",
            "source_path": str(source_path),
            "source_mode": source_mode,
            "width_pixels": int(width_pixels),
            "height_pixels": int(height_pixels),
            "use_alpha": bool(use_alpha),
            "mask": mask,
        }

    @staticmethod
    def _validate_path(
        path_value: Any,
    ) -> Path:
        if not isinstance(
            path_value,
            (
                str,
                Path,
            ),
        ):
            raise ValueError(
                "Mask path must be a string "
                "or pathlib.Path."
            )

        if (
            isinstance(path_value, str)
            and not path_value.strip()
        ):
            raise ValueError(
                "Mask path must not be empty."
            )

        path = Path(path_value).expanduser()

        if not path.is_file():
            raise ValueError(
                "Mask image file does not exist."
            )

        return path.resolve()
