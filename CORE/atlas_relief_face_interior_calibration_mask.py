from __future__ import annotations

from collections.abc import Sequence

import numpy as np


class AtlasReliefFaceInteriorCalibrationMask:
    """Build a soft mask for robust face-interior gradient calibration.

    The mask favors stable interior facial regions while suppressing:

    - lateral face and ear boundaries,
    - the eye and glasses band,
    - the mouth band,
    - the lower neck transition.

    ``face_bounds`` uses inclusive coordinates:

        (top, bottom, left, right)
    """

    @staticmethod
    def build(
        subject_mask: np.ndarray,
        *,
        face_bounds: Sequence[int],
        eye_suppression_strength: float = 0.80,
        mouth_suppression_strength: float = 0.85,
    ) -> np.ndarray:
        mask = np.asarray(
            subject_mask,
            dtype=np.float64,
        )

        AtlasReliefFaceInteriorCalibrationMask._validate_subject_mask(
            mask
        )

        rows, columns = mask.shape

        (
            top,
            bottom,
            left,
            right,
        ) = AtlasReliefFaceInteriorCalibrationMask._validate_face_bounds(
            face_bounds,
            rows=rows,
            columns=columns,
        )

        eye_strength = (
            AtlasReliefFaceInteriorCalibrationMask
            ._validate_unit_strength(
                eye_suppression_strength,
                name="eye_suppression_strength",
            )
        )

        mouth_strength = (
            AtlasReliefFaceInteriorCalibrationMask
            ._validate_unit_strength(
                mouth_suppression_strength,
                name="mouth_suppression_strength",
            )
        )

        row_grid, column_grid = np.mgrid[
            0:rows,
            0:columns,
        ]

        face_height = float(
            bottom - top
        )
        face_width = float(
            right - left
        )

        center_x = 0.5 * (
            left + right
        )
        center_y = top + 0.47 * face_height

        radius_x = max(
            0.46 * face_width,
            1.0,
        )
        radius_y = max(
            0.58 * face_height,
            1.0,
        )

        normalized_x = (
            column_grid - center_x
        ) / radius_x

        normalized_y = (
            row_grid - center_y
        ) / radius_y

        radial_distance = (
            normalized_x * normalized_x
            + normalized_y * normalized_y
        )

        interior_envelope = np.exp(
            -1.15 * radial_distance
        )

        bounds_mask = np.zeros(
            (rows, columns),
            dtype=np.float64,
        )
        bounds_mask[
            top:bottom + 1,
            left:right + 1,
        ] = 1.0

        eye_envelope = (
            AtlasReliefFaceInteriorCalibrationMask
            ._gaussian_band(
                row_grid=row_grid,
                column_grid=column_grid,
                center_y=top + 0.38 * face_height,
                center_x=center_x,
                sigma_y=max(
                    0.075 * face_height,
                    1.0,
                ),
                sigma_x=max(
                    0.36 * face_width,
                    1.0,
                ),
            )
        )

        mouth_envelope = (
            AtlasReliefFaceInteriorCalibrationMask
            ._gaussian_band(
                row_grid=row_grid,
                column_grid=column_grid,
                center_y=top + 0.71 * face_height,
                center_x=center_x,
                sigma_y=max(
                    0.070 * face_height,
                    1.0,
                ),
                sigma_x=max(
                    0.24 * face_width,
                    1.0,
                ),
            )
        )

        lower_taper_start = (
            top + 0.78 * face_height
        )

        lower_taper = np.ones(
            (rows, columns),
            dtype=np.float64,
        )

        lower_region = (
            row_grid > lower_taper_start
        )

        lower_taper[
            lower_region
        ] = np.clip(
            (
                bottom
                - row_grid[lower_region]
            )
            / max(
                bottom - lower_taper_start,
                1.0,
            ),
            0.0,
            1.0,
        )

        subject_weight = np.clip(
            mask,
            0.0,
            1.0,
        )

        result = (
            interior_envelope
            * bounds_mask
            * subject_weight
            * (
                1.0
                - eye_strength
                * eye_envelope
            )
            * (
                1.0
                - mouth_strength
                * mouth_envelope
            )
            * lower_taper
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
    def _validate_subject_mask(
        subject_mask: np.ndarray,
    ) -> None:
        if subject_mask.ndim != 2:
            raise ValueError(
                "subject_mask must be a two-dimensional array"
            )

        if not np.all(
            np.isfinite(subject_mask)
        ):
            raise ValueError(
                "subject_mask must contain only finite values"
            )

    @staticmethod
    def _validate_face_bounds(
        face_bounds: Sequence[int],
        *,
        rows: int,
        columns: int,
    ) -> tuple[int, int, int, int]:
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
                "inside the subject_mask"
            )

        return (
            top,
            bottom,
            left,
            right,
        )

    @staticmethod
    def _validate_unit_strength(
        value: float,
        *,
        name: str,
    ) -> float:
        numeric_value = float(
            value
        )

        if (
            not np.isfinite(numeric_value)
            or numeric_value < 0.0
            or numeric_value > 1.0
        ):
            raise ValueError(
                f"{name} must be finite and between 0 and 1"
            )

        return numeric_value

    @staticmethod
    def _gaussian_band(
        *,
        row_grid: np.ndarray,
        column_grid: np.ndarray,
        center_y: float,
        center_x: float,
        sigma_y: float,
        sigma_x: float,
    ) -> np.ndarray:
        exponent = (
            (
                (
                    row_grid - center_y
                ) / sigma_y
            ) ** 2
            + (
                (
                    column_grid - center_x
                ) / sigma_x
            ) ** 2
        )

        return np.exp(
            -0.5 * exponent
        )
