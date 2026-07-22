from __future__ import annotations

import json
import math
from collections.abc import Mapping
from numbers import Integral
from pathlib import Path
from typing import Any


class AtlasMediaPipePortraitLandmarkJsonExporter:
    """
    Builds and writes deterministic MediaPipe landmark JSON payloads.

    This contract is independent of the mediapipe package. Runtime
    inference will be connected separately through a Python 3.12 CLI.
    """

    SCHEMA_VERSION = "atlas-mediapipe-face-landmarks-v1"
    PROVIDER_ID = "mediapipe-face-landmarker-tasks"
    EXPECTED_LANDMARK_COUNT = 478

    @classmethod
    def build_payload(
        cls,
        *,
        image_width: Any,
        image_height: Any,
        confidence: Any,
        landmarks: Any,
        mediapipe_version: Any,
        model_asset: Any,
        source_image_sha256: Any,
        view_type: Any,
    ) -> dict[str, Any]:
        normalized_width = cls._normalize_positive_integer(
            image_width,
            field_name="image_width",
        )
        normalized_height = cls._normalize_positive_integer(
            image_height,
            field_name="image_height",
        )
        normalized_confidence = cls._normalize_confidence(
            confidence,
        )
        normalized_landmarks = cls._normalize_landmarks(
            landmarks,
        )

        normalized_mediapipe_version = cls._normalize_text(
            mediapipe_version,
            field_name="mediapipe_version",
        )
        normalized_model_asset = cls._normalize_text(
            model_asset,
            field_name="model_asset",
        )
        normalized_source_image_sha256 = cls._normalize_text(
            source_image_sha256,
            field_name="source_image_sha256",
        )
        normalized_view_type = cls._normalize_text(
            view_type,
            field_name="view_type",
        )

        return {
            "schema_version": cls.SCHEMA_VERSION,
            "provider_id": cls.PROVIDER_ID,
            "image_width": normalized_width,
            "image_height": normalized_height,
            "confidence": normalized_confidence,
            "landmark_count": len(
                normalized_landmarks,
            ),
            "landmarks": normalized_landmarks,
            "metadata": {
                "mediapipe_version": normalized_mediapipe_version,
                "model_asset": normalized_model_asset,
                "source_image_sha256": (
                    normalized_source_image_sha256
                ),
                "synthetic": False,
                "view_type": normalized_view_type,
            },
        }

    @staticmethod
    def write(
        output_path: Any,
        payload: Any,
    ) -> Path:
        path = AtlasMediaPipePortraitLandmarkJsonExporter._normalize_path(
            output_path,
        )

        if not isinstance(
            payload,
            Mapping,
        ):
            raise TypeError(
                "payload must be a mapping."
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            encoded = json.dumps(
                dict(
                    payload,
                ),
                allow_nan=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "payload must be JSON serializable."
            ) from exc

        path.write_text(
            encoded + "\n",
            encoding="utf-8",
        )

        return path

    @classmethod
    def _normalize_landmarks(
        cls,
        value: Any,
    ) -> list[dict[str, float | int]]:
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

        if len(
            records,
        ) != cls.EXPECTED_LANDMARK_COUNT:
            raise ValueError(
                "landmarks must contain exactly "
                f"{cls.EXPECTED_LANDMARK_COUNT} records."
            )

        indexed: dict[
            int,
            dict[str, float | int],
        ] = {}

        for record_index, record in enumerate(
            records,
        ):
            if not isinstance(
                record,
                Mapping,
            ):
                raise TypeError(
                    "landmark records must be mappings."
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

            indexed[
                landmark_id
            ] = {
                "id": landmark_id,
                "x": cls._normalize_xy_coordinate(
                    cls._require_record_field(
                        record,
                        "x",
                        record_index=record_index,
                    ),
                    axis="x",
                ),
                "y": cls._normalize_xy_coordinate(
                    cls._require_record_field(
                        record,
                        "y",
                        record_index=record_index,
                    ),
                    axis="y",
                ),
                "z": cls._normalize_z_coordinate(
                    cls._require_record_field(
                        record,
                        "z",
                        record_index=record_index,
                    )
                ),
            }

        expected_ids = set(
            range(
                cls.EXPECTED_LANDMARK_COUNT,
            )
        )
        actual_ids = set(
            indexed,
        )

        if actual_ids != expected_ids:
            raise ValueError(
                "landmarks must contain exactly the IDs "
                "0 through 477."
            )

        return [
            indexed[
                landmark_id
            ]
            for landmark_id in range(
                cls.EXPECTED_LANDMARK_COUNT,
            )
        ]

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
            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    "output_path must not be blank."
                )

            return Path(
                normalized,
            )

        raise TypeError(
            "output_path must be a string or pathlib.Path."
        )

    @staticmethod
    def _normalize_positive_integer(
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

        integer_value = int(
            numeric_value,
        )

        if integer_value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return integer_value

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

    @staticmethod
    def _normalize_text(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

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

        if not (
            0
            <= landmark_id
            < 478
        ):
            raise ValueError(
                "landmark id must be in the 0..477 range."
            )

        return landmark_id

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
