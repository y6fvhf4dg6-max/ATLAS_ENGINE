from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasLabelPlateSpec:
    width_mm: float = 118.0
    height_mm: float = 9.0
    depth_mm: float = 1.2
    corner_radius_mm: float = 2.0

    def __post_init__(self) -> None:
        width_mm = float(self.width_mm)
        height_mm = float(self.height_mm)
        depth_mm = float(self.depth_mm)
        corner_radius_mm = float(self.corner_radius_mm)

        if width_mm <= 0.0:
            raise ValueError("width_mm must be positive")

        if height_mm <= 0.0:
            raise ValueError("height_mm must be positive")

        if depth_mm <= 0.0:
            raise ValueError("depth_mm must be positive")

        if corner_radius_mm < 0.0:
            raise ValueError(
                "corner_radius_mm must not be negative"
            )

        maximum_corner_radius_mm = (
            min(width_mm, height_mm) / 2.0
        )

        if corner_radius_mm > maximum_corner_radius_mm:
            raise ValueError(
                "corner_radius_mm exceeds plate dimensions"
            )

        object.__setattr__(self, "width_mm", width_mm)
        object.__setattr__(self, "height_mm", height_mm)
        object.__setattr__(self, "depth_mm", depth_mm)
        object.__setattr__(
            self,
            "corner_radius_mm",
            corner_radius_mm,
        )
