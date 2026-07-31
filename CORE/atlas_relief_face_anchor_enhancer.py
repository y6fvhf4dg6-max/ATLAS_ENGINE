from __future__ import annotations

from collections.abc import Sequence

import numpy as np


class AtlasReliefFaceAnchorEnhancer:
    """Increase low/mid-frequency facial contrast inside a controlled region.

    The enhancer performs a local unsharp-mask style operation over the anchor
    height map. Enhancement is limited by:

    - the subject mask,
    - optional inclusive face bounds,
    - a soft facial envelope,
    - a mouth suppression envelope.

    The operation preserves values outside the effective face region.
    """

    @staticmethod
    def enhance(
        anchor_height: np.ndarray,
        subject_mask: np.ndarray,
        *,
        face_bounds: Sequence[int] | None = None,
        face_strength: float = 0.20,
        mouth_suppression_strength: float = 0.35,
        blur_radius: int = 5,
    ) -> np.ndarray:
        anchor = np.asarray(
            anchor_height,
            dtype=np.float64,
        )
        mask = np.asarray(
            subject_mask,
            dtype=np.float64,
        )

        AtlasReliefFaceAnchorEnhancer._validate_inputs(
            anchor,
            mask,
        )

        face_strength_value = (
            AtlasReliefFaceAnchorEnhancer._validate_unit_strength(
                face_strength,
                name="face_strength",
            )
        )

        mouth_suppression_value = (
            AtlasReliefFaceAnchorEnhancer._validate_unit_strength(
                mouth_suppression_strength,
                name="mouth_suppression_strength",
            )
        )

        blur_radius_value = int(blur_radius)

        if blur_radius_value < 1:
            raise ValueError(
                "blur_radius must be an integer greater than or equal to 1"
            )

        if face_strength_value == 0.0:
            return anchor.copy()

        rows, columns = anchor.shape

        (
            top,
            bottom,
            left,
            right,
        ) = AtlasReliefFaceAnchorEnhancer._resolve_face_bounds(
            mask,
            rows=rows,
            columns=columns,
            face_bounds=face_bounds,
        )

        local_blur = (
            AtlasReliefFaceAnchorEnhancer._box_blur(
                anchor,
                radius=blur_radius_value,
            )
        )

        local_detail = (
            anchor
            - local_blur
        )

        face_envelope = (
            AtlasReliefFaceAnchorEnhancer._build_face_envelope(
                rows=rows,
                columns=columns,
                top=top,
                bottom=bottom,
                left=left,
                right=right,
            )
        )

        mouth_envelope = (
            AtlasReliefFaceAnchorEnhancer._build_mouth_envelope(
                rows=rows,
                columns=columns,
                top=top,
                bottom=bottom,
                left=left,
                right=right,
            )
        )

        subject = np.clip(
            mask,
            0.0,
            1.0,
        )

        effective_weight = (
            face_envelope
            * subject
            * (
                1.0
                - mouth_suppression_value
                * mouth_envelope
            )
        )

        result = (
            anchor
            + face_strength_value
            * local_detail
            * effective_weight
        )

        return np.asarray(
            np.clip(
                result,
                0.0,
                1.0,
            ),
            dtype=np.float64,
        )

    @staticmethod
    def _validate_inputs(
        anchor: np.ndarray,
        mask: np.ndarray,
    ) -> None:
        if anchor.ndim != 2:
            raise ValueError(
                "anchor_height must be a two-dimensional array"
            )

        if mask.shape != anchor.shape:
            raise ValueError(
                "subject_mask shape must match anchor_height"
            )

        if not np.all(
            np.isfinite(anchor)
        ):
            raise ValueError(
                "anchor_height must contain only finite values"
            )

        if not np.all(
            np.isfinite(mask)
        ):
            raise ValueError(
                "subject_mask must contain only finite values"
            )

        if not np.any(
            mask > 0.0
        ):
            raise ValueError(
                "subject_mask must contain at least one active pixel"
            )

    @staticmethod
    def _validate_unit_strength(
        value: float,
        *,
        name: str,
    ) -> float:
        numeric_value = float(value)

        if not np.isfinite(
            numeric_value
        ):
            raise ValueError(
                f"{name} must be finite"
            )

        if (
            numeric_value < 0.0
            or numeric_value > 1.0
        ):
            raise ValueError(
                f"{name} must be between 0 and 1"
            )

        return numeric_value

    @staticmethod
    def _resolve_face_bounds(
        mask: np.ndarray,
        *,
        rows: int,
        columns: int,
        face_bounds: Sequence[int] | None,
    ) -> tuple[int, int, int, int]:
        if face_bounds is None:
            active_rows, active_columns = np.nonzero(
                mask > 0.0
            )

            return (
                int(active_rows.min()),
                int(active_rows.max()),
                int(active_columns.min()),
                int(active_columns.max()),
            )

        if (
            not isinstance(
                face_bounds,
                Sequence,
            )
            or isinstance(
                face_bounds,
                (str, bytes),
            )
            or len(face_bounds) != 4
        ):
            raise ValueError(
                "face_bounds must contain "
                "(top, bottom, left, right)"
            )

        try:
            top, bottom, left, right = (
                int(value)
                for value in face_bounds
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "face_bounds must contain integer coordinates"
            ) from error

        if (
            top < 0
            or bottom < 0
            or left < 0
            or right < 0
            or top >= rows
            or bottom >= rows
            or left >= columns
            or right >= columns
            or bottom <= top
            or right <= left
        ):
            raise ValueError(
                "face_bounds must define a valid region "
                "inside the anchor image"
            )

        return (
            top,
            bottom,
            left,
            right,
        )

    @staticmethod
    def _build_face_envelope(
        *,
        rows: int,
        columns: int,
        top: int,
        bottom: int,
        left: int,
        right: int,
    ) -> np.ndarray:
        row_grid, column_grid = np.mgrid[
            0:rows,
            0:columns,
        ]

        center_x = 0.5 * (
            left + right
        )
        center_y = top + 0.46 * (
            bottom - top
        )

        radius_x = max(
            0.52 * (
                right - left
            ),
            1.0,
        )
        radius_y = max(
            0.58 * (
                bottom - top
            ),
            1.0,
        )

        distance = (
            (
                (
                    column_grid - center_x
                ) / radius_x
            ) ** 2
            + (
                (
                    row_grid - center_y
                ) / radius_y
            ) ** 2
        )

        envelope = np.exp(
            -1.25 * distance
        )

        bounds_mask = np.zeros(
            (rows, columns),
            dtype=np.float64,
        )
        bounds_mask[
            top:bottom + 1,
            left:right + 1,
        ] = 1.0

        return (
            envelope
            * bounds_mask
        )

    @staticmethod
    def _build_mouth_envelope(
        *,
        rows: int,
        columns: int,
        top: int,
        bottom: int,
        left: int,
        right: int,
    ) -> np.ndarray:
        row_grid, column_grid = np.mgrid[
            0:rows,
            0:columns,
        ]

        center_x = 0.5 * (
            left + right
        )
        center_y = top + 0.70 * (
            bottom - top
        )

        sigma_x = max(
            0.20 * (
                right - left
            ),
            1.0,
        )
        sigma_y = max(
            0.075 * (
                bottom - top
            ),
            1.0,
        )

        exponent = (
            (
                (
                    column_grid - center_x
                ) / sigma_x
            ) ** 2
            + (
                (
                    row_grid - center_y
                ) / sigma_y
            ) ** 2
        )

        return np.exp(
            -0.5 * exponent
        )

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
