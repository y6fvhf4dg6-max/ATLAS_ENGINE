from __future__ import annotations

import numpy as np


class AtlasReliefScreenedNormalIntegrator:
    """Reconstruct height from normals while remaining anchored to a base map.

    The reconstruction minimizes two competing objectives:

    - follow the directional gradients derived from the normal field;
    - remain close to ``anchor_height``.

    ``screening_strength`` controls the second objective. Larger values keep
    the result closer to the anchor. ``confidence_map`` controls where the
    normal-derived gradients are trusted.

    Input normal convention:

        X = image-right
        Y = image-down
        Z = toward the camera

    Therefore:

        dz/dx = -nx / nz
        dz/dy = -ny / nz
    """

    @staticmethod
    def integrate(
        normals: np.ndarray,
        anchor_height: np.ndarray,
        *,
        mask: np.ndarray | None = None,
        confidence_map: np.ndarray | None = None,
        screening_strength: float = 1.0,
        minimum_nz: float = 0.05,
        normalize_output: bool = True,
    ) -> np.ndarray:
        normal_array = np.asarray(
            normals,
            dtype=np.float64,
        )
        anchor = np.asarray(
            anchor_height,
            dtype=np.float64,
        )

        AtlasReliefScreenedNormalIntegrator._validate_normals(
            normal_array
        )

        rows, columns, _ = normal_array.shape

        AtlasReliefScreenedNormalIntegrator._validate_anchor(
            anchor,
            rows=rows,
            columns=columns,
        )

        screening = float(
            screening_strength
        )

        if (
            not np.isfinite(screening)
            or screening <= 0.0
        ):
            raise ValueError(
                "screening_strength must be finite "
                "and greater than zero"
            )

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

        valid_mask, output_mask = (
            AtlasReliefScreenedNormalIntegrator._resolve_mask(
                mask,
                rows=rows,
                columns=columns,
            )
        )

        confidence = (
            AtlasReliefScreenedNormalIntegrator._resolve_confidence(
                confidence_map,
                rows=rows,
                columns=columns,
            )
        )

        confidence *= valid_mask.astype(
            np.float64
        )

        if not np.any(
            confidence > 0.0
        ):
            result = anchor.copy()

            if output_mask is not None:
                result = np.where(
                    output_mask,
                    result,
                    0.0,
                )

            return np.asarray(
                result,
                dtype=np.float64,
            )

        nx = normal_array[..., 0]
        ny = normal_array[..., 1]
        nz = normal_array[..., 2]

        safe_nz = np.maximum(
            nz,
            minimum_normal_z,
        )

        gradient_x = (
            -nx / safe_nz
        ) * confidence

        gradient_y = (
            -ny / safe_nz
        ) * confidence

        result = (
            AtlasReliefScreenedNormalIntegrator
            ._solve_screened_poisson(
                gradient_x,
                gradient_y,
                anchor,
                screening_strength=screening,
            )
        )

        if normalize_output:
            result = (
                AtlasReliefScreenedNormalIntegrator
                ._normalize_result(
                    result,
                    valid_mask=valid_mask,
                )
            )

        if output_mask is not None:
            result = np.where(
                output_mask,
                result,
                0.0,
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
    def _validate_anchor(
        anchor_height: np.ndarray,
        *,
        rows: int,
        columns: int,
    ) -> None:
        if anchor_height.shape != (
            rows,
            columns,
        ):
            raise ValueError(
                "anchor_height shape must match "
                "the normal field"
            )

        if not np.all(
            np.isfinite(anchor_height)
        ):
            raise ValueError(
                "anchor_height must contain "
                "only finite values"
            )

    @staticmethod
    def _resolve_mask(
        mask: np.ndarray | None,
        *,
        rows: int,
        columns: int,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        if mask is None:
            valid = np.ones(
                (rows, columns),
                dtype=bool,
            )

            return valid, None

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

        valid = mask_array > 0.0

        if not np.any(valid):
            raise ValueError(
                "mask must contain at least "
                "one active pixel"
            )

        return valid, valid

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
    def _solve_screened_poisson(
        gradient_x: np.ndarray,
        gradient_y: np.ndarray,
        anchor_height: np.ndarray,
        *,
        screening_strength: float,
    ) -> np.ndarray:
        """Solve the screened Poisson system in the frequency domain.

        The zero-frequency component is controlled by the anchor, preventing
        the arbitrary global offset found in unscreened Poisson integration.
        """

        rows, columns = anchor_height.shape

        frequency_x = (
            2.0
            * np.pi
            * np.fft.fftfreq(columns)
        )
        frequency_y = (
            2.0
            * np.pi
            * np.fft.fftfreq(rows)
        )

        omega_x, omega_y = np.meshgrid(
            frequency_x,
            frequency_y,
        )

        gradient_x_fft = np.fft.fft2(
            gradient_x
        )
        gradient_y_fft = np.fft.fft2(
            gradient_y
        )
        anchor_fft = np.fft.fft2(
            anchor_height
        )

        gradient_divergence_fft = (
            -1j
            * omega_x
            * gradient_x_fft
            - 1j
            * omega_y
            * gradient_y_fft
        )

        denominator = (
            omega_x * omega_x
            + omega_y * omega_y
            + screening_strength
        )

        height_fft = (
            gradient_divergence_fft
            + screening_strength
            * anchor_fft
        ) / denominator

        return np.fft.ifft2(
            height_fft
        ).real.astype(
            np.float64
        )

    @staticmethod
    def _normalize_result(
        result: np.ndarray,
        *,
        valid_mask: np.ndarray,
    ) -> np.ndarray:
        active_values = result[
            valid_mask
        ]

        minimum = float(
            np.min(active_values)
        )
        maximum = float(
            np.max(active_values)
        )

        value_range = (
            maximum
            - minimum
        )

        if value_range <= 1e-12:
            return np.zeros_like(
                result,
                dtype=np.float64,
            )

        return (
            result
            - minimum
        ) / value_range
