from __future__ import annotations

from numbers import Integral
from typing import Any

import numpy as np

from CORE.atlas_portrait_indexed_landmark_result import (
    AtlasPortraitIndexedLandmarkResult,
)
from CORE.atlas_portrait_weak_perspective_fitting_input import (
    AtlasPortraitWeakPerspectiveFittingInput,
)


class AtlasPortraitDenseWeakPerspectiveFittingInputBuilder:
    """
    Builds dense weak-perspective fitting input from an
    indexed portrait-landmark result.

    Requested MediaPipe IDs determine both the target-point
    order and deterministic landmark names. Canonical FLAME
    source points must already follow the same requested-ID
    order.

    The builder performs no provider loading, embedding
    evaluation, camera estimation, optimization, FLAME
    deformation, rendering, relief compression, or STL
    generation.
    """

    @classmethod
    def build(
        cls,
        *,
        landmark_result: AtlasPortraitIndexedLandmarkResult,
        source_points_3d: Any,
        requested_mediapipe_ids: Any,
        landmark_weights: Any | None = None,
    ) -> AtlasPortraitWeakPerspectiveFittingInput:
        if not isinstance(
            landmark_result,
            AtlasPortraitIndexedLandmarkResult,
        ):
            raise TypeError(
                "landmark_result must be an "
                "AtlasPortraitIndexedLandmarkResult."
            )

        requested_ids = cls._normalize_requested_ids(
            requested_mediapipe_ids
        )

        missing_ids = tuple(
            landmark_id
            for landmark_id in requested_ids
            if landmark_id not in landmark_result.index_by_id
        )

        if missing_ids:
            raise ValueError(
                "landmark_result is missing requested "
                "MediaPipe IDs: "
                + ", ".join(
                    str(
                        landmark_id
                    )
                    for landmark_id in missing_ids
                )
                + "."
            )

        landmark_names = tuple(
            f"mediapipe_{landmark_id}"
            for landmark_id in requested_ids
        )

        target_points_2d = np.asarray(
            [
                landmark_result.landmark_2d(
                    landmark_id
                )
                for landmark_id in requested_ids
            ],
            dtype=np.float64,
        )

        landmark_count = len(
            requested_ids
        )

        if landmark_weights is None:
            normalized_weights = np.ones(
                landmark_count,
                dtype=np.float64,
            )
        else:
            normalized_weights = landmark_weights

        metadata = cls._build_metadata(
            landmark_result,
            landmark_count=landmark_count,
        )

        return AtlasPortraitWeakPerspectiveFittingInput(
            landmark_names=landmark_names,
            source_points_3d=source_points_3d,
            target_points_2d=target_points_2d,
            landmark_weights=normalized_weights,
            image_width=landmark_result.image_width,
            image_height=landmark_result.image_height,
            metadata=metadata,
        )

    @staticmethod
    def _normalize_requested_ids(
        value: Any,
    ) -> tuple[int, ...]:
        if (
            value is None
            or isinstance(
                value,
                (
                    str,
                    bytes,
                ),
            )
        ):
            raise TypeError(
                "requested_mediapipe_ids must be a "
                "non-empty iterable of integers."
            )

        try:
            raw_ids = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "requested_mediapipe_ids must be a "
                "non-empty iterable of integers."
            ) from exc

        if not raw_ids:
            raise ValueError(
                "requested_mediapipe_ids must not be empty."
            )

        normalized_ids: list[int] = []

        for raw_id in raw_ids:
            if (
                isinstance(
                    raw_id,
                    bool,
                )
                or not isinstance(
                    raw_id,
                    Integral,
                )
            ):
                raise TypeError(
                    "requested_mediapipe_ids must contain "
                    "integer values."
                )

            landmark_id = int(
                raw_id
            )

            if landmark_id < 0:
                raise ValueError(
                    "requested_mediapipe_ids must not "
                    "contain negative values."
                )

            normalized_ids.append(
                landmark_id
            )

        if len(
            normalized_ids
        ) != len(
            set(
                normalized_ids
            )
        ):
            raise ValueError(
                "requested_mediapipe_ids must contain "
                "unique values."
            )

        return tuple(
            normalized_ids
        )

    @staticmethod
    def _build_metadata(
        landmark_result: AtlasPortraitIndexedLandmarkResult,
        *,
        landmark_count: int,
    ) -> dict[str, Any]:
        source_metadata = landmark_result.metadata

        return {
            "correspondence_type": "indexed-mediapipe",
            "input_view": source_metadata.get(
                "view_type"
            ),
            "landmark_count": landmark_count,
            "landmark_provider_id": (
                landmark_result.provider_id
            ),
            "model_family": "flame",
            "source_image_sha256": source_metadata.get(
                "image_sha256"
            ),
            "synthetic": source_metadata.get(
                "synthetic"
            ),
        }
