from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasCanonicalHeadLocalFacialFeatureXYCorrectionResult:
    vertices: np.ndarray
    applied_channels: tuple[str, ...]
    provenance: str
    support_source: str
    dense_semantics_invented: bool
    hair_semantics_used: bool
    ear_semantics_used: bool


class AtlasCanonicalHeadLocalFacialFeatureXYCorrection:
    """
    Applies bounded, support-weighted local XY affine corrections
    to explicitly authorized facial-feature channels.

    This owner does not derive dense semantics. It consumes explicit
    external support arrays and leaves Z unchanged.
    """

    SUPPORTED_CHANNELS = (
        "nose_bridge",
        "nose_body_base",
        "mouth_lips",
    )

    PROVENANCE = (
        "atlas_canonical_head_local_facial_feature_xy_correction:v1"
    )

    CHANNEL_APPLICATION_ORDER = SUPPORTED_CHANNELS

    @classmethod
    def apply(
        cls,
        *,
        vertices: np.ndarray,
        channels: Mapping[str, Mapping[str, Any]],
    ) -> AtlasCanonicalHeadLocalFacialFeatureXYCorrectionResult:
        points = np.asarray(vertices, dtype=np.float64)

        if (
            points.ndim != 2
            or points.shape[1] != 3
            or points.shape[0] == 0
        ):
            raise ValueError(
                "vertices must have shape (N, 3) with N > 0"
            )

        if not np.all(np.isfinite(points)):
            raise ValueError(
                "vertices must contain only finite coordinates"
            )

        if not isinstance(channels, Mapping):
            raise TypeError(
                "channels must be a mapping"
            )

        unknown = sorted(
            set(channels.keys())
            - set(cls.SUPPORTED_CHANNELS)
        )

        if unknown:
            raise ValueError(
                "unsupported channel: "
                + ", ".join(str(name) for name in unknown)
            )

        normalized: dict[str, dict[str, np.ndarray | tuple[float, float]]] = {}

        for channel_name, payload in channels.items():
            if not isinstance(payload, Mapping):
                raise TypeError(
                    f"{channel_name} channel must be a mapping"
                )

            support = np.asarray(
                payload.get("support"),
                dtype=np.float64,
            )

            if (
                support.ndim != 1
                or support.shape[0] != points.shape[0]
            ):
                raise ValueError(
                    f"{channel_name} support must contain "
                    "exactly one value per vertex"
                )

            if not np.all(np.isfinite(support)):
                raise ValueError(
                    f"{channel_name} support must be finite"
                )

            if np.any(support < 0.0) or np.any(support > 1.0):
                raise ValueError(
                    f"{channel_name} support must be within [0, 1]"
                )

            pivot_xy = cls._finite_pair(
                payload.get("pivot_xy"),
                field_name=f"{channel_name}.pivot_xy",
            )

            scale_xy = cls._positive_pair(
                payload.get("scale_xy"),
                field_name=f"{channel_name}.scale_xy",
            )

            translation_xy = cls._finite_pair(
                payload.get("translation_xy"),
                field_name=f"{channel_name}.translation_xy",
            )

            normalized[channel_name] = {
                "support": support,
                "pivot_xy": pivot_xy,
                "scale_xy": scale_xy,
                "translation_xy": translation_xy,
            }

        corrected = points.copy()
        original_z = corrected[:, 2].copy()
        applied_channels: list[str] = []

        for channel_name in cls.CHANNEL_APPLICATION_ORDER:
            if channel_name not in normalized:
                continue

            payload = normalized[channel_name]

            support = np.asarray(
                payload["support"],
                dtype=np.float64,
            )

            pivot_x, pivot_y = payload["pivot_xy"]
            scale_x, scale_y = payload["scale_xy"]
            translate_x, translate_y = payload["translation_xy"]

            current_xy = corrected[:, :2].copy()

            full_xy = np.empty_like(current_xy)

            full_xy[:, 0] = (
                pivot_x
                + scale_x * (current_xy[:, 0] - pivot_x)
                + translate_x
            )

            full_xy[:, 1] = (
                pivot_y
                + scale_y * (current_xy[:, 1] - pivot_y)
                + translate_y
            )

            alpha = support[:, None]

            corrected[:, :2] = (
                (1.0 - alpha) * current_xy
                + alpha * full_xy
            )

            applied_channels.append(channel_name)

        corrected[:, 2] = original_z

        return AtlasCanonicalHeadLocalFacialFeatureXYCorrectionResult(
            vertices=corrected,
            applied_channels=tuple(applied_channels),
            provenance=cls.PROVENANCE,
            support_source="explicit_external_feature_support",
            dense_semantics_invented=False,
            hair_semantics_used=False,
            ear_semantics_used=False,
        )

    @staticmethod
    def _finite_pair(
        value: Any,
        *,
        field_name: str,
    ) -> tuple[float, float]:
        if isinstance(value, (str, bytes)):
            raise ValueError(
                f"{field_name} must contain exactly two finite values"
            )

        try:
            items = tuple(value)
        except TypeError as exc:
            raise ValueError(
                f"{field_name} must contain exactly two finite values"
            ) from exc

        if len(items) != 2:
            raise ValueError(
                f"{field_name} must contain exactly two finite values"
            )

        resolved = tuple(float(item) for item in items)

        if not all(np.isfinite(item) for item in resolved):
            raise ValueError(
                f"{field_name} must contain exactly two finite values"
            )

        return resolved

    @classmethod
    def _positive_pair(
        cls,
        value: Any,
        *,
        field_name: str,
    ) -> tuple[float, float]:
        resolved = cls._finite_pair(
            value,
            field_name=field_name,
        )

        if any(item <= 0.0 for item in resolved):
            raise ValueError(
                f"{field_name} values must be greater than zero"
            )

        return resolved
