from __future__ import annotations

import json
import math
from collections.abc import Mapping
from numbers import Integral
from pathlib import Path
from typing import Any

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.providers.portrait.atlas_flame_mediapipe_landmark_correspondence import (
    AtlasFlameMediaPipeLandmarkCorrespondence,
)


class AtlasMediaPipePortraitLandmarkJsonLoader:
    """
    Loads deterministic MediaPipe Face Landmarker JSON output.

    The loader runs in the main ATLAS_ENGINE Python environment and
    has no dependency on the mediapipe package.

    It validates the complete exported landmark table, maps the
    confirmed MediaPipe IDs to ATLAS landmark names, and returns an
    AtlasPortraitLandmarkResult for weak-perspective fitting.

    MediaPipe Z coordinates are validated in the bridge payload but
    are not included in the current two-dimensional landmark result.
    """

    SCHEMA_VERSION = "atlas-mediapipe-face-landmarks-v1"
    PROVIDER_ID = "mediapipe-face-landmarker-tasks"

    @classmethod
    def load(
        cls,
        path: Any,
    ) -> AtlasPortraitLandmarkResult:
        json_path = cls._normalize_path(
            path,
        )

        try:
            raw_text = json_path.read_text(
                encoding="utf-8",
            )
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise ValueError(
                "Unable to read MediaPipe landmark JSON file."
            ) from exc

        try:
            payload = json.loads(
                raw_text,
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "MediaPipe landmark JSON is invalid."
            ) from exc

        if not isinstance(
            payload,
            Mapping,
        ):
            raise ValueError(
                "JSON root must be a mapping."
            )

        schema_version = cls._require_exact_text(
            payload,
            field_name="schema_version",
            expected=cls.SCHEMA_VERSION,
        )
        provider_id = cls._require_exact_text(
            payload,
            field_name="provider_id",
            expected=cls.PROVIDER_ID,
        )

        image_width = cls._normalize_positive_integer(
            cls._require_field(
                payload,
                "image_width",
            ),
            field_name="image_width",
        )
        image_height = cls._normalize_positive_integer(
            cls._require_field(
                payload,
                "image_height",
            ),
            field_name="image_height",
        )
        confidence = cls._normalize_confidence(
            cls._require_field(
                payload,
                "confidence",
            )
        )

        raw_landmark_count = cls._require_field(
            payload,
            "landmark_count",
        )
        landmark_count = cls._normalize_non_negative_integer(
            raw_landmark_count,
            field_name="landmark_count",
        )

        raw_landmarks = cls._require_field(
            payload,
            "landmarks",
        )
        indexed_landmarks = cls._normalize_landmarks(
            raw_landmarks,
        )

        correspondence = (
            AtlasFlameMediaPipeLandmarkCorrespondence
        )

        correspondence.validate_embedding_indices(
            indexed_landmarks.keys(),
        )

        if landmark_count != len(
            indexed_landmarks,
        ):
            raise ValueError(
                "landmark_count must match the number "
                "of landmark records."
            )

        raw_metadata = cls._require_field(
            payload,
            "metadata",
        )

        if not isinstance(
            raw_metadata,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        named_landmarks = {
            name: (
                indexed_landmarks[
                    media_pipe_id
                ][
                    0
                ],
                indexed_landmarks[
                    media_pipe_id
                ][
                    1
                ],
            )
            for name, media_pipe_id
            in correspondence.mapping().items()
        }

        metadata = cls._build_metadata(
            source_metadata=raw_metadata,
            schema_version=schema_version,
            landmark_count=landmark_count,
        )

        return AtlasPortraitLandmarkResult(
            image_width=image_width,
            image_height=image_height,
            landmarks=named_landmarks,
            confidence=confidence,
            provider_id=provider_id,
            metadata=metadata,
        )

    @staticmethod
    def _normalize_path(
        value: Any,
    ) -> Path:
        if isinstance(
            value,
            Path,
        ):
            return value

        if isinstance(
            value,
            str,
        ):
            return Path(
                value,
            )

        raise TypeError(
            "path must be a string or pathlib.Path."
        )

    @staticmethod
    def _require_field(
        payload: Mapping[str, Any],
        field_name: str,
    ) -> Any:
        try:
            return payload[
                field_name
            ]
        except KeyError as exc:
            raise ValueError(
                f"{field_name} is required."
            ) from exc

    @classmethod
    def _require_exact_text(
        cls,
        payload: Mapping[str, Any],
        *,
        field_name: str,
        expected: str,
    ) -> str:
        value = cls._require_field(
            payload,
            field_name,
        )

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if normalized != expected:
            raise ValueError(
                f"{field_name} must equal {expected!r}."
            )

        return normalized

    @staticmethod
    def _normalize_positive_integer(
        value: Any,
        *,
        field_name: str,
    ) -> int:
        normalized = (
            AtlasMediaPipePortraitLandmarkJsonLoader
            ._normalize_integer(
                value,
                field_name=field_name,
            )
        )

        if normalized <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return normalized

    @staticmethod
    def _normalize_non_negative_integer(
        value: Any,
        *,
        field_name: str,
    ) -> int:
        normalized = (
            AtlasMediaPipePortraitLandmarkJsonLoader
            ._normalize_integer(
                value,
                field_name=field_name,
            )
        )

        if normalized < 0:
            raise ValueError(
                f"{field_name} must not be negative."
            )

        return normalized

    @staticmethod
    def _normalize_integer(
        value: Any,
        *,
        field_name: str,
    ) -> int:
        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                f"{field_name} must be an integer."
            )

        try:
            numeric_value = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{field_name} must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(
                f"{field_name} must be finite."
            )

        if not numeric_value.is_integer():
            raise ValueError(
                f"{field_name} must be an integer."
            )

        return int(
            numeric_value,
        )

    @staticmethod
    def _normalize_confidence(
        value: Any,
    ) -> float:
        try:
            confidence = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "confidence must be numeric."
            ) from exc

        if not math.isfinite(
            confidence,
        ):
            raise ValueError(
                "confidence must be finite."
            )

        if not (
            0.0
            <= confidence
            <= 1.0
        ):
            raise ValueError(
                "confidence must be in the 0.0..1.0 range."
            )

        return confidence

    @classmethod
    def _normalize_landmarks(
        cls,
        value: Any,
    ) -> dict[
        int,
        tuple[
            float,
            float,
            float,
        ],
    ]:
        if (
            value is None
            or isinstance(
                value,
                (
                    str,
                    bytes,
                    Mapping,
                ),
            )
        ):
            raise TypeError(
                "landmarks must be a sequence."
            )

        try:
            records = tuple(
                value,
            )
        except TypeError as exc:
            raise TypeError(
                "landmarks must be a sequence."
            ) from exc

        indexed: dict[
            int,
            tuple[
                float,
                float,
                float,
            ],
        ] = {}

        for record_index, record in enumerate(
            records,
        ):
            if not isinstance(
                record,
                Mapping,
            ):
                raise TypeError(
                    "landmarks records must be mappings."
                )

            landmark_id = cls._normalize_landmark_id(
                cls._require_record_field(
                    record,
                    "id",
                    record_index=record_index,
                )
            )

            if landmark_id in indexed:
                raise ValueError(
                    "landmark IDs must be unique."
                )

            x_coordinate = cls._normalize_xy_coordinate(
                cls._require_record_field(
                    record,
                    "x",
                    record_index=record_index,
                ),
                axis="x",
            )
            y_coordinate = cls._normalize_xy_coordinate(
                cls._require_record_field(
                    record,
                    "y",
                    record_index=record_index,
                ),
                axis="y",
            )
            z_coordinate = cls._normalize_z_coordinate(
                cls._require_record_field(
                    record,
                    "z",
                    record_index=record_index,
                )
            )

            indexed[
                landmark_id
            ] = (
                x_coordinate,
                y_coordinate,
                z_coordinate,
            )

        return indexed

    @staticmethod
    def _require_record_field(
        record: Mapping[str, Any],
        field_name: str,
        *,
        record_index: int,
    ) -> Any:
        try:
            return record[
                field_name
            ]
        except KeyError as exc:
            raise ValueError(
                f"landmarks[{record_index}] "
                f"is missing {field_name}."
            ) from exc

    @staticmethod
    def _normalize_landmark_id(
        value: Any,
    ) -> int:
        if (
            isinstance(
                value,
                bool,
            )
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise ValueError(
                "landmark id must be an integer."
            )

        landmark_id = int(
            value,
        )

        if landmark_id < 0:
            raise ValueError(
                "landmark id must not be negative."
            )

        return landmark_id

    @staticmethod
    def _normalize_xy_coordinate(
        value: Any,
        *,
        axis: str,
    ) -> float:
        try:
            coordinate = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{axis} coordinate must be numeric."
            ) from exc

        if not math.isfinite(
            coordinate,
        ):
            raise ValueError(
                f"{axis} coordinate must be finite."
            )

        if not (
            0.0
            <= coordinate
            <= 1.0
        ):
            raise ValueError(
                f"{axis} coordinate must be in the "
                "0.0..1.0 range."
            )

        return coordinate

    @staticmethod
    def _normalize_z_coordinate(
        value: Any,
    ) -> float:
        try:
            coordinate = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "z coordinate must be numeric."
            ) from exc

        if not math.isfinite(
            coordinate,
        ):
            raise ValueError(
                "z coordinate must be finite."
            )

        return coordinate

    @staticmethod
    def _build_metadata(
        *,
        source_metadata: Mapping[str, Any],
        schema_version: str,
        landmark_count: int,
    ) -> dict[str, Any]:
        return {
            "correspondence_version": (
                AtlasFlameMediaPipeLandmarkCorrespondence
                .VERSION
            ),
            "fixture_name": source_metadata.get(
                "fixture_name",
            ),
            "image_sha256": source_metadata.get(
                "source_image_sha256",
            ),
            "landmark_count": landmark_count,
            "mediapipe_version": source_metadata.get(
                "mediapipe_version",
            ),
            "model_asset": source_metadata.get(
                "model_asset",
            ),
            "schema_version": schema_version,
            "synthetic": source_metadata.get(
                "synthetic",
            ),
            "view_type": source_metadata.get(
                "view_type",
            ),
        }
