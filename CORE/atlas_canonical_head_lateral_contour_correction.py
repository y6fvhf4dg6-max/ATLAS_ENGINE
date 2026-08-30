from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AtlasCanonicalHeadLateralContourCorrectionResult:
    vertices: np.ndarray
    local_x_factor: np.ndarray
    lateral_support: np.ndarray
    provenance: str
    semantic_support: str
    hair_semantics_used: bool
    ear_semantics_used: bool


class AtlasCanonicalHeadLateralContourCorrection:
    """
    Applies bounded X-only contraction to the lateral outer contour.

    The central face is protected by a radius expressed relative to the
    subject-specific outer-eye half span. Correction rises smoothly from
    zero at the protection radius to full support at the outer radius.

    This owner does not infer or claim ear or hair semantics. The supplied
    vertical_factors are external geometric calibration evidence and are
    applied only where lateral support is non-zero.
    """

    PROVENANCE = (
        "atlas_canonical_head_lateral_contour_correction:v1"
    )

    @classmethod
    def apply(
        cls,
        *,
        vertices: np.ndarray,
        pivot_x: float,
        eye_half_span: float,
        protect_radius_eye_half: float,
        full_radius_eye_half: float,
        vertical_factors: np.ndarray,
        strength: float,
    ) -> AtlasCanonicalHeadLateralContourCorrectionResult:
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

        pivot = cls._finite_float(
            pivot_x,
            field_name="pivot_x",
        )

        eye_span = cls._positive_finite_float(
            eye_half_span,
            field_name="eye_half_span",
        )

        protect_radius = cls._nonnegative_finite_float(
            protect_radius_eye_half,
            field_name="protect_radius_eye_half",
        )

        full_radius = cls._positive_finite_float(
            full_radius_eye_half,
            field_name="full_radius_eye_half",
        )

        if full_radius <= protect_radius:
            raise ValueError(
                "full_radius_eye_half must be greater than "
                "protect_radius_eye_half"
            )

        resolved_strength = cls._unit_interval_float(
            strength,
            field_name="strength",
        )

        factors = np.asarray(
            vertical_factors,
            dtype=np.float64,
        )

        if (
            factors.ndim != 1
            or factors.shape[0] != points.shape[0]
        ):
            raise ValueError(
                "vertical_factors must contain exactly one "
                "value per vertex"
            )

        if not np.all(np.isfinite(factors)):
            raise ValueError(
                "vertical_factors must contain only finite values"
            )

        if np.any(factors <= 0.0):
            raise ValueError(
                "vertical_factors must be strictly positive"
            )

        protect_distance = protect_radius * eye_span
        full_distance = full_radius * eye_span

        abs_dx = np.abs(
            points[:, 0] - pivot
        )

        normalized_lateral = (
            (abs_dx - protect_distance)
            / (full_distance - protect_distance)
        )

        clipped = np.clip(
            normalized_lateral,
            0.0,
            1.0,
        )

        lateral_support = (
            clipped
            * clipped
            * (3.0 - 2.0 * clipped)
        )

        desired_factor = (
            1.0
            + resolved_strength
            * (factors - 1.0)
        )

        local_x_factor = (
            1.0
            + lateral_support
            * (desired_factor - 1.0)
        )

        corrected = points.copy()

        corrected[:, 0] = (
            pivot
            + local_x_factor
            * (points[:, 0] - pivot)
        )

        return (
            AtlasCanonicalHeadLateralContourCorrectionResult(
                vertices=corrected,
                local_x_factor=local_x_factor,
                lateral_support=lateral_support,
                provenance=cls.PROVENANCE,
                semantic_support="none",
                hair_semantics_used=False,
                ear_semantics_used=False,
            )
        )

    @staticmethod
    def _finite_float(
        value: float,
        *,
        field_name: str,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be finite"
            )

        try:
            resolved = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must be finite"
            ) from exc

        if not np.isfinite(resolved):
            raise ValueError(
                f"{field_name} must be finite"
            )

        return resolved

    @classmethod
    def _positive_finite_float(
        cls,
        value: float,
        *,
        field_name: str,
    ) -> float:
        resolved = cls._finite_float(
            value,
            field_name=field_name,
        )

        if resolved <= 0.0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )

        return resolved

    @classmethod
    def _nonnegative_finite_float(
        cls,
        value: float,
        *,
        field_name: str,
    ) -> float:
        resolved = cls._finite_float(
            value,
            field_name=field_name,
        )

        if resolved < 0.0:
            raise ValueError(
                f"{field_name} must be nonnegative"
            )

        return resolved

    @classmethod
    def _unit_interval_float(
        cls,
        value: float,
        *,
        field_name: str,
    ) -> float:
        resolved = cls._finite_float(
            value,
            field_name=field_name,
        )

        if resolved < 0.0 or resolved > 1.0:
            raise ValueError(
                f"{field_name} must be within [0, 1]"
            )

        return resolved
