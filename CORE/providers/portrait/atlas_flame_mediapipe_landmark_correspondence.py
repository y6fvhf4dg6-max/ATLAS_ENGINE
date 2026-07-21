from __future__ import annotations

from collections.abc import Iterable
from numbers import Integral
from typing import Any


class AtlasFlameMediaPipeLandmarkCorrespondence:
    """
    Deterministic ground-truth to MediaPipe landmark map
    for the FLAME 2023 Open fitting spike.

    The mapping contains only correspondences confirmed
    against the downloaded FLAME MediaPipe embedding and
    neutral-template geometry.

    It performs no model loading, barycentric evaluation,
    fitting, camera estimation, mesh deformation,
    projection, rendering, or STL generation.
    """

    VERSION = "flame-mediapipe-ground-truth-v1"

    _MAPPING = {
        "left_eye_outer": 263,
        "left_eye_inner": 362,
        "right_eye_inner": 133,
        "right_eye_outer": 33,
        "left_eyebrow_outer": 300,
        "left_eyebrow_inner": 336,
        "right_eyebrow_inner": 107,
        "right_eyebrow_outer": 70,
        "nose_root": 168,
        "nose_bridge": 197,
        "nose_tip": 4,
        "nose_left": 327,
        "nose_right": 98,
        "mouth_left": 291,
        "upper_lip_center": 0,
        "lower_lip_center": 17,
        "mouth_right": 61,
    }

    _UNSUPPORTED_GROUND_TRUTH_LANDMARKS = (
        "chin_tip",
        "hairline_center",
        "left_face_edge",
        "left_jaw",
        "right_face_edge",
        "right_jaw",
    )

    @classmethod
    def mapping(
        cls,
    ) -> dict[str, int]:
        return {
            name: cls._MAPPING[name]
            for name in sorted(
                cls._MAPPING,
            )
        }

    @classmethod
    def landmark_count(
        cls,
    ) -> int:
        return len(
            cls._MAPPING,
        )

    @classmethod
    def landmark_names(
        cls,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                cls._MAPPING,
            )
        )

    @classmethod
    def mediapipe_ids(
        cls,
    ) -> tuple[int, ...]:
        return tuple(
            cls._MAPPING[name]
            for name in cls.landmark_names()
        )

    @classmethod
    def resolve(
        cls,
        landmark_name: Any,
    ) -> int:
        normalized_name = cls._normalize_landmark_name(
            landmark_name,
        )

        try:
            return cls._MAPPING[
                normalized_name
            ]
        except KeyError as exc:
            raise KeyError(
                normalized_name,
            ) from exc

    @classmethod
    def is_supported(
        cls,
        landmark_name: Any,
    ) -> bool:
        try:
            normalized_name = (
                cls._normalize_landmark_name(
                    landmark_name,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            return False

        return normalized_name in cls._MAPPING

    @classmethod
    def validate_embedding_indices(
        cls,
        embedding_indices: Any,
    ) -> tuple[int, ...]:
        if (
            embedding_indices is None
            or isinstance(
                embedding_indices,
                (
                    str,
                    bytes,
                ),
            )
        ):
            raise TypeError(
                "embedding_indices must be an iterable "
                "of integer indices."
            )

        try:
            raw_indices = tuple(
                embedding_indices,
            )
        except TypeError as exc:
            raise TypeError(
                "embedding_indices must be an iterable "
                "of integer indices."
            ) from exc

        normalized_indices: set[int] = set()

        for raw_index in raw_indices:
            if (
                isinstance(
                    raw_index,
                    bool,
                )
                or not isinstance(
                    raw_index,
                    Integral,
                )
            ):
                raise TypeError(
                    "embedding_indices must contain "
                    "only integer indices."
                )

            normalized_indices.add(
                int(
                    raw_index,
                )
            )

        missing_ids = tuple(
            sorted(
                set(
                    cls.mediapipe_ids(),
                )
                - normalized_indices
            )
        )

        if missing_ids:
            raise ValueError(
                "Embedding is missing required MediaPipe "
                "landmark IDs: "
                + ", ".join(
                    str(
                        media_pipe_id,
                    )
                    for media_pipe_id in missing_ids
                )
                + "."
            )

        return cls.mediapipe_ids()

    @classmethod
    def metadata(
        cls,
    ) -> dict[str, Any]:
        return {
            "correspondence_version": cls.VERSION,
            "landmark_count": cls.landmark_count(),
            "model_family": "flame",
            "source_embedding": (
                "mediapipe_landmark_embedding"
            ),
            "unsupported_ground_truth_landmarks": list(
                cls._UNSUPPORTED_GROUND_TRUTH_LANDMARKS
            ),
        }

    @staticmethod
    def _normalize_landmark_name(
        value: Any,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "landmark_name must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "landmark_name must not be blank."
            )

        return normalized
