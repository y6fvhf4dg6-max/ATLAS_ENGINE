from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefStructureProfile:
    strength: float = 1.0
    max_correction: float = 0.05

    def __post_init__(self) -> None:
        strength = self._finite_number(
            self.strength,
            name="strength",
        )
        max_correction = self._finite_number(
            self.max_correction,
            name="max_correction",
        )

        if not 0.0 <= strength <= 1.0:
            raise ValueError(
                "strength must be in the range 0.0..1.0"
            )

        if max_correction <= 0.0:
            raise ValueError(
                "max_correction must be greater than zero"
            )

        object.__setattr__(
            self,
            "strength",
            strength,
        )
        object.__setattr__(
            self,
            "max_correction",
            max_correction,
        )

    @staticmethod
    def _finite_number(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric"
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{name} must be finite"
            )

        return numeric


class AtlasArchitecturalReliefStructurePreserver:
    @staticmethod
    def _normalize_name(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        name = str(value).strip()

        if not name:
            raise ValueError(
                f"{field_name} must not be blank"
            )

        return name

    @staticmethod
    def _as_finite_map(
        values: Any,
        *,
        name: str,
    ) -> np.ndarray:
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
                f"{name} must be numeric"
            ) from exc

        if array.ndim != 2:
            raise ValueError(
                f"{name} must be two-dimensional"
            )

        if array.size == 0:
            raise ValueError(
                f"{name} must not be empty"
            )

        if not np.isfinite(array).all():
            raise ValueError(
                f"{name} must contain only finite values"
            )

        return array.copy()

    @staticmethod
    def _feature_weight(
        value: Any,
        *,
        feature_name: str,
    ) -> float:
        try:
            weight = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"feature weight for {feature_name} must be numeric"
            ) from exc

        if (
            not math.isfinite(weight)
            or not 0.0 <= weight <= 1.0
        ):
            raise ValueError(
                f"feature weight for {feature_name} "
                "must be in the range 0.0..1.0"
            )

        return weight

    @classmethod
    def build_protection_map(
        cls,
        *,
        feature_masks: Mapping[str, Any],
        feature_weights: Mapping[str, float],
    ) -> np.ndarray:
        if not isinstance(
            feature_masks,
            Mapping,
        ):
            raise TypeError(
                "feature_masks must be a mapping"
            )

        if not feature_masks:
            raise ValueError(
                "feature_masks must not be empty"
            )

        if not isinstance(
            feature_weights,
            Mapping,
        ):
            raise TypeError(
                "feature_weights must be a mapping"
            )

        normalized_masks = {}
        expected_shape = None

        for raw_name, raw_mask in feature_masks.items():
            feature_name = cls._normalize_name(
                raw_name,
                field_name="feature name",
            )

            if feature_name in normalized_masks:
                raise ValueError(
                    f"duplicate feature name: {feature_name}"
                )

            mask = cls._as_finite_map(
                raw_mask,
                name=f"feature mask {feature_name}",
            )

            if expected_shape is None:
                expected_shape = mask.shape
            elif mask.shape != expected_shape:
                raise ValueError(
                    "feature mask shapes must match"
                )

            normalized_masks[
                feature_name
            ] = np.clip(
                mask,
                0.0,
                1.0,
            )

        normalized_weights = {}

        for raw_name, raw_weight in feature_weights.items():
            feature_name = cls._normalize_name(
                raw_name,
                field_name="feature weight name",
            )

            if feature_name not in normalized_masks:
                raise ValueError(
                    f"unknown feature weight: {feature_name}"
                )

            if feature_name in normalized_weights:
                raise ValueError(
                    f"duplicate feature weight: {feature_name}"
                )

            normalized_weights[
                feature_name
            ] = cls._feature_weight(
                raw_weight,
                feature_name=feature_name,
            )

        protection_map = np.zeros(
            expected_shape,
            dtype=np.float64,
        )

        for feature_name, mask in normalized_masks.items():
            weighted_mask = (
                mask
                * normalized_weights.get(
                    feature_name,
                    1.0,
                )
            )

            protection_map = np.maximum(
                protection_map,
                weighted_mask,
            )

        return protection_map

    @classmethod
    def preserve(
        cls,
        *,
        depth_candidate: Any,
        structure_reference: Any,
        protection_map: Any,
        profile: AtlasArchitecturalReliefStructureProfile,
        clamp_output: bool = False,
    ) -> dict[str, Any]:
        candidate = cls._as_finite_map(
            depth_candidate,
            name="depth_candidate",
        )
        reference = cls._as_finite_map(
            structure_reference,
            name="structure_reference",
        )
        protection = cls._as_finite_map(
            protection_map,
            name="protection_map",
        )

        if not (
            candidate.shape
            == reference.shape
            == protection.shape
        ):
            raise ValueError(
                "depth, reference and protection map shapes must match"
            )

        if not isinstance(
            profile,
            AtlasArchitecturalReliefStructureProfile,
        ):
            raise TypeError(
                "profile must be an "
                "AtlasArchitecturalReliefStructureProfile"
            )

        if not isinstance(
            clamp_output,
            (
                bool,
                np.bool_,
            ),
        ):
            raise TypeError(
                "clamp_output must be boolean"
            )

        effective_protection = np.clip(
            protection,
            0.0,
            1.0,
        )

        raw_correction = (
            reference
            - candidate
        )

        bounded_correction = np.clip(
            raw_correction,
            -profile.max_correction,
            profile.max_correction,
        )

        applied_correction = (
            bounded_correction
            * profile.strength
            * effective_protection
        )

        preserved_depth = (
            candidate
            + applied_correction
        )

        if clamp_output:
            preserved_depth = np.clip(
                preserved_depth,
                0.0,
                1.0,
            )

            applied_correction = (
                preserved_depth
                - candidate
            )

        return {
            "type": (
                "architectural_relief_structure_preservation"
            ),
            "profile": profile,
            "protection_map": (
                effective_protection.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "raw_correction": (
                raw_correction.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "bounded_correction": (
                bounded_correction.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "applied_correction": (
                applied_correction.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "preserved_depth": (
                preserved_depth.astype(
                    np.float64,
                    copy=True,
                )
            ),
        }
