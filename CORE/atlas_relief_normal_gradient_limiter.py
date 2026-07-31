from __future__ import annotations

import numpy as np


class AtlasReliefNormalGradientLimiter:
    """Limit normal-derived gradient magnitudes while preserving direction.

    Intended primarily for the high-frequency detail-normal layer. Broad
    structure normals should normally bypass this limiter.

    Processing order:

    1. Convert normals to directional gradients.
    2. Resolve either an explicit or percentile-derived magnitude limit.
    3. Clip only magnitudes above that limit.
    4. Apply optional confidence weighting.
    5. Flatten output outside the optional subject mask.
    6. Convert gradients back to unit normals.
    """

    @staticmethod
    def limit(
        normals: np.ndarray,
        *,
        mask: np.ndarray | None = None,
        confidence_map: np.ndarray | None = None,
        minimum_nz: float = 0.05,
        magnitude_percentile: float = 95.0,
        maximum_gradient: float | None = None,
    ) -> np.ndarray:
        normal_array = np.asarray(
            normals,
            dtype=np.float64,
        )

        AtlasReliefNormalGradientLimiter._validate_normals(
            normal_array
        )

        rows, columns, _ = normal_array.shape

        minimum_normal_z = float(
            minimum_nz
        )

        if (
            not np.isfinite(minimum_normal_z)
            or minimum_normal_z <= 0.0
        ):
            raise ValueError(
                "minimum_nz must be finite "
                "and greater than zero"
            )

        percentile = float(
            magnitude_percentile
        )

        if (
            not np.isfinite(percentile)
            or percentile <= 0.0
            or percentile >= 100.0
        ):
            raise ValueError(
                "magnitude_percentile must be finite "
                "and strictly between 0 and 100"
            )

        explicit_limit: float | None = None

        if maximum_gradient is not None:
            explicit_limit = float(
                maximum_gradient
            )

            if (
                not np.isfinite(explicit_limit)
                or explicit_limit <= 0.0
            ):
                raise ValueError(
                    "maximum_gradient must be finite "
                    "and greater than zero"
                )

        active_mask = (
            AtlasReliefNormalGradientLimiter._resolve_mask(
                mask,
                rows=rows,
                columns=columns,
            )
        )

        confidence = (
            AtlasReliefNormalGradientLimiter._resolve_confidence(
                confidence_map,
                rows=rows,
                columns=columns,
            )
        )

        nx = normal_array[..., 0]
        ny = normal_array[..., 1]
        nz = np.maximum(
            normal_array[..., 2],
            minimum_normal_z,
        )

        gradient_x = (
            -nx / nz
        )
        gradient_y = (
            -ny / nz
        )

        magnitude = np.sqrt(
            gradient_x * gradient_x
            + gradient_y * gradient_y
        )

        if explicit_limit is None:
            selection = np.isfinite(
                magnitude
            )

            if active_mask is not None:
                selection &= (
                    active_mask > 0.0
                )

            if confidence_map is not None:
                selection &= (
                    confidence > 0.0
                )

            selected_magnitudes = magnitude[
                selection
            ]

            if selected_magnitudes.size == 0:
                limit_value = 0.0
            else:
                limit_value = float(
                    np.percentile(
                        selected_magnitudes,
                        percentile,
                    )
                )
        else:
            limit_value = explicit_limit

        if limit_value > 0.0:
            scale = np.minimum(
                1.0,
                limit_value
                / np.maximum(
                    magnitude,
                    1e-12,
                ),
            )

            gradient_x = (
                gradient_x
                * scale
            )
            gradient_y = (
                gradient_y
                * scale
            )
        else:
            gradient_x = np.zeros_like(
                gradient_x
            )
            gradient_y = np.zeros_like(
                gradient_y
            )

        gradient_x *= confidence
        gradient_y *= confidence

        if active_mask is not None:
            gradient_x *= active_mask
            gradient_y *= active_mask

        result = (
            AtlasReliefNormalGradientLimiter
            ._gradients_to_normals(
                gradient_x,
                gradient_y,
            )
        )

        return np.asarray(
            result,
            dtype=np.float64,
        )

    @staticmethod
    def _validate_normals(
        normals: np.ndarray,
    ) -> None:
        if (
            normals.ndim != 3
            or normals.shape[2] != 3
        ):
            raise ValueError(
                "normals must have shape "
                "(rows, columns, 3)"
            )

        if not np.all(
            np.isfinite(normals)
        ):
            raise ValueError(
                "normals must contain only finite values"
            )

    @staticmethod
    def _resolve_mask(
        mask: np.ndarray | None,
        *,
        rows: int,
        columns: int,
    ) -> np.ndarray | None:
        if mask is None:
            return None

        mask_array = np.asarray(
            mask,
            dtype=np.float64,
        )

        if mask_array.shape != (
            rows,
            columns,
        ):
            raise ValueError(
                "mask shape must match "
                "the normal field"
            )

        if not np.all(
            np.isfinite(mask_array)
        ):
            raise ValueError(
                "mask must contain only finite values"
            )

        return np.clip(
            mask_array,
            0.0,
            1.0,
        )

    @staticmethod
    def _resolve_confidence(
        confidence_map: np.ndarray | None,
        *,
        rows: int,
        columns: int,
    ) -> np.ndarray:
        if confidence_map is None:
            return np.ones(
                (rows, columns),
                dtype=np.float64,
            )

        confidence = np.asarray(
            confidence_map,
            dtype=np.float64,
        )

        if confidence.shape != (
            rows,
            columns,
        ):
            raise ValueError(
                "confidence_map shape must match "
                "the normal field"
            )

        if not np.all(
            np.isfinite(confidence)
        ):
            raise ValueError(
                "confidence_map must contain "
                "only finite values"
            )

        return np.clip(
            confidence,
            0.0,
            1.0,
        )

    @staticmethod
    def _gradients_to_normals(
        gradient_x: np.ndarray,
        gradient_y: np.ndarray,
    ) -> np.ndarray:
        normal_field = np.stack(
            [
                -gradient_x,
                -gradient_y,
                np.ones_like(
                    gradient_x
                ),
            ],
            axis=2,
        )

        lengths = np.linalg.norm(
            normal_field,
            axis=2,
            keepdims=True,
        )

        return (
            normal_field
            / np.maximum(
                lengths,
                1e-12,
            )
        )
