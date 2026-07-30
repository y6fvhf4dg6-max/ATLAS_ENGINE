from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import numpy as np


class AtlasReliefPreprocessorChain:
    @staticmethod
    def apply(
        values: Any,
        *,
        preprocessors: Iterable[
            Callable[[np.ndarray], Any]
        ],
    ) -> np.ndarray:
        source = np.asarray(
            values,
            dtype=np.float64,
        )

        if source.ndim != 2:
            raise ValueError(
                "values must be a two-dimensional array."
            )

        if source.size == 0:
            raise ValueError(
                "values must not be empty."
            )

        if not np.all(np.isfinite(source)):
            raise ValueError(
                "values must contain only finite values."
            )

        result = source.copy()
        expected_shape = result.shape

        for index, preprocessor in enumerate(
            preprocessors
        ):
            if not callable(preprocessor):
                raise ValueError(
                    "each preprocessor must be callable."
                )

            processed = np.asarray(
                preprocessor(result),
                dtype=np.float64,
            )

            if processed.shape != expected_shape:
                raise ValueError(
                    "preprocessors must preserve image shape."
                )

            if not np.all(np.isfinite(processed)):
                raise ValueError(
                    "preprocessor output must contain only "
                    "finite values."
                )

            result = processed.copy()

        return result
