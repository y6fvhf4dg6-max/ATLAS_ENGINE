from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)

_PROVIDER_ID = "manual-ground-truth-fixture"
_DOCUMENT_TYPE = "portrait_landmark_ground_truth"


def load_portrait_landmark_ground_truth(
    path: str | Path,
) -> AtlasPortraitLandmarkResult:
    """
    Loads a manual portrait-landmark ground-truth
    JSON document and converts it to the immutable
    portrait landmark result contract.
    """

    document_path = Path(path)

    try:
        raw_document = document_path.read_text(
            encoding="utf-8",
        )
    except OSError as exc:
        raise ValueError("ground-truth document could not be read.") from exc

    try:
        document = json.loads(
            raw_document,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("ground-truth document must contain valid JSON.") from exc

    if not isinstance(
        document,
        dict,
    ):
        raise ValueError("ground-truth document must be a JSON object.")

    if document.get("type") != _DOCUMENT_TYPE:
        raise ValueError("ground-truth document type is invalid.")

    image = _require_mapping(
        document,
        "image",
    )

    landmarks = _require_mapping(
        document,
        "landmarks",
    )

    pixel_landmarks = _require_mapping(
        document,
        "pixel_landmarks",
    )

    image_width = _require_positive_integer(
        image,
        "width",
    )

    image_height = _require_positive_integer(
        image,
        "height",
    )

    if set(landmarks) != set(pixel_landmarks):
        raise ValueError("normalized and pixel landmark names must match.")

    _validate_pixel_mapping(
        landmarks=landmarks,
        pixel_landmarks=pixel_landmarks,
        image_width=image_width,
        image_height=image_height,
    )

    metadata = _build_metadata(
        document=document,
        image=image,
    )

    return AtlasPortraitLandmarkResult(
        image_width=image_width,
        image_height=image_height,
        landmarks=landmarks,
        confidence=1.0,
        provider_id=_PROVIDER_ID,
        metadata=metadata,
    )


def _require_mapping(
    mapping: dict[str, Any],
    key: str,
) -> dict[str, Any]:
    value = mapping.get(key)

    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(f"{key} must be a mapping.")

    if not value:
        raise ValueError(f"{key} must not be empty.")

    return value


def _require_positive_integer(
    mapping: dict[str, Any],
    key: str,
) -> int:
    value = mapping.get(key)

    try:
        numeric_value = float(value)
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(f"{key} must be numeric.") from exc

    if not math.isfinite(
        numeric_value,
    ):
        raise ValueError(f"{key} must be finite.")

    if not numeric_value.is_integer():
        raise ValueError(f"{key} must be an integer.")

    integer_value = int(
        numeric_value,
    )

    if integer_value <= 0:
        raise ValueError(f"{key} must be greater than zero.")

    return integer_value


def _validate_pixel_mapping(
    *,
    landmarks: dict[str, Any],
    pixel_landmarks: dict[str, Any],
    image_width: int,
    image_height: int,
) -> None:
    for name, normalized_coordinates in landmarks.items():
        normalized_x, normalized_y = _coordinates(
            normalized_coordinates,
            name=name,
            coordinate_type="normalized",
        )

        pixel_x, pixel_y = _coordinates(
            pixel_landmarks[name],
            name=name,
            coordinate_type="pixel",
        )

        expected_pixel_x = normalized_x * (image_width - 1)

        expected_pixel_y = normalized_y * (image_height - 1)

        if not math.isclose(
            pixel_x,
            expected_pixel_x,
            abs_tol=0.0011,
        ):
            raise ValueError(f"{name} pixel coordinate x is inconsistent.")

        if not math.isclose(
            pixel_y,
            expected_pixel_y,
            abs_tol=0.0011,
        ):
            raise ValueError(f"{name} pixel coordinate y is inconsistent.")


def _coordinates(
    value: Any,
    *,
    name: str,
    coordinate_type: str,
) -> tuple[float, float]:
    if isinstance(
        value,
        (str, bytes),
    ):
        raise ValueError(
            f"{name} {coordinate_type} coordinates "
            "must contain exactly two numeric values."
        )

    try:
        coordinates = tuple(
            value,
        )
    except TypeError as exc:
        raise ValueError(
            f"{name} {coordinate_type} coordinates "
            "must contain exactly two numeric values."
        ) from exc

    if len(coordinates) != 2:
        raise ValueError(
            f"{name} {coordinate_type} coordinates "
            "must contain exactly two numeric values."
        )

    result = []

    for axis, coordinate in zip(
        ("x", "y"),
        coordinates,
        strict=True,
    ):
        try:
            numeric_coordinate = float(
                coordinate,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} {coordinate_type} " f"{axis} coordinate must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_coordinate,
        ):
            raise ValueError(
                f"{name} {coordinate_type} " f"{axis} coordinate must be finite."
            )

        result.append(
            numeric_coordinate,
        )

    return (
        result[0],
        result[1],
    )


def _build_metadata(
    *,
    document: dict[str, Any],
    image: dict[str, Any],
) -> dict[str, Any]:
    source_metadata = document.get(
        "metadata",
        {},
    )

    if not isinstance(
        source_metadata,
        dict,
    ):
        raise ValueError("metadata must be a mapping.")

    return {
        "fixture_name": document.get(
            "fixture_name",
        ),
        "view_type": document.get(
            "view_type",
        ),
        "synthetic": source_metadata.get(
            "synthetic",
        ),
        "manual_ground_truth": source_metadata.get(
            "manual_ground_truth",
        ),
        "image_path": image.get(
            "path",
        ),
        "image_sha256": image.get(
            "sha256",
        ),
    }
