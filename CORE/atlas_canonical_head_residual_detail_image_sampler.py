from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)


class AtlasCanonicalHeadResidualDetailImageSampler:
    @classmethod
    def sample(
        cls,
        *,
        observation_id: str,
        source_view_id: str,
        scalar_detail_field: Any,
        confidence_field: Any,
        sample_indices: Any,
        sample_coordinates_normalized: Any,
    ) -> AtlasCanonicalHeadResidualDetailObservation:
        scalar_field = cls._normalize_field(
            scalar_detail_field,
            name="scalar_detail_field",
        )
        confidence = cls._normalize_field(
            confidence_field,
            name="confidence_field",
        )

        if confidence.shape != scalar_field.shape:
            raise ValueError(
                "confidence_field shape must match "
                "scalar_detail_field shape."
            )

        if (
            np.any(
                confidence < 0.0
            )
            or np.any(
                confidence > 1.0
            )
        ):
            raise ValueError(
                "confidence_field values must be "
                "in the 0.0..1.0 range."
            )

        try:
            indices = tuple(
                sample_indices
            )
        except TypeError as exc:
            raise TypeError(
                "sample_indices must be a sequence."
            ) from exc

        coordinates = np.asarray(
            sample_coordinates_normalized,
            dtype=np.float64,
        )

        expected_shape = (
            len(indices),
            2,
        )

        if coordinates.shape != expected_shape:
            raise ValueError(
                "sample_coordinates_normalized must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            coordinates
        ).all():
            raise ValueError(
                "sample_coordinates_normalized must contain "
                "only finite values."
            )

        if (
            np.any(
                coordinates < 0.0
            )
            or np.any(
                coordinates > 1.0
            )
        ):
            raise ValueError(
                "sample_coordinates_normalized values must be "
                "in the 0.0..1.0 range."
            )

        sampled_scalar = cls._bilinear_sample(
            scalar_field,
            coordinates,
        )
        sampled_confidence = cls._bilinear_sample(
            confidence,
            coordinates,
        )

        sampled_confidence = np.clip(
            sampled_confidence,
            0.0,
            1.0,
        )

        height, width = scalar_field.shape

        return AtlasCanonicalHeadResidualDetailObservation(
            observation_id=observation_id,
            source_view_id=source_view_id,
            image_width=width,
            image_height=height,
            sample_indices=indices,
            sample_coordinates_normalized=coordinates,
            scalar_detail=sampled_scalar,
            confidence=sampled_confidence,
        )

    @staticmethod
    def _normalize_field(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            field = np.asarray(
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

        if field.ndim != 2:
            raise ValueError(
                f"{name} must be two-dimensional."
            )

        if (
            field.shape[0] <= 0
            or field.shape[1] <= 0
        ):
            raise ValueError(
                f"{name} must not be empty."
            )

        if not np.isfinite(
            field
        ).all():
            raise ValueError(
                f"{name} must contain only finite values."
            )

        return field.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _bilinear_sample(
        field: np.ndarray,
        coordinates: np.ndarray,
    ) -> np.ndarray:
        height, width = field.shape

        x = (
            coordinates[:, 0]
            * (
                width - 1
            )
        )
        y = (
            coordinates[:, 1]
            * (
                height - 1
            )
        )

        x0 = np.floor(
            x
        ).astype(
            np.int64
        )
        y0 = np.floor(
            y
        ).astype(
            np.int64
        )

        x1 = np.minimum(
            x0 + 1,
            width - 1,
        )
        y1 = np.minimum(
            y0 + 1,
            height - 1,
        )

        wx = (
            x - x0
        )
        wy = (
            y - y0
        )

        top = (
            field[
                y0,
                x0,
            ]
            * (
                1.0 - wx
            )
            + field[
                y0,
                x1,
            ]
            * wx
        )

        bottom = (
            field[
                y1,
                x0,
            ]
            * (
                1.0 - wx
            )
            + field[
                y1,
                x1,
            ]
            * wx
        )

        return (
            top
            * (
                1.0 - wy
            )
            + bottom
            * wy
        ).astype(
            np.float64,
            copy=False,
        )
