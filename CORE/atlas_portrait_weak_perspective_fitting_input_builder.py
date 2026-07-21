from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.atlas_portrait_weak_perspective_fitting_input import (
    AtlasPortraitWeakPerspectiveFittingInput,
)
from CORE.providers.portrait.atlas_flame_mediapipe_landmark_correspondence import (
    AtlasFlameMediaPipeLandmarkCorrespondence,
)


class AtlasPortraitWeakPerspectiveFittingInputBuilder:
    """
    Builds deterministic weak-perspective fitting input
    from canonical FLAME landmarks and portrait landmarks.

    Unsupported portrait landmarks are ignored. Supported
    landmark names are selected in the fixed correspondence
    order.

    It performs no FLAME model loading, camera estimation,
    optimization, mesh deformation, projection, rendering,
    relief compression, or STL generation.
    """

    @classmethod
    def build(
        cls,
        *,
        landmark_result: AtlasPortraitLandmarkResult,
        source_points_3d: Any,
        landmark_weights: Any | None = None,
    ) -> AtlasPortraitWeakPerspectiveFittingInput:
        if not isinstance(
            landmark_result,
            AtlasPortraitLandmarkResult,
        ):
            raise TypeError(
                "landmark_result must be an "
                "AtlasPortraitLandmarkResult."
            )

        landmark_names = (
            AtlasFlameMediaPipeLandmarkCorrespondence
            .landmark_names()
        )

        missing_names = tuple(
            name
            for name in landmark_names
            if name not in landmark_result.landmarks
        )

        if missing_names:
            raise ValueError(
                "landmark_result is missing required "
                "landmarks: "
                + ", ".join(
                    missing_names,
                )
                + "."
            )

        target_points_2d = np.asarray(
            [
                landmark_result.landmarks[name]
                for name in landmark_names
            ],
            dtype=np.float64,
        )

        if landmark_weights is None:
            normalized_weights = np.ones(
                len(
                    landmark_names,
                ),
                dtype=np.float64,
            )
        else:
            normalized_weights = landmark_weights

        metadata = cls._build_metadata(
            landmark_result,
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
    def _build_metadata(
        landmark_result: AtlasPortraitLandmarkResult,
    ) -> dict[str, Any]:
        source_metadata = landmark_result.metadata

        return {
            "correspondence_version": (
                AtlasFlameMediaPipeLandmarkCorrespondence
                .VERSION
            ),
            "input_view": source_metadata.get(
                "view_type",
            ),
            "landmark_provider_id": (
                landmark_result.provider_id
            ),
            "model_family": "flame",
            "portrait_fixture": source_metadata.get(
                "fixture_name",
            ),
            "source_image_sha256": source_metadata.get(
                "image_sha256",
            ),
            "synthetic": source_metadata.get(
                "synthetic",
            ),
        }
