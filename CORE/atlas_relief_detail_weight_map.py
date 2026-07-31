from __future__ import annotations

from collections.abc import Sequence

import numpy as np


class AtlasReliefDetailWeightMap:
    """Build a soft portrait detail-weight map.

    The map contains three controlled regions:

    - broad facial contribution,
    - narrow upper-mouth suppression,
    - separate lip restoration.

    When ``face_bounds`` is supplied, all facial regions are positioned within
    those bounds rather than within the complete subject silhouette.

    ``face_bounds`` uses inclusive image coordinates in this order:

        (top, bottom, left, right)
    """

    @staticmethod
    def build_portrait_weight_map(
        subject_mask: np.ndarray,
        *,
        face_bounds: Sequence[int] | None = None,
        mouth_suppression_strength: float = 0.75,
        lip_restore_strength: float = 0.30,
    ) -> np.ndarray:
        mask = np.asarray(subject_mask, dtype=np.float64)

        if mask.ndim != 2:
            raise ValueError(
                "subject_mask must be a two-dimensional array"
            )

        if not np.all(np.isfinite(mask)):
            raise ValueError(
                "subject_mask must contain only finite values"
            )

        active = mask > 0.0

        if not np.any(active):
            raise ValueError(
                "subject_mask must contain at least one active pixel"
            )

        AtlasReliefDetailWeightMap._validate_unit_strength(
            mouth_suppression_strength,
            name="mouth_suppression_strength",
        )
        AtlasReliefDetailWeightMap._validate_unit_strength(
            lip_restore_strength,
            name="lip_restore_strength",
        )

        rows, columns = mask.shape

        (
            top,
            bottom,
            left,
            right,
            uses_explicit_face_bounds,
        ) = AtlasReliefDetailWeightMap._resolve_face_bounds(
            active,
            rows=rows,
            columns=columns,
            face_bounds=face_bounds,
        )

        face_height = max(bottom - top, 1)
        face_width = max(right - left, 1)

        center_x = 0.5 * (left + right)

        row_grid, column_grid = np.mgrid[
            0:rows,
            0:columns,
        ]

        normalized_x = (
            column_grid - center_x
        ) / max(0.5 * face_width, 1.0)

        normalized_y = (
            row_grid - top
        ) / face_height

        if uses_explicit_face_bounds:
            face_center_y = 0.43
            face_radius_y = 0.47
            upper_mouth_center_y = 0.62
            lip_center_y = 0.72
            upper_mouth_sigma_y = 0.040
            lip_sigma_y = 0.038
        else:
            # Preserve the original automatic-mask behavior used by the
            # existing synthetic contract tests.
            face_center_y = 0.34
            face_radius_y = 0.40
            upper_mouth_center_y = 0.535
            lip_center_y = 0.625
            upper_mouth_sigma_y = 0.050
            lip_sigma_y = 0.040

        face_radius_x = 0.82

        face_distance = (
            (normalized_x / face_radius_x) ** 2
            + (
                (normalized_y - face_center_y)
                / face_radius_y
            ) ** 2
        )

        face_weight = np.exp(
            -1.35 * face_distance
        )

        upper_mouth_band = (
            AtlasReliefDetailWeightMap._gaussian_region(
                normalized_x,
                normalized_y,
                center_x=0.0,
                center_y=upper_mouth_center_y,
                sigma_x=0.27,
                sigma_y=upper_mouth_sigma_y,
            )
        )

        lip_restore_band = (
            AtlasReliefDetailWeightMap._gaussian_region(
                normalized_x,
                normalized_y,
                center_x=0.0,
                center_y=lip_center_y,
                sigma_x=0.25,
                sigma_y=lip_sigma_y,
            )
        )

        weight = face_weight.copy()

        weight *= (
            1.0
            - mouth_suppression_strength
            * upper_mouth_band
        )

        weight += (
            lip_restore_strength
            * lip_restore_band
        )

        normalized_subject_mask = np.clip(
            mask,
            0.0,
            1.0,
        )

        weight *= normalized_subject_mask

        return np.asarray(
            np.clip(weight, 0.0, 1.0),
            dtype=np.float64,
        )

    @staticmethod
    def _resolve_face_bounds(
        active_mask: np.ndarray,
        *,
        rows: int,
        columns: int,
        face_bounds: Sequence[int] | None,
    ) -> tuple[int, int, int, int, bool]:
        if face_bounds is None:
            active_rows, active_columns = np.nonzero(
                active_mask
            )

            return (
                int(active_rows.min()),
                int(active_rows.max()),
                int(active_columns.min()),
                int(active_columns.max()),
                False,
            )

        if (
            not isinstance(face_bounds, Sequence)
            or isinstance(face_bounds, (str, bytes))
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
        except (TypeError, ValueError) as error:
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
                "inside the subject-mask image"
            )

        return (
            top,
            bottom,
            left,
            right,
            True,
        )

    @staticmethod
    def _gaussian_region(
        normalized_x: np.ndarray,
        normalized_y: np.ndarray,
        *,
        center_x: float,
        center_y: float,
        sigma_x: float,
        sigma_y: float,
    ) -> np.ndarray:
        exponent = (
            (
                (normalized_x - center_x)
                / sigma_x
            ) ** 2
            + (
                (normalized_y - center_y)
                / sigma_y
            ) ** 2
        )

        return np.exp(
            -0.5 * exponent
        )

    @staticmethod
    def _validate_unit_strength(
        value: float,
        *,
        name: str,
    ) -> None:
        numeric_value = float(value)

        if not np.isfinite(numeric_value):
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
