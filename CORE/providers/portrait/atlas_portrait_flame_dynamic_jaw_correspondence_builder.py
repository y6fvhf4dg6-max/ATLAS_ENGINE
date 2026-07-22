from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameDynamicJawCorrespondence:
    """
    Immutable ordered correspondence between a FLAME dynamic
    contour and a MediaPipe jaw polyline.
    """

    flame_contour_points_2d: np.ndarray
    target_jaw_points_2d: np.ndarray
    residual_vectors_2d: np.ndarray
    distances: np.ndarray
    target_orientation: str

    def __post_init__(
        self,
    ) -> None:
        flame_points = self._normalize_points(
            self.flame_contour_points_2d,
            name="flame_contour_points_2d",
        )
        target_points = self._normalize_points(
            self.target_jaw_points_2d,
            name="target_jaw_points_2d",
        )

        if flame_points.shape != target_points.shape:
            raise ValueError(
                "flame_contour_points_2d and "
                "target_jaw_points_2d must have matching shapes."
            )

        residual_vectors = np.asarray(
            self.residual_vectors_2d,
            dtype=np.float64,
        ).copy()

        if residual_vectors.shape != flame_points.shape:
            raise ValueError(
                "residual_vectors_2d must match the landmark "
                "point shape."
            )

        if not np.isfinite(
            residual_vectors
        ).all():
            raise ValueError(
                "residual_vectors_2d contains non-finite values."
            )

        distances = np.asarray(
            self.distances,
            dtype=np.float64,
        ).copy()

        if distances.shape != (
            flame_points.shape[0],
        ):
            raise ValueError(
                "distances must have shape (L,)."
            )

        if not np.isfinite(
            distances
        ).all():
            raise ValueError(
                "distances contains non-finite values."
            )

        if np.any(
            distances < 0.0
        ):
            raise ValueError(
                "distances must not contain negative values."
            )

        orientation = str(
            self.target_orientation
        )

        if orientation not in {
            "forward",
            "reversed",
        }:
            raise ValueError(
                "target_orientation must be 'forward' "
                "or 'reversed'."
            )

        expected_residuals = (
            flame_points
            - target_points
        )

        if not np.allclose(
            residual_vectors,
            expected_residuals,
            rtol=0.0,
            atol=1.0e-12,
        ):
            raise ValueError(
                "residual_vectors_2d must equal "
                "flame_contour_points_2d - target_jaw_points_2d."
            )

        expected_distances = np.linalg.norm(
            residual_vectors,
            axis=1,
        )

        if not np.allclose(
            distances,
            expected_distances,
            rtol=0.0,
            atol=1.0e-12,
        ):
            raise ValueError(
                "distances must equal the residual vector norms."
            )

        flame_points.setflags(
            write=False
        )
        target_points.setflags(
            write=False
        )
        residual_vectors.setflags(
            write=False
        )
        distances.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "flame_contour_points_2d",
            flame_points,
        )
        object.__setattr__(
            self,
            "target_jaw_points_2d",
            target_points,
        )
        object.__setattr__(
            self,
            "residual_vectors_2d",
            residual_vectors,
        )
        object.__setattr__(
            self,
            "distances",
            distances,
        )
        object.__setattr__(
            self,
            "target_orientation",
            orientation,
        )

    @property
    def landmark_count(
        self,
    ) -> int:
        return int(
            self.flame_contour_points_2d.shape[0]
        )

    @property
    def mean_distance(
        self,
    ) -> float:
        return float(
            np.mean(
                self.distances
            )
        )

    @property
    def maximum_distance(
        self,
    ) -> float:
        return float(
            np.max(
                self.distances
            )
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "landmark_count": self.landmark_count,
            "target_orientation": self.target_orientation,
            "mean_distance": self.mean_distance,
            "maximum_distance": self.maximum_distance,
            "flame_contour_points_2d": (
                self.flame_contour_points_2d.tolist()
            ),
            "target_jaw_points_2d": (
                self.target_jaw_points_2d.tolist()
            ),
            "residual_vectors_2d": (
                self.residual_vectors_2d.tolist()
            ),
            "distances": self.distances.tolist(),
        }

    @staticmethod
    def _normalize_points(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            points = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if (
            points.ndim != 2
            or points.shape[0] < 2
            or points.shape[1] != 2
        ):
            raise ValueError(
                f"{name} must have shape "
                "(N, 2) with N >= 2."
            )

        if not np.isfinite(
            points
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return points.astype(
            np.float64,
            copy=True,
        )


class AtlasPortraitFlameDynamicJawCorrespondenceBuilder:
    """
    Builds ordered 2D jaw correspondence.

    The MediaPipe jaw polyline is resampled by cumulative arc
    length to the FLAME dynamic contour landmark count. Both
    target orientations are evaluated, and the lower-error
    orientation is selected deterministically.

    This builder performs no fitting, weighting, robust loss,
    mesh deformation, camera projection, rendering, or STL export.
    """

    _LENGTH_TOLERANCE = 1.0e-12
    _ORIENTATION_TIE_TOLERANCE = 1.0e-12

    @classmethod
    def build(
        cls,
        *,
        flame_contour_points_2d: Any,
        mediapipe_jaw_points_2d: Any,
    ) -> AtlasPortraitFlameDynamicJawCorrespondence:
        flame_points = cls._normalize_points(
            flame_contour_points_2d,
            name="flame_contour_points_2d",
        )
        mediapipe_points = cls._normalize_points(
            mediapipe_jaw_points_2d,
            name="mediapipe_jaw_points_2d",
        )

        forward_target = cls._resample_polyline(
            mediapipe_points,
            target_count=flame_points.shape[0],
        )

        reversed_target = cls._resample_polyline(
            mediapipe_points[
                ::-1
            ],
            target_count=flame_points.shape[0],
        )

        forward_error = cls._mean_distance(
            flame_points,
            forward_target,
        )
        reversed_error = cls._mean_distance(
            flame_points,
            reversed_target,
        )

        if (
            reversed_error
            < forward_error
            - cls._ORIENTATION_TIE_TOLERANCE
        ):
            target_points = reversed_target
            orientation = "reversed"
        else:
            target_points = forward_target
            orientation = "forward"

        residual_vectors = (
            flame_points
            - target_points
        )

        distances = np.linalg.norm(
            residual_vectors,
            axis=1,
        )

        return AtlasPortraitFlameDynamicJawCorrespondence(
            flame_contour_points_2d=flame_points,
            target_jaw_points_2d=target_points,
            residual_vectors_2d=residual_vectors,
            distances=distances,
            target_orientation=orientation,
        )

    @staticmethod
    def _normalize_points(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            points = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if (
            points.ndim != 2
            or points.shape[0] < 2
            or points.shape[1] != 2
        ):
            raise ValueError(
                f"{name} must have shape "
                "(N, 2) with N >= 2."
            )

        if not np.isfinite(
            points
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return points.astype(
            np.float64,
            copy=True,
        )

    @classmethod
    def _resample_polyline(
        cls,
        points: np.ndarray,
        *,
        target_count: int,
    ) -> np.ndarray:
        segment_vectors = (
            points[
                1:
            ]
            - points[
                :-1
            ]
        )

        segment_lengths = np.linalg.norm(
            segment_vectors,
            axis=1,
        )

        cumulative_lengths = np.concatenate(
            (
                np.array(
                    [
                        0.0,
                    ],
                    dtype=np.float64,
                ),
                np.cumsum(
                    segment_lengths,
                    dtype=np.float64,
                ),
            )
        )

        total_length = float(
            cumulative_lengths[
                -1
            ]
        )

        if (
            not math.isfinite(
                total_length
            )
            or total_length
            <= cls._LENGTH_TOLERANCE
        ):
            raise ValueError(
                "mediapipe_jaw_points_2d polyline length "
                "must be greater than zero."
            )

        sample_lengths = np.linspace(
            0.0,
            total_length,
            target_count,
            dtype=np.float64,
        )

        result = np.empty(
            (
                target_count,
                2,
            ),
            dtype=np.float64,
        )

        for sample_index, sample_length in enumerate(
            sample_lengths
        ):
            if sample_length <= 0.0:
                result[
                    sample_index
                ] = points[
                    0
                ]
                continue

            if sample_length >= total_length:
                result[
                    sample_index
                ] = points[
                    -1
                ]
                continue

            segment_index = int(
                np.searchsorted(
                    cumulative_lengths,
                    sample_length,
                    side="right",
                )
                - 1
            )

            segment_index = min(
                segment_index,
                segment_lengths.shape[0] - 1,
            )

            while (
                segment_index
                < segment_lengths.shape[0]
                and segment_lengths[
                    segment_index
                ]
                <= cls._LENGTH_TOLERANCE
            ):
                segment_index += 1

            if (
                segment_index
                >= segment_lengths.shape[0]
            ):
                result[
                    sample_index
                ] = points[
                    -1
                ]
                continue

            segment_start_length = float(
                cumulative_lengths[
                    segment_index
                ]
            )
            segment_length = float(
                segment_lengths[
                    segment_index
                ]
            )

            fraction = (
                sample_length
                - segment_start_length
            ) / segment_length

            result[
                sample_index
            ] = (
                points[
                    segment_index
                ]
                + fraction
                * segment_vectors[
                    segment_index
                ]
            )

        return result

    @staticmethod
    def _mean_distance(
        first: np.ndarray,
        second: np.ndarray,
    ) -> float:
        return float(
            np.mean(
                np.linalg.norm(
                    first
                    - second,
                    axis=1,
                )
            )
        )
