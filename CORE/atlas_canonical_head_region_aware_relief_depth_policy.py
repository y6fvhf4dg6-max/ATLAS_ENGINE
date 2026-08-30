from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasCanonicalHeadRegionAwareReliefDepthResult:
    depth_map_mm: np.ndarray
    coverage_map: np.ndarray
    metadata: dict[str, Any]


class AtlasCanonicalHeadRegionAwareReliefDepthPolicy:
    """
    Allocate bounded local physical depth to raster-space facial regions.

    The policy operates after frontal visible-surface rasterization.

    It does not:
    - invent dense FLAME semantic labels;
    - modify canonical identity parameters;
    - modify pose or expression;
    - perform camera fitting;
    - construct mesh topology;
    - make likeness or production acceptance decisions.

    Semantic support is supplied explicitly as raster-space masks derived
    from externally validated facial landmarks.

    Architecture:
    1. Preserve the visible surface as a global monotonic linear depth base.
    2. Add a bounded local differential field:
       - nose structure receives a positive physical-depth allocation;
       - upper-lip / philtrum structure receives an opposing allocation.
    3. Clamp the final surface to the finite relief-height envelope.

    The bounded differential is deliberately small. Its purpose is to
    recover sub-layer central-face distinctions without replacing the
    canonical macro surface.
    """

    TRANSFER_KIND = (
        "region_aware_bounded_local_depth_allocation"
    )

    POLICY_PROVENANCE = (
        "atlas_canonical_head_region_aware_relief_depth_policy:v1"
    )

    REQUIRED_REGIONS = (
        "eye_glasses",
        "nose_bridge",
        "nose_body",
        "nose_base",
        "philtrum",
        "upper_lip",
        "lower_lip",
        "left_cheek",
        "right_cheek",
        "chin",
        "face_interior",
        "face_boundary_falloff",
    )

    @classmethod
    def transfer(
        cls,
        *,
        source_depth_map: Any,
        coverage_map: Any,
        region_masks: Any,
        relief_height_mm: Any,
        minimum_printable_separation_mm: Any,
    ) -> AtlasCanonicalHeadRegionAwareReliefDepthResult:
        source = cls._depth_map(
            source_depth_map
        )

        coverage = cls._coverage_map(
            coverage_map,
            shape=source.shape,
        )

        regions = cls._region_masks(
            region_masks,
            shape=source.shape,
        )

        relief_height = cls._positive_finite(
            relief_height_mm,
            name="relief_height_mm",
        )

        minimum_separation = cls._positive_finite(
            minimum_printable_separation_mm,
            name="minimum_printable_separation_mm",
        )

        if minimum_separation > relief_height:
            raise ValueError(
                "minimum_printable_separation_mm must not "
                "exceed relief_height_mm"
            )

        if not np.any(coverage):
            raise ValueError(
                "coverage_map must contain covered samples"
            )

        covered_depth = source[
            coverage
        ]

        base_low_percentile = 0.25
        base_high_percentile = 99.75

        source_low = float(
            np.percentile(
                covered_depth,
                base_low_percentile,
            )
        )
        source_high = float(
            np.percentile(
                covered_depth,
                base_high_percentile,
            )
        )
        source_range = (
            source_high
            - source_low
        )

        if (
            not np.isfinite(source_range)
            or source_range <= 1.0e-15
        ):
            raise ValueError(
                "source_depth_map must contain a positive "
                "robust depth range inside coverage_map"
            )

        base = np.zeros_like(
            source,
            dtype=np.float64,
        )

        robust_depth = np.clip(
            covered_depth,
            source_low,
            source_high,
        )

        base[coverage] = (
            (
                robust_depth
                - source_low
            )
            / source_range
            * relief_height
        )

        # Empirically bounded central-face differential support.
        #
        # The constants below are dimensionless multipliers of the caller's
        # explicit minimum printable separation. They were selected from the
        # Item 11.15 real-candidate diagnostic sweep rather than encoded as
        # subject-specific millimeter constants.
        nose_allocation_factor = 1.10
        lower_face_allocation_factor = 0.75

        nose_positive_allocation = (
            nose_allocation_factor
            * minimum_separation
        )
        lower_face_negative_allocation = (
            lower_face_allocation_factor
            * minimum_separation
        )

        nose_support = np.maximum.reduce(
            (
                0.50 * regions["nose_bridge"],
                regions["nose_body"],
                0.75 * regions["nose_base"],
            )
        )

        lower_face_support = np.maximum.reduce(
            (
                regions["upper_lip"],
                0.80 * regions["lower_lip"],
                0.65 * regions["philtrum"],
                0.70 * regions["chin"],
            )
        )

        face_support = np.clip(
            regions["face_interior"],
            0.0,
            1.0,
        )

        boundary_suppression = np.clip(
            1.0
            - regions["face_boundary_falloff"],
            0.0,
            1.0,
        )

        nose_support = np.clip(
            nose_support
            * face_support
            * boundary_suppression,
            0.0,
            1.0,
        )

        lower_face_support = np.clip(
            lower_face_support
            * face_support
            * boundary_suppression,
            0.0,
            1.0,
        )

        local_offset = (
            nose_support
            * nose_positive_allocation
            - lower_face_support
            * lower_face_negative_allocation
        )

        result = base.copy()

        result[coverage] = np.clip(
            base[coverage]
            + local_offset[coverage],
            0.0,
            relief_height,
        )

        result[
            ~coverage
        ] = 0.0

        result = np.asarray(
            result,
            dtype=np.float64,
        )

        output_coverage = np.asarray(
            coverage,
            dtype=np.bool_,
        ).copy()

        result.setflags(
            write=False
        )
        output_coverage.setflags(
            write=False
        )

        metadata = {
            "transfer_kind": (
                cls.TRANSFER_KIND
            ),
            "policy_provenance": (
                cls.POLICY_PROVENANCE
            ),
            "semantic_support": (
                "raster_region_masks"
            ),
            "relief_height_mm": (
                relief_height
            ),
            "minimum_printable_separation_mm": (
                minimum_separation
            ),
            "base_transfer": (
                "covered_robust_percentile_linear"
            ),
            "base_low_percentile": (
                base_low_percentile
            ),
            "base_high_percentile": (
                base_high_percentile
            ),
            "local_allocation": (
                "nose_positive_coherent_lower_face_negative"
            ),
            "nose_allocation_factor": (
                nose_allocation_factor
            ),
            "lower_face_allocation_factor": (
                lower_face_allocation_factor
            ),
            "nose_positive_allocation_mm": (
                nose_positive_allocation
            ),
            "lower_face_negative_allocation_mm": (
                lower_face_negative_allocation
            ),
            "lower_face_regions": (
                "upper_lip",
                "lower_lip",
                "philtrum",
                "chin",
            ),
            "lower_face_region_weights": {
                "upper_lip": 1.00,
                "lower_lip": 0.80,
                "philtrum": 0.65,
                "chin": 0.70,
            },
        }

        return (
            AtlasCanonicalHeadRegionAwareReliefDepthResult(
                depth_map_mm=result,
                coverage_map=output_coverage,
                metadata=metadata,
            )
        )

    @staticmethod
    def _depth_map(
        value: Any,
    ) -> np.ndarray:
        try:
            result = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "source_depth_map must be numeric"
            ) from exc

        if result.ndim != 2:
            raise ValueError(
                "source_depth_map must be two-dimensional"
            )

        if not np.all(
            np.isfinite(result)
        ):
            raise ValueError(
                "source_depth_map contains non-finite values"
            )

        return result.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _coverage_map(
        value: Any,
        *,
        shape: tuple[int, int],
    ) -> np.ndarray:
        result = np.asarray(
            value
        )

        if result.shape != shape:
            raise ValueError(
                "coverage_map shape must match source_depth_map"
            )

        return result.astype(
            np.bool_,
            copy=True,
        )

    @classmethod
    def _region_masks(
        cls,
        value: Any,
        *,
        shape: tuple[int, int],
    ) -> dict[str, np.ndarray]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "region_masks must be a mapping"
            )

        validated: dict[str, np.ndarray] = {}

        for region_name in cls.REQUIRED_REGIONS:
            if region_name not in value:
                raise ValueError(
                    "region_masks is missing required region: "
                    f"{region_name}"
                )

            try:
                region = np.asarray(
                    value[region_name],
                    dtype=np.float64,
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    f"region mask {region_name!r} must be numeric"
                ) from exc

            if region.shape != shape:
                raise ValueError(
                    f"region mask {region_name!r} shape "
                    f"must match source_depth_map"
                )

            if not np.all(
                np.isfinite(region)
            ):
                raise ValueError(
                    f"region mask {region_name!r} contains "
                    "non-finite values"
                )

            if (
                np.any(region < 0.0)
                or np.any(region > 1.0)
            ):
                raise ValueError(
                    f"region mask {region_name!r} must stay "
                    "within 0..1"
                )

            validated[
                region_name
            ] = region.astype(
                np.float64,
                copy=True,
            )

        return validated

    @staticmethod
    def _positive_finite(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            result = float(
                value
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise ValueError(
                f"{name} must be positive and finite"
            ) from exc

        if (
            not np.isfinite(result)
            or result <= 0.0
        ):
            raise ValueError(
                f"{name} must be positive and finite"
            )

        return result
