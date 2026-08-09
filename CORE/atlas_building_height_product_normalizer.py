from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasBuildingHeightProductNormalization:
    source_height_m: float
    normalized_height_m: float
    normalized_height_mm: float
    block_median_height_m: float | None
    semantic_importance: float
    is_semantic_landmark: bool
    is_statistical_outlier: bool
    changed: bool
    reason: str
    landmark_distance_m: float | None = None
    landmark_context_distance_m: float | None = None
    near_landmark: bool = False


class AtlasBuildingHeightProductNormalizer:
    CONTEXT_HEIGHT_RATIO_MULTIPLIER = 1.25
    HIGH_SEMANTIC_IMPORTANCE = 0.80

    @staticmethod
    def _positive_finite(
        value,
        *,
        field_name,
    ) -> float:
        value = float(value)

        if (
            not math.isfinite(value)
            or value <= 0.0
        ):
            raise ValueError(
                f"{field_name} must be finite "
                "and greater than zero"
            )

        return value

    @staticmethod
    def _optional_positive_finite(
        value,
        *,
        field_name,
    ) -> float | None:
        if value is None:
            return None

        value = float(value)

        if (
            not math.isfinite(value)
            or value <= 0.0
        ):
            raise ValueError(
                f"{field_name} must be finite "
                "and greater than zero"
            )

        return value

    @classmethod
    def resolve(
        cls,
        *,
        source_height_m,
        block_median_height_m,
        scale_ratio,
        minimum_readable_height_mm,
        semantic_importance,
        is_semantic_landmark,
        maximum_block_height_ratio=2.0,
        landmark_distance_m=None,
        landmark_context_distance_m=50.0,
    ) -> AtlasBuildingHeightProductNormalization:
        source_height_m = cls._positive_finite(
            source_height_m,
            field_name="source_height_m",
        )

        block_median_height_m = (
            cls._optional_positive_finite(
                block_median_height_m,
                field_name="block_median_height_m",
            )
        )

        scale_ratio = cls._positive_finite(
            scale_ratio,
            field_name="scale_ratio",
        )

        minimum_readable_height_mm = (
            cls._positive_finite(
                minimum_readable_height_mm,
                field_name="minimum_readable_height_mm",
            )
        )

        maximum_block_height_ratio = (
            cls._positive_finite(
                maximum_block_height_ratio,
                field_name="maximum_block_height_ratio",
            )
        )

        landmark_distance_m = (
            cls._optional_positive_finite(
                landmark_distance_m,
                field_name="landmark_distance_m",
            )
        )

        landmark_context_distance_m = (
            cls._positive_finite(
                landmark_context_distance_m,
                field_name="landmark_context_distance_m",
            )
        )

        semantic_importance = float(
            semantic_importance
        )

        if (
            not math.isfinite(
                semantic_importance
            )
            or not (
                0.0
                <= semantic_importance
                <= 1.0
            )
        ):
            raise ValueError(
                "semantic_importance must be "
                "finite and within 0..1"
            )

        if not isinstance(
            is_semantic_landmark,
            bool,
        ):
            raise TypeError(
                "is_semantic_landmark must be bool"
            )

        near_landmark = (
            landmark_distance_m is not None
            and landmark_distance_m
            <= landmark_context_distance_m
        )

        source_height_mm = (
            source_height_m
            * 1000.0
            / scale_ratio
        )

        common = {
            "source_height_m": source_height_m,
            "block_median_height_m": (
                block_median_height_m
            ),
            "semantic_importance": (
                semantic_importance
            ),
            "landmark_distance_m": (
                landmark_distance_m
            ),
            "landmark_context_distance_m": (
                landmark_context_distance_m
            ),
            "near_landmark": near_landmark,
        }

        if is_semantic_landmark:
            return AtlasBuildingHeightProductNormalization(
                **common,
                normalized_height_m=source_height_m,
                normalized_height_mm=source_height_mm,
                is_semantic_landmark=True,
                is_statistical_outlier=False,
                changed=False,
                reason="semantic_landmark_preserved",
            )

        base_limit_m = None
        contextual_limit_m = None

        if block_median_height_m is not None:
            base_limit_m = (
                block_median_height_m
                * maximum_block_height_ratio
            )
            contextual_limit_m = (
                base_limit_m
                * cls.CONTEXT_HEIGHT_RATIO_MULTIPLIER
            )

        if (
            base_limit_m is not None
            and source_height_m > base_limit_m
        ):
            within_contextual_limit = (
                source_height_m
                <= contextual_limit_m
            )

            if (
                near_landmark
                and within_contextual_limit
            ):
                return AtlasBuildingHeightProductNormalization(
                    **common,
                    normalized_height_m=source_height_m,
                    normalized_height_mm=source_height_mm,
                    is_semantic_landmark=False,
                    is_statistical_outlier=False,
                    changed=False,
                    reason="landmark_context_preserved",
                )

            if (
                semantic_importance
                >= cls.HIGH_SEMANTIC_IMPORTANCE
                and within_contextual_limit
            ):
                return AtlasBuildingHeightProductNormalization(
                    **common,
                    normalized_height_m=source_height_m,
                    normalized_height_mm=source_height_mm,
                    is_semantic_landmark=False,
                    is_statistical_outlier=False,
                    changed=False,
                    reason="semantic_importance_preserved",
                )

            normalized_height_m = (
                contextual_limit_m
                if (
                    near_landmark
                    or semantic_importance
                    >= cls.HIGH_SEMANTIC_IMPORTANCE
                )
                else base_limit_m
            )

            normalized_height_mm = (
                normalized_height_m
                * 1000.0
                / scale_ratio
            )

            if (
                normalized_height_mm
                < minimum_readable_height_mm
            ):
                normalized_height_mm = (
                    minimum_readable_height_mm
                )
                normalized_height_m = (
                    normalized_height_mm
                    * scale_ratio
                    / 1000.0
                )

            return AtlasBuildingHeightProductNormalization(
                **common,
                normalized_height_m=normalized_height_m,
                normalized_height_mm=normalized_height_mm,
                is_semantic_landmark=False,
                is_statistical_outlier=True,
                changed=True,
                reason="block_height_outlier",
            )

        if (
            source_height_mm
            < minimum_readable_height_mm
        ):
            normalized_height_mm = (
                minimum_readable_height_mm
            )
            normalized_height_m = (
                normalized_height_mm
                * scale_ratio
                / 1000.0
            )

            return AtlasBuildingHeightProductNormalization(
                **common,
                normalized_height_m=normalized_height_m,
                normalized_height_mm=normalized_height_mm,
                is_semantic_landmark=False,
                is_statistical_outlier=False,
                changed=True,
                reason="physical_minimum",
            )

        return AtlasBuildingHeightProductNormalization(
            **common,
            normalized_height_m=source_height_m,
            normalized_height_mm=source_height_mm,
            is_semantic_landmark=False,
            is_statistical_outlier=False,
            changed=False,
            reason="source_height_preserved",
        )
