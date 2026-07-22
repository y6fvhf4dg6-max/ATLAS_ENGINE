from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameShadedPreviewResult:
    """
    Immutable FLAME shaded-preview result.

    The contract stores normalized float64 shading,
    uint8 grayscale preview pixels, the foreground
    coverage mask, and deterministic lighting settings.
    """

    shading: np.ndarray
    preview: np.ndarray
    coverage_mask: np.ndarray
    light_direction: tuple[float, float, float]
    ambient_strength: float
    diffuse_strength: float
    background_intensity: float

    _LIGHT_DIRECTION_TOLERANCE = 1.0e-12

    def __post_init__(
        self,
    ) -> None:
        shading = self._normalize_shading(
            self.shading,
        )
        preview = self._normalize_preview(
            self.preview,
        )
        coverage_mask = self._normalize_coverage_mask(
            self.coverage_mask,
        )

        if (
            shading.shape != preview.shape
            or shading.shape != coverage_mask.shape
        ):
            raise ValueError(
                "shading, preview, and coverage_mask "
                "must have identical shapes."
            )

        if (
            shading.shape[0] < 1
            or shading.shape[1] < 1
        ):
            raise ValueError(
                "preview arrays must not be empty."
            )

        light_direction = self._normalize_light_direction(
            self.light_direction,
        )
        ambient_strength = self._normalize_strength(
            self.ambient_strength,
            name="ambient_strength",
        )
        diffuse_strength = self._normalize_strength(
            self.diffuse_strength,
            name="diffuse_strength",
        )
        background_intensity = self._normalize_strength(
            self.background_intensity,
            name="background_intensity",
        )

        shading.setflags(
            write=False,
        )
        preview.setflags(
            write=False,
        )
        coverage_mask.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "shading",
            shading,
        )
        object.__setattr__(
            self,
            "preview",
            preview,
        )
        object.__setattr__(
            self,
            "coverage_mask",
            coverage_mask,
        )
        object.__setattr__(
            self,
            "light_direction",
            light_direction,
        )
        object.__setattr__(
            self,
            "ambient_strength",
            ambient_strength,
        )
        object.__setattr__(
            self,
            "diffuse_strength",
            diffuse_strength,
        )
        object.__setattr__(
            self,
            "background_intensity",
            background_intensity,
        )

    @property
    def shape(
        self,
    ) -> tuple[int, int]:
        return self.shading.shape

    @property
    def image_height(
        self,
    ) -> int:
        return int(
            self.shape[0]
        )

    @property
    def image_width(
        self,
    ) -> int:
        return int(
            self.shape[1]
        )

    @property
    def covered_pixel_count(
        self,
    ) -> int:
        return int(
            np.count_nonzero(
                self.coverage_mask,
            )
        )

    @property
    def background_pixel_count(
        self,
    ) -> int:
        return (
            self.image_width
            * self.image_height
            - self.covered_pixel_count
        )

    @property
    def minimum_intensity(
        self,
    ) -> float:
        return float(
            np.min(
                self.shading,
            )
        )

    @property
    def maximum_intensity(
        self,
    ) -> float:
        return float(
            np.max(
                self.shading,
            )
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "image_width": self.image_width,
            "image_height": self.image_height,
            "covered_pixel_count": (
                self.covered_pixel_count
            ),
            "background_pixel_count": (
                self.background_pixel_count
            ),
            "minimum_intensity": self.minimum_intensity,
            "maximum_intensity": self.maximum_intensity,
            "light_direction": list(
                self.light_direction,
            ),
            "ambient_strength": self.ambient_strength,
            "diffuse_strength": self.diffuse_strength,
            "background_intensity": (
                self.background_intensity
            ),
            "shading": self.shading.tolist(),
            "preview": self.preview.tolist(),
            "coverage_mask": self.coverage_mask.tolist(),
        }

    @staticmethod
    def _normalize_shading(
        value: Any,
    ) -> np.ndarray:
        try:
            shading = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "shading must be numeric."
            ) from exc

        if shading.ndim != 2:
            raise ValueError(
                "shading must be two-dimensional."
            )

        if not np.isfinite(
            shading,
        ).all():
            raise ValueError(
                "shading contains non-finite values."
            )

        if (
            np.any(
                shading < 0.0,
            )
            or np.any(
                shading > 1.0,
            )
        ):
            raise ValueError(
                "shading must be in the 0.0..1.0 range."
            )

        return shading.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_preview(
        value: Any,
    ) -> np.ndarray:
        try:
            preview_numeric = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "preview must be numeric."
            ) from exc

        if preview_numeric.ndim != 2:
            raise ValueError(
                "preview must be two-dimensional."
            )

        if not np.isfinite(
            preview_numeric,
        ).all():
            raise ValueError(
                "preview contains non-finite values."
            )

        if not np.equal(
            preview_numeric,
            np.rint(
                preview_numeric,
            ),
        ).all():
            raise ValueError(
                "preview must contain integer values."
            )

        if (
            np.any(
                preview_numeric < 0.0,
            )
            or np.any(
                preview_numeric > 255.0,
            )
        ):
            raise ValueError(
                "preview must be in the 0..255 range."
            )

        return preview_numeric.astype(
            np.uint8,
            copy=True,
        )

    @staticmethod
    def _normalize_coverage_mask(
        value: Any,
    ) -> np.ndarray:
        coverage_mask = np.asarray(
            value,
        )

        if coverage_mask.ndim != 2:
            raise ValueError(
                "coverage_mask must be two-dimensional."
            )

        return coverage_mask.astype(
            np.bool_,
            copy=True,
        )

    @classmethod
    def _normalize_light_direction(
        cls,
        value: Any,
    ) -> tuple[float, float, float]:
        try:
            components = tuple(
                float(
                    component,
                )
                for component in value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "light_direction must contain "
                "three numeric components."
            ) from exc

        if len(
            components,
        ) != 3:
            raise ValueError(
                "light_direction must contain "
                "three components."
            )

        if not all(
            math.isfinite(
                component,
            )
            for component in components
        ):
            raise ValueError(
                "light_direction must be finite."
            )

        magnitude = math.sqrt(
            sum(
                component
                * component
                for component in components
            )
        )

        if not math.isclose(
            magnitude,
            1.0,
            rel_tol=0.0,
            abs_tol=cls._LIGHT_DIRECTION_TOLERANCE,
        ):
            raise ValueError(
                "light_direction must be normalized."
            )

        return (
            components[0],
            components[1],
            components[2],
        )

    @staticmethod
    def _normalize_strength(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            strength = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            strength,
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if not (
            0.0
            <= strength
            <= 1.0
        ):
            raise ValueError(
                f"{name} must be in the "
                "0.0..1.0 range."
            )

        return strength
