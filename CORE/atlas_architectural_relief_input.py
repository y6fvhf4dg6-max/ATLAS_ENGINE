from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefSemanticMaskSpec:
    expected_shape: tuple[int, int]
    default_material: str
    mask_paths: Mapping[str, object]
    threshold: int = 128

    def __post_init__(self) -> None:
        try:
            rows, columns = self.expected_shape
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "expected_shape must contain exactly two dimensions"
            ) from exc

        if (
            isinstance(rows, bool)
            or isinstance(columns, bool)
        ):
            raise ValueError(
                "expected_shape dimensions must be positive integers"
            )

        try:
            rows = int(rows)
            columns = int(columns)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "expected_shape dimensions must be positive integers"
            ) from exc

        if rows <= 0 or columns <= 0:
            raise ValueError(
                "expected_shape dimensions must be positive"
            )

        default_material = "_".join(
            str(self.default_material)
            .strip()
            .lower()
            .split()
        )

        if not default_material:
            raise ValueError(
                "default_material must not be blank"
            )

        if not isinstance(
            self.mask_paths,
            Mapping,
        ):
            raise TypeError(
                "mask_paths must be a mapping"
            )

        if not self.mask_paths:
            raise ValueError(
                "mask_paths must not be empty"
            )

        normalized_paths = {}

        for material_name, path_value in (
            self.mask_paths.items()
        ):
            normalized_name = "_".join(
                str(material_name)
                .strip()
                .lower()
                .split()
            )

            if not normalized_name:
                raise ValueError(
                    "mask material names must not be blank"
                )

            if normalized_name in normalized_paths:
                raise ValueError(
                    "duplicate semantic mask material name"
                )

            if not isinstance(
                path_value,
                (
                    str,
                    Path,
                ),
            ):
                raise TypeError(
                    "semantic mask paths must be strings or pathlib.Path"
                )

            if (
                isinstance(path_value, str)
                and not path_value.strip()
            ):
                raise ValueError(
                    "semantic mask paths must not be blank"
                )

            normalized_paths[
                normalized_name
            ] = Path(path_value)

        if isinstance(self.threshold, bool):
            raise ValueError(
                "threshold must be an integer between 0 and 255"
            )

        try:
            threshold = int(
                self.threshold
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "threshold must be an integer between 0 and 255"
            ) from exc

        if threshold < 0 or threshold > 255:
            raise ValueError(
                "threshold must be between 0 and 255"
            )

        object.__setattr__(
            self,
            "expected_shape",
            (
                rows,
                columns,
            ),
        )
        object.__setattr__(
            self,
            "default_material",
            default_material,
        )
        object.__setattr__(
            self,
            "mask_paths",
            normalized_paths,
        )
        object.__setattr__(
            self,
            "threshold",
            threshold,
        )

    def to_load_kwargs(self) -> dict[str, Any]:
        return {
            "mask_paths": dict(
                self.mask_paths
            ),
            "expected_shape": (
                self.expected_shape
            ),
            "default_material": (
                self.default_material
            ),
            "threshold": self.threshold,
        }


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefInput:
    image_path: Path
    width_mm: float
    depth_mm: float
    architectural_kind: str
    product_profile: AtlasReliefProductProfile
    preprocessors: tuple[Any, ...] = ()
    semantic_masks: (
        AtlasArchitecturalReliefSemanticMaskSpec
        | None
    ) = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.image_path,
            (
                str,
                Path,
            ),
        ):
            raise TypeError(
                "image_path must be a string or pathlib.Path"
            )

        if (
            isinstance(self.image_path, str)
            and not self.image_path.strip()
        ):
            raise ValueError(
                "image_path must not be blank"
            )

        image_path = Path(
            self.image_path
        )

        width_mm = self._positive_finite(
            self.width_mm,
            name="width_mm",
        )
        depth_mm = self._positive_finite(
            self.depth_mm,
            name="depth_mm",
        )

        architectural_kind = "_".join(
            str(self.architectural_kind)
            .strip()
            .lower()
            .split()
        )

        if not architectural_kind:
            raise ValueError(
                "architectural_kind must not be blank"
            )

        if not isinstance(
            self.product_profile,
            AtlasReliefProductProfile,
        ):
            raise TypeError(
                "product_profile must be an "
                "AtlasReliefProductProfile instance"
            )

        if isinstance(
            self.preprocessors,
            (
                str,
                bytes,
            ),
        ):
            raise TypeError(
                "preprocessors must be an iterable of preprocessors"
            )

        try:
            preprocessors = tuple(
                self.preprocessors
            )
        except TypeError as exc:
            raise TypeError(
                "preprocessors must be iterable"
            ) from exc

        if (
            self.semantic_masks is not None
            and not isinstance(
                self.semantic_masks,
                AtlasArchitecturalReliefSemanticMaskSpec,
            )
        ):
            raise TypeError(
                "semantic_masks must be an "
                "AtlasArchitecturalReliefSemanticMaskSpec or None"
            )

        object.__setattr__(
            self,
            "image_path",
            image_path,
        )
        object.__setattr__(
            self,
            "width_mm",
            width_mm,
        )
        object.__setattr__(
            self,
            "depth_mm",
            depth_mm,
        )
        object.__setattr__(
            self,
            "architectural_kind",
            architectural_kind,
        )
        object.__setattr__(
            self,
            "preprocessors",
            preprocessors,
        )

    @staticmethod
    def _positive_finite(
        value,
        *,
        name,
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

        if (
            not math.isfinite(numeric)
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be greater than zero"
            )

        return numeric

    def to_pipeline_request(
        self,
    ) -> dict[str, Any]:
        semantic_mask_kwargs = None

        if self.semantic_masks is not None:
            semantic_mask_kwargs = (
                self.semantic_masks
                .to_load_kwargs()
            )

        return {
            "image_path": self.image_path,
            "pipeline_kwargs": {
                "width_mm": self.width_mm,
                "depth_mm": self.depth_mm,
                "product_profile": (
                    self.product_profile
                ),
                "preprocessors": (
                    self.preprocessors
                ),
            },
            "semantic_mask_kwargs": (
                semantic_mask_kwargs
            ),
            "architectural_kind": (
                self.architectural_kind
            ),
        }
