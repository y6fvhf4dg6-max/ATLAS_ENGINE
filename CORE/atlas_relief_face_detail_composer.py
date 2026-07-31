from __future__ import annotations

from collections.abc import Sequence

import numpy as np


class AtlasReliefFaceDetailComposer:
    """Compose bounded facial detail over a stable base height map.

    The detail map is centered over the active weighted region, normalized to
    a symmetric unit range, limited by ``max_detail_amplitude``, and then
    blended additively into the base height map.

    ``face_bounds`` uses inclusive image coordinates:

        (top, bottom, left, right)
    """

    @staticmethod
    def compose(
        base_height: np.ndarray,
        detail_height: np.ndarray,
        detail_weight: np.ndarray,
        *,
        face_bounds: Sequence[int] | None = None,
        max_detail_amplitude: float = 0.08,
        clamp_output: bool = True,
    ) -> np.ndarray:
        base = np.asarray(
            base_height,
            dtype=np.float64,
        )
        detail = np.asarray(
            detail_height,
            dtype=np.float64,
        )
        weight = np.asarray(
            detail_weight,
            dtype=np.float64,
        )

        AtlasReliefFaceDetailComposer._validate_inputs(
            base,
            detail,
            weight,
        )

        amplitude = float(
            max_detail_amplitude
        )

        if (
            not np.isfinite(amplitude)
            or amplitude < 0.0
        ):
            raise ValueError(
                "max_detail_amplitude must be finite "
                "and greater than or equal to zero"
            )

        rows, columns = base.shape

        bounds_mask = (
            AtlasReliefFaceDetailComposer._build_bounds_mask(
                rows=rows,
                columns=columns,
                face_bounds=face_bounds,
            )
        )

        effective_weight = (
            np.clip(
                weight,
                0.0,
                1.0,
            )
            * bounds_mask
        )

        active = effective_weight > 0.0

        if not np.any(active) or amplitude == 0.0:
            return base.copy()

        active_detail = detail[active]
        active_weights = effective_weight[active]

        weight_sum = float(
            np.sum(active_weights)
        )

        if weight_sum <= 1e-15:
            return base.copy()

        weighted_center = float(
            np.sum(
                active_detail
                * active_weights
            )
            / weight_sum
        )

        centered_detail = (
            detail
            - weighted_center
        )

        active_centered = centered_detail[active]

        scale = float(
            np.max(
                np.abs(active_centered)
            )
        )

        if scale <= 1e-15:
            normalized_detail = np.zeros_like(
                centered_detail,
                dtype=np.float64,
            )
        else:
            normalized_detail = np.clip(
                centered_detail / scale,
                -1.0,
                1.0,
            )

        contribution = (
            normalized_detail
            * effective_weight
            * amplitude
        )

        result = (
            base
            + contribution
        )

        if clamp_output:
            result = np.clip(
                result,
                0.0,
                1.0,
            )

        return np.asarray(
            result,
            dtype=np.float64,
        )

    @staticmethod
    def _validate_inputs(
        base_height: np.ndarray,
        detail_height: np.ndarray,
        detail_weight: np.ndarray,
    ) -> None:
        if base_height.ndim != 2:
            raise ValueError(
                "base_height must be a two-dimensional array"
            )

        if detail_height.shape != base_height.shape:
            raise ValueError(
                "detail_height shape must match base_height"
            )

        if detail_weight.shape != base_height.shape:
            raise ValueError(
                "detail_weight shape must match base_height"
            )

        if not np.all(
            np.isfinite(base_height)
        ):
            raise ValueError(
                "base_height must contain only finite values"
            )

        if not np.all(
            np.isfinite(detail_height)
        ):
            raise ValueError(
                "detail_height must contain only finite values"
            )

        if not np.all(
            np.isfinite(detail_weight)
        ):
            raise ValueError(
                "detail_weight must contain only finite values"
            )

    @staticmethod
    def _build_bounds_mask(
        *,
        rows: int,
        columns: int,
        face_bounds: Sequence[int] | None,
    ) -> np.ndarray:
        mask = np.ones(
            (rows, columns),
            dtype=np.float64,
        )

        if face_bounds is None:
            return mask

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
                "inside the height-map image"
            )

        mask.fill(0.0)
        mask[
            top:bottom + 1,
            left:right + 1,
        ] = 1.0

        return mask
