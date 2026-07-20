from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasParametricFaceShadedPreviewResult:
    """
    Immutable parametric face shaded-preview result.

    The contract stores:
    - normalized float64 shading intensities
    - aligned uint8 grayscale preview values
    - normalized light direction
    - ambient and diffuse render strengths

    It performs no surface deformation, normal
    calculation, lighting, image writing, projection,
    triangulation, or mesh generation.
    """

    shading: np.ndarray
    preview: np.ndarray
    light_direction: tuple[float, float, float]
    ambient_strength: float
    diffuse_strength: float

    LIGHT_DIRECTION_TOLERANCE = 1e-12

    def __post_init__(self) -> None:
        shading = self._normalize_shading(
            self.shading,
        )

        preview = self._normalize_preview(
            self.preview,
        )

        if shading.shape != preview.shape:
            raise ValueError(
                "shading and preview must have "
                "identical shapes."
            )

        row_count, column_count = shading.shape

        if row_count < 2 or column_count < 2:
            raise ValueError(
                "shading and preview must contain at "
                "least two rows and two columns."
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

        shading.setflags(
            write=False,
        )
        preview.setflags(
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

    @property
    def shape(
        self,
    ) -> tuple[int, int]:
        return self.shading.shape

    @property
    def row_count(
        self,
    ) -> int:
        return int(
            self.shape[0],
        )

    @property
    def column_count(
        self,
    ) -> int:
        return int(
            self.shape[1],
        )

    @property
    def minimum_intensity(
        self,
    ) -> float:
        return float(
            self.shading.min(),
        )

    @property
    def maximum_intensity(
        self,
    ) -> float:
        return float(
            self.shading.max(),
        )

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

    @classmethod
    def _normalize_light_direction(
        cls,
        value: Any,
    ) -> tuple[float, float, float]:
        try:
            components = tuple(
                float(component)
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

        if len(components) != 3:
            raise ValueError(
                "light_direction must contain "
                "three components."
            )

        if not all(
            math.isfinite(component)
            for component in components
        ):
            raise ValueError(
                "light_direction must be finite."
            )

        magnitude = math.sqrt(
            sum(
                component * component
                for component in components
            )
        )

        if not math.isclose(
            magnitude,
            1.0,
            rel_tol=0.0,
            abs_tol=cls.LIGHT_DIRECTION_TOLERANCE,
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
