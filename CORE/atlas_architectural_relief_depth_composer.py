from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefDepthProfile:
    form_weight: float = 1.0
    detail_weight: float = 0.35
    micro_detail_weight: float = 0.10
    micro_detail_limit: float = 0.05

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "form_weight",
            self._nonnegative(
                self.form_weight,
                name="form_weight",
            ),
        )
        object.__setattr__(
            self,
            "detail_weight",
            self._nonnegative(
                self.detail_weight,
                name="detail_weight",
            ),
        )
        object.__setattr__(
            self,
            "micro_detail_weight",
            self._nonnegative(
                self.micro_detail_weight,
                name="micro_detail_weight",
            ),
        )
        object.__setattr__(
            self,
            "micro_detail_limit",
            self._positive(
                self.micro_detail_limit,
                name="micro_detail_limit",
            ),
        )

    @staticmethod
    def _finite(
        value,
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

    @classmethod
    def _nonnegative(
        cls,
        value,
        *,
        name: str,
    ) -> float:
        numeric = cls._finite(
            value,
            name=name,
        )

        if numeric < 0.0:
            raise ValueError(
                f"{name} must not be negative"
            )

        return numeric

    @classmethod
    def _positive(
        cls,
        value,
        *,
        name: str,
    ) -> float:
        numeric = cls._finite(
            value,
            name=name,
        )

        if numeric <= 0.0:
            raise ValueError(
                f"{name} must be greater than zero"
            )

        return numeric


class AtlasArchitecturalReliefDepthComposer:
    @staticmethod
    def _as_band(
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
                f"{name} contains non-finite values"
            )

        return array.copy()

    @staticmethod
    def _material_names(
        values: Sequence[str],
    ) -> tuple[str, ...]:
        try:
            names = tuple(
                str(value).strip()
                for value in values
            )
        except TypeError as exc:
            raise TypeError(
                "material_names must be iterable"
            ) from exc

        if not names:
            raise ValueError(
                "material_names must not be empty"
            )

        if any(
            not name
            for name in names
        ):
            raise ValueError(
                "material names must not be blank"
            )

        if len(set(names)) != len(names):
            raise ValueError(
                "material names must be unique"
            )

        return names

    @staticmethod
    def _material_map(
        values: Any,
        *,
        shape: tuple[int, int],
        material_count: int,
    ) -> np.ndarray:
        array = np.asarray(
            values
        )

        if array.ndim != 2:
            raise ValueError(
                "material_id_map must be two-dimensional"
            )

        if array.shape != shape:
            raise ValueError(
                "material_id_map shape must match relief bands"
            )

        if not (
            np.issubdtype(
                array.dtype,
                np.integer,
            )
            or np.issubdtype(
                array.dtype,
                np.bool_,
            )
        ):
            raise TypeError(
                "material_id_map must contain integer ids"
            )

        normalized = array.astype(
            np.int64,
            copy=True,
        )

        if np.any(normalized < 0):
            raise ValueError(
                "material_id_map must contain non-negative ids"
            )

        if int(normalized.max()) >= material_count:
            raise ValueError(
                "material_id_map contains ids outside material_names"
            )

        return normalized

    @staticmethod
    def _profiles(
        *,
        material_names: tuple[str, ...],
        default_profile: AtlasArchitecturalReliefDepthProfile,
        material_profiles: Mapping[
            str,
            AtlasArchitecturalReliefDepthProfile,
        ],
    ) -> Mapping[
        str,
        AtlasArchitecturalReliefDepthProfile,
    ]:
        if not isinstance(
            default_profile,
            AtlasArchitecturalReliefDepthProfile,
        ):
            raise TypeError(
                "default_profile must be an "
                "AtlasArchitecturalReliefDepthProfile"
            )

        if not isinstance(
            material_profiles,
            Mapping,
        ):
            raise TypeError(
                "material_profiles must be a mapping"
            )

        resolved = {
            name: default_profile
            for name in material_names
        }

        for raw_name, profile in (
            material_profiles.items()
        ):
            name = str(
                raw_name
            ).strip()

            if name not in resolved:
                raise ValueError(
                    f"unknown material profile: {name}"
                )

            if not isinstance(
                profile,
                AtlasArchitecturalReliefDepthProfile,
            ):
                raise TypeError(
                    "material profiles must be "
                    "AtlasArchitecturalReliefDepthProfile instances"
                )

            resolved[name] = profile

        return MappingProxyType(
            resolved
        )

    @classmethod
    def compose(
        cls,
        *,
        form: Any,
        detail: Any,
        micro_detail: Any,
        material_id_map: Any,
        material_names: Sequence[str],
        default_profile: AtlasArchitecturalReliefDepthProfile,
        material_profiles: Mapping[
            str,
            AtlasArchitecturalReliefDepthProfile,
        ],
    ) -> dict[str, Any]:
        form_array = cls._as_band(
            form,
            name="form",
        )
        detail_array = cls._as_band(
            detail,
            name="detail",
        )
        micro_array = cls._as_band(
            micro_detail,
            name="micro_detail",
        )

        if not (
            form_array.shape
            == detail_array.shape
            == micro_array.shape
        ):
            raise ValueError(
                "relief band shapes must match"
            )

        names = cls._material_names(
            material_names
        )
        ids = cls._material_map(
            material_id_map,
            shape=form_array.shape,
            material_count=len(names),
        )
        profiles = cls._profiles(
            material_names=names,
            default_profile=default_profile,
            material_profiles=material_profiles,
        )

        weighted_form = np.zeros_like(
            form_array
        )
        weighted_detail = np.zeros_like(
            detail_array
        )
        limited_micro_detail = np.zeros_like(
            micro_array
        )
        weighted_micro_detail = np.zeros_like(
            micro_array
        )

        for material_id, material_name in enumerate(
            names
        ):
            mask = ids == material_id
            profile = profiles[
                material_name
            ]

            weighted_form[mask] = (
                form_array[mask]
                * profile.form_weight
            )
            weighted_detail[mask] = (
                detail_array[mask]
                * profile.detail_weight
            )

            limited = np.clip(
                micro_array[mask],
                -profile.micro_detail_limit,
                profile.micro_detail_limit,
            )
            limited_micro_detail[mask] = (
                limited
            )
            weighted_micro_detail[mask] = (
                limited
                * profile.micro_detail_weight
            )

        depth_candidate = (
            weighted_form
            + weighted_detail
            + weighted_micro_detail
        )

        return {
            "type": (
                "architectural_relief_depth_composition"
            ),
            "material_names": names,
            "resolved_profiles": profiles,
            "weighted_form": weighted_form,
            "weighted_detail": weighted_detail,
            "limited_micro_detail": (
                limited_micro_detail
            ),
            "weighted_micro_detail": (
                weighted_micro_detail
            ),
            "depth_candidate": (
                depth_candidate
            ),
        }
