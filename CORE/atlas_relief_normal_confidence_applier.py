from __future__ import annotations

import numpy as np


class AtlasReliefNormalConfidenceApplier:
    """
    Apply a soft confidence map to normal-derived gradients.

    The operation preserves gradient direction while scaling gradient
    magnitude by the confidence map. Confidence zero produces a flat normal;
    confidence one preserves the input normal.
    """

    @staticmethod
    def apply(
        normals: np.ndarray,
        *,
        confidence_map: np.ndarray,
        mask: np.ndarray | None = None,
        minimum_nz: float = 0.05,
        minimum_retention: float = 0.0,
        minimum_retention_map: np.ndarray | None = None,
    ) -> np.ndarray:
        normal_array = np.asarray(
            normals,
            dtype=np.float64,
        )

        AtlasReliefNormalConfidenceApplier._validate_normals(
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
                "minimum_nz must be finite and greater than zero"
            )

        confidence = (
            AtlasReliefNormalConfidenceApplier
            ._resolve_confidence(
                confidence_map,
                rows=rows,
                columns=columns,
            )
        )

        retention = float(
            minimum_retention
        )

        if (
            not np.isfinite(retention)
            or retention < 0.0
            or retention > 1.0
        ):
            raise ValueError(
                "minimum_retention must be finite "
                "and between 0 and 1"
            )

        if minimum_retention_map is None:
            retention_field = np.full(
                (rows, columns),
                retention,
                dtype=np.float64,
            )
        else:
            retention_field = np.asarray(
                minimum_retention_map,
                dtype=np.float64,
            )

            if retention_field.shape != (
                rows,
                columns,
            ):
                raise ValueError(
                    "minimum_retention_map must have "
                    f"shape {(rows, columns)}"
                )

            if not np.all(
                np.isfinite(retention_field)
            ):
                raise ValueError(
                    "minimum_retention_map must contain "
                    "only finite values"
                )

            if (
                np.any(retention_field < 0.0)
                or np.any(retention_field > 1.0)
            ):
                raise ValueError(
                    "minimum_retention_map values must "
                    "be between 0 and 1"
                )

            retention_field = np.ascontiguousarray(
                retention_field,
                dtype=np.float64,
            )

        effective_confidence = (
            retention_field
            + (
                1.0 - retention_field
            )
            * confidence
        )

        active_mask = (
            AtlasReliefNormalConfidenceApplier
            ._resolve_mask(
                mask,
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

        gradient_x *= effective_confidence
        gradient_y *= effective_confidence

        if active_mask is not None:
            gradient_x *= active_mask
            gradient_y *= active_mask

        result = (
            AtlasReliefNormalConfidenceApplier
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
                "normals must have shape (rows, columns, 3)"
            )

        if not np.all(
            np.isfinite(normals)
        ):
            raise ValueError(
                "normals must contain only finite values"
            )

    @staticmethod
    def _resolve_confidence(
        confidence_map: np.ndarray,
        *,
        rows: int,
        columns: int,
    ) -> np.ndarray:
        confidence = np.asarray(
            confidence_map,
            dtype=np.float64,
        )

        if confidence.shape != (
            rows,
            columns,
        ):
            raise ValueError(
                "confidence_map shape must match the normal field"
            )

        if not np.all(
            np.isfinite(confidence)
        ):
            raise ValueError(
                "confidence_map must contain only finite values"
            )

        return np.clip(
            confidence,
            0.0,
            1.0,
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
                "mask shape must match the normal field"
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
    def _gradients_to_normals(
        gradient_x: np.ndarray,
        gradient_y: np.ndarray,
    ) -> np.ndarray:
        normals = np.stack(
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
            normals,
            axis=2,
            keepdims=True,
        )

        return (
            normals
            / np.maximum(
                lengths,
                1.0e-12,
            )
        )
