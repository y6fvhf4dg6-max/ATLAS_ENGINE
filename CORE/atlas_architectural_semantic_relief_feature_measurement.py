from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from CORE.atlas_architectural_relief_detail_scale_filter import (
    AtlasArchitecturalReliefDetailScaleFilter,
    AtlasArchitecturalReliefDetailScaleProfile,
)


class AtlasArchitecturalSemanticReliefFeatureMeasurement:
    @staticmethod
    def _detail_map(values: Any) -> np.ndarray:
        try:
            array = np.asarray(
                values,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "detail_map must be numeric"
            ) from exc

        if array.ndim != 2:
            raise ValueError(
                "detail_map must be two-dimensional"
            )

        if array.size == 0:
            raise ValueError(
                "detail_map must not be empty"
            )

        if not np.isfinite(array).all():
            raise ValueError(
                "detail_map must contain only finite values"
            )

        return array.copy()

    @staticmethod
    def _feature_masks(
        values: Any,
        *,
        shape: tuple[int, int],
    ) -> dict[str, np.ndarray]:
        if not isinstance(
            values,
            Mapping,
        ):
            raise TypeError(
                "feature_masks must be a mapping"
            )

        if not values:
            raise ValueError(
                "feature_masks must not be empty"
            )

        normalized = {}

        for raw_name, raw_mask in values.items():
            name = str(
                raw_name
            ).strip()

            if not name:
                raise ValueError(
                    "feature name must not be blank"
                )

            if name in normalized:
                raise ValueError(
                    f"duplicate feature name: {name}"
                )

            mask = np.asarray(
                raw_mask,
                dtype=bool,
            )

            if mask.ndim != 2:
                raise ValueError(
                    f"feature mask {name} must be two-dimensional"
                )

            if mask.shape != shape:
                raise ValueError(
                    f"feature mask {name} shape must match detail_map"
                )

            normalized[name] = mask.copy()

        return normalized

    @classmethod
    def measure(
        cls,
        *,
        detail_map: Any,
        feature_masks: Mapping[str, Any],
        width_mm: float,
        depth_mm: float,
        detail_profile: AtlasArchitecturalReliefDetailScaleProfile,
    ) -> dict[str, Any]:
        detail = cls._detail_map(
            detail_map
        )

        masks = cls._feature_masks(
            feature_masks,
            shape=detail.shape,
        )

        if not isinstance(
            detail_profile,
            AtlasArchitecturalReliefDetailScaleProfile,
        ):
            raise TypeError(
                "detail_profile must be an "
                "AtlasArchitecturalReliefDetailScaleProfile"
            )

        features = {}

        for feature_name, mask in masks.items():
            masked_detail = np.zeros_like(
                detail,
                dtype=np.float64,
            )

            masked_detail[
                mask
            ] = detail[
                mask
            ]

            measurement = (
                AtlasArchitecturalReliefDetailScaleFilter
                .filter(
                    detail_map=masked_detail,
                    width_mm=width_mm,
                    depth_mm=depth_mm,
                    profile=detail_profile,
                )
            )

            active_component_count = len(
                measurement[
                    "component_reports"
                ]
            )

            retained_component_count = int(
                measurement[
                    "retained_component_count"
                ]
            )

            culled_component_count = int(
                measurement[
                    "culled_component_count"
                ]
            )

            active_pixel_mask = (
                np.abs(masked_detail)
                >= detail_profile.activity_threshold
            )

            active_pixel_count = int(
                np.count_nonzero(
                    active_pixel_mask
                )
            )

            retained_pixel_mask = (
                active_pixel_mask
                & (
                    np.asarray(
                        measurement["retention_map"],
                        dtype=np.float64,
                    )
                    > 0.0
                )
            )

            retained_pixel_count = int(
                np.count_nonzero(
                    retained_pixel_mask
                )
            )

            retained_active_pixel_ratio = (
                0.0
                if active_pixel_count == 0
                else (
                    retained_pixel_count
                    / active_pixel_count
                )
            )

            features[feature_name] = {
                "feature_name": feature_name,
                "active_component_count": (
                    active_component_count
                ),
                "retained_component_count": (
                    retained_component_count
                ),
                "culled_component_count": (
                    culled_component_count
                ),
                "feature_retained": bool(
                    retained_component_count > 0
                ),
                "active_pixel_count": (
                    active_pixel_count
                ),
                "retained_pixel_count": (
                    retained_pixel_count
                ),
                "retained_active_pixel_ratio": (
                    float(
                        retained_active_pixel_ratio
                    )
                ),
                "component_reports": tuple(
                    measurement[
                        "component_reports"
                    ]
                ),
                "pixel_pitch_x_mm": float(
                    measurement[
                        "pixel_pitch_x_mm"
                    ]
                ),
                "pixel_pitch_y_mm": float(
                    measurement[
                        "pixel_pitch_y_mm"
                    ]
                ),
            }

        return {
            "type": (
                "architectural_semantic_relief_feature_measurement"
            ),
            "shape": detail.shape,
            "width_mm": float(width_mm),
            "depth_mm": float(depth_mm),
            "features": features,
        }
