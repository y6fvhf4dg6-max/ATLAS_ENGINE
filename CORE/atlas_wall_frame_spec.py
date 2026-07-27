from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AtlasWallFrameSpec:
    outer_width_mm: float = 150.0
    outer_height_mm: float = 150.0
    frame_width_mm: float = 8.0

    inner_width_mm: float = field(init=False)
    inner_height_mm: float = field(init=False)

    def __post_init__(self) -> None:
        outer_width_mm = float(self.outer_width_mm)
        outer_height_mm = float(self.outer_height_mm)
        frame_width_mm = float(self.frame_width_mm)

        if outer_width_mm <= 0.0:
            raise ValueError("outer_width_mm must be positive")

        if outer_height_mm <= 0.0:
            raise ValueError("outer_height_mm must be positive")

        if frame_width_mm <= 0.0:
            raise ValueError("frame_width_mm must be positive")

        inner_width_mm = outer_width_mm - (2.0 * frame_width_mm)
        inner_height_mm = outer_height_mm - (2.0 * frame_width_mm)

        if inner_width_mm <= 0.0 or inner_height_mm <= 0.0:
            raise ValueError(
                "frame_width_mm must leave a positive inner opening"
            )

        object.__setattr__(self, "outer_width_mm", outer_width_mm)
        object.__setattr__(self, "outer_height_mm", outer_height_mm)
        object.__setattr__(self, "frame_width_mm", frame_width_mm)
        object.__setattr__(self, "inner_width_mm", inner_width_mm)
        object.__setattr__(self, "inner_height_mm", inner_height_mm)
