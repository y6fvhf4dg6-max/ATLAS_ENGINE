from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


class AtlasReliefSemanticMaskInput:
    @staticmethod
    def _normalize_threshold(value) -> int:
        try:
            threshold = int(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "threshold must be an integer between 0 and 255"
            ) from error

        if threshold < 0 or threshold > 255:
            raise ValueError(
                "threshold must be between 0 and 255"
            )

        return threshold

    @staticmethod
    def _normalize_expected_shape(
        expected_shape,
    ) -> tuple[int, int] | None:
        if expected_shape is None:
            return None

        try:
            rows, columns = expected_shape
        except (TypeError, ValueError) as error:
            raise ValueError(
                "expected_shape must contain exactly two dimensions"
            ) from error

        rows = int(rows)
        columns = int(columns)

        if rows <= 0 or columns <= 0:
            raise ValueError(
                "expected_shape dimensions must be positive"
            )

        return rows, columns

    @classmethod
    def load(
        cls,
        path,
        *,
        threshold: int = 128,
        expected_shape=None,
    ) -> dict:
        normalized_threshold = cls._normalize_threshold(
            threshold
        )
        normalized_expected_shape = (
            cls._normalize_expected_shape(
                expected_shape
            )
        )

        image_path = Path(path)

        with Image.open(image_path) as image:
            grayscale = image.convert("L")
            values = np.asarray(
                grayscale,
                dtype=np.uint8,
            )

        shape = tuple(values.shape)

        if (
            normalized_expected_shape is not None
            and shape != normalized_expected_shape
        ):
            raise ValueError(
                "semantic mask shape does not match "
                f"expected shape {normalized_expected_shape}: "
                f"{shape}"
            )

        mask = values >= normalized_threshold

        return {
            "type": "relief_semantic_mask_input",
            "path": str(image_path),
            "shape": shape,
            "threshold": normalized_threshold,
            "mask": mask,
        }
