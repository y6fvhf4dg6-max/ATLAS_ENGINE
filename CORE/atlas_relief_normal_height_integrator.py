from __future__ import annotations

import numpy as np


class AtlasReliefNormalHeightIntegrator:
    """Integrate a surface-normal field into a scalar height map.

    Input normal convention:

        X = image-right
        Y = image-down
        Z = toward the camera

    For outward-facing normals:

        dz/dx = -nx / nz
        dz/dy = -ny / nz

    Without a confidence map, integration uses the original frequency-domain
    least-squares reconstruction.

    When a confidence map is supplied, the confidence values scale the
    directional gradients before integration. This prevents low-confidence
    portrait regions from creating artificial height depressions after the
    surface has already been reconstructed.
    """

    @staticmethod
    def integrate(
        normals: np.ndarray,
        *,
        mask: np.ndarray | None = None,
        confidence_map: np.ndarray | None = None,
        minimum_nz: float = 0.05,
        sample_spacing_mm: float = 1.0,
        normalize_output: bool = True,
    ) -> np.ndarray:
        normal_array = np.asarray(
            normals,
            dtype=np.float64,
        )

        if (
            normal_array.ndim != 3
            or normal_array.shape[2] != 3
        ):
            raise ValueError(
                "normals must have shape "
                "(rows, columns, 3)"
            )

        if not np.all(
            np.isfinite(normal_array)
        ):
            raise ValueError(
                "normals must contain only finite values"
            )

        if (
            minimum_nz <= 0.0
            or not np.isfinite(minimum_nz)
        ):
            raise ValueError(
                "minimum_nz must be finite "
                "and greater than zero"
            )

        sample_spacing = float(sample_spacing_mm)
        if (
            not np.isfinite(sample_spacing)
            or sample_spacing <= 0.0
        ):
            raise ValueError(
                "sample_spacing_mm must be finite "
                "and greater than zero"
            )

        rows, columns, _ = normal_array.shape

        (
            valid_mask,
            output_mask,
        ) = AtlasReliefNormalHeightIntegrator._resolve_mask(
            mask,
            rows=rows,
            columns=columns,
        )

        confidence = (
            AtlasReliefNormalHeightIntegrator
            ._resolve_confidence_map(
                confidence_map,
                rows=rows,
                columns=columns,
            )
        )

        nx = normal_array[..., 0]
        ny = normal_array[..., 1]
        nz = normal_array[..., 2]

        safe_nz = np.maximum(
            nz,
            minimum_nz,
        )

        gradient_x = -nx / safe_nz
        gradient_y = -ny / safe_nz

        if confidence is None:
            height = (
                AtlasReliefNormalHeightIntegrator
                ._integrate_unweighted_gradients(
                    gradient_x,
                    gradient_y,
                    valid_mask=valid_mask,
                    sample_spacing=sample_spacing,
                )
            )
        else:
            effective_confidence = (
                confidence
                * valid_mask.astype(np.float64)
            )

            weighted_gradient_x = (
                gradient_x
                * effective_confidence
            )
            weighted_gradient_y = (
                gradient_y
                * effective_confidence
            )

            height = (
                AtlasReliefNormalHeightIntegrator
                ._integrate_confidence_weighted_gradients(
                    weighted_gradient_x,
                    weighted_gradient_y,
                    sample_spacing=sample_spacing,
                )
            )

        height -= float(
            np.mean(height[valid_mask])
        )

        if normalize_output:
            height = (
                AtlasReliefNormalHeightIntegrator
                ._normalize_height(
                    height,
                    valid_mask=valid_mask,
                )
            )

        if output_mask is not None:
            height = np.where(
                output_mask,
                height,
                0.0,
            )

        return np.asarray(
            height,
            dtype=np.float64,
        )

    @staticmethod
    def _resolve_mask(
        mask: np.ndarray | None,
        *,
        rows: int,
        columns: int,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        if mask is None:
            return (
                np.ones(
                    (rows, columns),
                    dtype=bool,
                ),
                None,
            )

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

        valid_mask = mask_array > 0.0

        if not np.any(valid_mask):
            raise ValueError(
                "mask must contain at least "
                "one active pixel"
            )

        return (
            valid_mask,
            valid_mask,
        )

    @staticmethod
    def _resolve_confidence_map(
        confidence_map: np.ndarray | None,
        *,
        rows: int,
        columns: int,
    ) -> np.ndarray | None:
        if confidence_map is None:
            return None

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
    def _integrate_unweighted_gradients(
        gradient_x: np.ndarray,
        gradient_y: np.ndarray,
        *,
        valid_mask: np.ndarray,
        sample_spacing: float,
    ) -> np.ndarray:
        mean_gradient_x = float(
            np.mean(
                gradient_x[valid_mask]
            )
        )
        mean_gradient_y = float(
            np.mean(
                gradient_y[valid_mask]
            )
        )

        residual_gradient_x = (
            gradient_x
            - mean_gradient_x
        )
        residual_gradient_y = (
            gradient_y
            - mean_gradient_y
        )

        residual_height = (
            AtlasReliefNormalHeightIntegrator
            ._integrate_zero_mean_gradients(
                residual_gradient_x,
                residual_gradient_y,
                sample_spacing=sample_spacing,
            )
        )

        rows, columns = gradient_x.shape

        row_coordinates, column_coordinates = (
            np.mgrid[
                0:rows,
                0:columns,
            ]
        )

        plane_height = (
            mean_gradient_x
            * column_coordinates
            * sample_spacing
            + mean_gradient_y
            * row_coordinates
            * sample_spacing
        )

        return (
            residual_height
            + plane_height
        )

    @staticmethod
    def _integrate_confidence_weighted_gradients(
        gradient_x: np.ndarray,
        gradient_y: np.ndarray,
        *,
        sample_spacing: float,
    ) -> np.ndarray:
        """Integrate locally weighted gradients without global plane leakage.

        Cumulative directional reconstructions preserve zero-gradient regions:
        if confidence is zero outside a face region, those outside regions stay
        flat rather than inheriting a global mean plane.

        The two directional reconstructions are combined according to their
        gradient energy. A purely horizontal or vertical field therefore
        remains exact.
        """

        rows, columns = gradient_x.shape

        height_from_x = np.zeros(
            (rows, columns),
            dtype=np.float64,
        )

        if columns > 1:
            horizontal_steps = 0.5 * (
                gradient_x[:, :-1]
                + gradient_x[:, 1:]
            )

            height_from_x[:, 1:] = np.cumsum(
                horizontal_steps * sample_spacing,
                axis=1,
            )

        height_from_y = np.zeros(
            (rows, columns),
            dtype=np.float64,
        )

        if rows > 1:
            vertical_steps = 0.5 * (
                gradient_y[:-1, :]
                + gradient_y[1:, :]
            )

            height_from_y[1:, :] = np.cumsum(
                vertical_steps * sample_spacing,
                axis=0,
            )

        energy_x = float(
            np.mean(
                np.abs(gradient_x)
            )
        )
        energy_y = float(
            np.mean(
                np.abs(gradient_y)
            )
        )

        total_energy = (
            energy_x
            + energy_y
        )

        if total_energy <= 1e-15:
            return np.zeros(
                (rows, columns),
                dtype=np.float64,
            )

        weight_x = (
            energy_x
            / total_energy
        )
        weight_y = (
            energy_y
            / total_energy
        )

        return (
            weight_x * height_from_x
            + weight_y * height_from_y
        )

    @staticmethod
    def _normalize_height(
        height: np.ndarray,
        *,
        valid_mask: np.ndarray,
    ) -> np.ndarray:
        valid_values = height[valid_mask]

        minimum_height = float(
            np.min(valid_values)
        )
        maximum_height = float(
            np.max(valid_values)
        )

        height_range = (
            maximum_height
            - minimum_height
        )

        if height_range <= 1e-12:
            return np.zeros_like(
                height,
                dtype=np.float64,
            )

        return (
            height
            - minimum_height
        ) / height_range

    @staticmethod
    def _integrate_zero_mean_gradients(
        gradient_x: np.ndarray,
        gradient_y: np.ndarray,
        *,
        sample_spacing: float,
    ) -> np.ndarray:
        rows, columns = gradient_x.shape

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

        frequency_x = frequency_x / sample_spacing
        frequency_y = frequency_y / sample_spacing

        omega_x, omega_y = np.meshgrid(
            frequency_x,
            frequency_y,
        )

        transformed_gradient_x = (
            np.fft.fft2(gradient_x)
        )
        transformed_gradient_y = (
            np.fft.fft2(gradient_y)
        )

        denominator = (
            omega_x * omega_x
            + omega_y * omega_y
        )

        transformed_height = np.zeros(
            gradient_x.shape,
            dtype=np.complex128,
        )

        nonzero_frequency = (
            denominator > 0.0
        )

        transformed_height[
            nonzero_frequency
        ] = (
            -1j
            * omega_x[nonzero_frequency]
            * transformed_gradient_x[
                nonzero_frequency
            ]
            - 1j
            * omega_y[nonzero_frequency]
            * transformed_gradient_y[
                nonzero_frequency
            ]
        ) / denominator[
            nonzero_frequency
        ]

        transformed_height[0, 0] = 0.0

        return np.fft.ifft2(
            transformed_height
        ).real.astype(np.float64)
