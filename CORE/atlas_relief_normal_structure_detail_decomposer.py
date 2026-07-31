from __future__ import annotations

import numbers

import numpy as np


class AtlasReliefNormalStructureDetailDecomposer:
    """Split a normal field into broad structure and residual detail layers.

    Decomposition is performed in gradient space:

    1. Convert normals to directional gradients.
    2. Smooth gradients to obtain the broad structure layer.
    3. Subtract structure gradients from input gradients to obtain detail.
    4. Convert both gradient layers back to unit normals.

    The two output gradient fields sum to the original input gradient field
    within numerical precision.
    """

    @staticmethod
    def decompose(
        normals: np.ndarray,
        *,
        mask: np.ndarray | None = None,
        structure_radius: int = 5,
        minimum_nz: float = 0.05,
    ) -> tuple[np.ndarray, np.ndarray]:
        normal_array = np.asarray(
            normals,
            dtype=np.float64,
        )

        AtlasReliefNormalStructureDetailDecomposer._validate_normals(
            normal_array
        )

        radius = (
            AtlasReliefNormalStructureDetailDecomposer
            ._validate_structure_radius(
                structure_radius
            )
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

        rows, columns, _ = normal_array.shape

        active_mask = (
            AtlasReliefNormalStructureDetailDecomposer
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

        input_gradient_x = (
            -nx / nz
        )
        input_gradient_y = (
            -ny / nz
        )

        if active_mask is None:
            structure_gradient_x = (
                AtlasReliefNormalStructureDetailDecomposer
                ._box_blur(
                    input_gradient_x,
                    radius=radius,
                )
            )
            structure_gradient_y = (
                AtlasReliefNormalStructureDetailDecomposer
                ._box_blur(
                    input_gradient_y,
                    radius=radius,
                )
            )
        else:
            structure_gradient_x = (
                AtlasReliefNormalStructureDetailDecomposer
                ._masked_box_blur(
                    input_gradient_x,
                    active_mask,
                    radius=radius,
                )
            )
            structure_gradient_y = (
                AtlasReliefNormalStructureDetailDecomposer
                ._masked_box_blur(
                    input_gradient_y,
                    active_mask,
                    radius=radius,
                )
            )

        detail_gradient_x = (
            input_gradient_x
            - structure_gradient_x
        )
        detail_gradient_y = (
            input_gradient_y
            - structure_gradient_y
        )

        structure_normals = (
            AtlasReliefNormalStructureDetailDecomposer
            ._gradients_to_normals(
                structure_gradient_x,
                structure_gradient_y,
            )
        )

        detail_normals = (
            AtlasReliefNormalStructureDetailDecomposer
            ._gradients_to_normals(
                detail_gradient_x,
                detail_gradient_y,
            )
        )

        if active_mask is not None:
            outside = (
                active_mask <= 0.0
            )

            structure_normals[outside, 0] = 0.0
            structure_normals[outside, 1] = 0.0
            structure_normals[outside, 2] = 1.0

            detail_normals[outside, 0] = 0.0
            detail_normals[outside, 1] = 0.0
            detail_normals[outside, 2] = 1.0

        return (
            np.asarray(
                structure_normals,
                dtype=np.float64,
            ),
            np.asarray(
                detail_normals,
                dtype=np.float64,
            ),
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
    def _validate_structure_radius(
        structure_radius: int,
    ) -> int:
        if (
            isinstance(
                structure_radius,
                bool,
            )
            or not isinstance(
                structure_radius,
                numbers.Integral,
            )
        ):
            raise ValueError(
                "structure_radius must be "
                "a positive integer"
            )

        radius = int(
            structure_radius
        )

        if radius <= 0:
            raise ValueError(
                "structure_radius must be "
                "a positive integer"
            )

        return radius

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

        return normals / np.maximum(
            lengths,
            1e-12,
        )

    @staticmethod
    def _masked_box_blur(
        values: np.ndarray,
        mask: np.ndarray,
        *,
        radius: int,
    ) -> np.ndarray:
        weighted_values = (
            values
            * mask
        )

        blurred_values = (
            AtlasReliefNormalStructureDetailDecomposer
            ._box_blur(
                weighted_values,
                radius=radius,
            )
        )

        blurred_weights = (
            AtlasReliefNormalStructureDetailDecomposer
            ._box_blur(
                mask,
                radius=radius,
            )
        )

        result = np.zeros_like(
            values,
            dtype=np.float64,
        )

        valid = (
            blurred_weights > 1e-12
        )

        result[valid] = (
            blurred_values[valid]
            / blurred_weights[valid]
        )

        return result

    @staticmethod
    def _box_blur(
        values: np.ndarray,
        *,
        radius: int,
    ) -> np.ndarray:
        kernel_size = (
            2 * radius + 1
        )

        padded = np.pad(
            values,
            (
                (radius, radius),
                (radius, radius),
            ),
            mode="edge",
        )

        integral = np.pad(
            padded,
            (
                (1, 0),
                (1, 0),
            ),
            mode="constant",
            constant_values=0.0,
        )

        integral = np.cumsum(
            np.cumsum(
                integral,
                axis=0,
            ),
            axis=1,
        )

        window_sum = (
            integral[
                kernel_size:,
                kernel_size:,
            ]
            - integral[
                :-kernel_size,
                kernel_size:,
            ]
            - integral[
                kernel_size:,
                :-kernel_size,
            ]
            + integral[
                :-kernel_size,
                :-kernel_size,
            ]
        )

        return (
            window_sum
            / float(
                kernel_size * kernel_size
            )
        )
