from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasLabelTextSpec:
    primary_text: str
    secondary_text: str = ""

    primary_height_mm: float = 4.2
    secondary_height_mm: float = 2.8
    depth_mm: float = 0.6
    max_width_mm: float = 108.0
    graduation_cap: bool = False
    birthday_cake: bool = False
    home: bool = False

    def __post_init__(self) -> None:
        primary_text = str(self.primary_text).strip()
        secondary_text = str(self.secondary_text).strip()

        primary_height_mm = float(self.primary_height_mm)
        secondary_height_mm = float(self.secondary_height_mm)
        depth_mm = float(self.depth_mm)
        max_width_mm = float(self.max_width_mm)
        graduation_cap = bool(self.graduation_cap)
        birthday_cake = bool(self.birthday_cake)
        home = bool(self.home)

        if not primary_text:
            raise ValueError("primary_text must not be empty")

        if primary_height_mm <= 0.0:
            raise ValueError("primary_height_mm must be positive")

        if secondary_height_mm <= 0.0:
            raise ValueError("secondary_height_mm must be positive")

        if depth_mm <= 0.0:
            raise ValueError("depth_mm must be positive")

        if max_width_mm <= 0.0:
            raise ValueError("max_width_mm must be positive")

        object.__setattr__(self, "primary_text", primary_text)
        object.__setattr__(self, "secondary_text", secondary_text)
        object.__setattr__(
            self,
            "primary_height_mm",
            primary_height_mm,
        )
        object.__setattr__(
            self,
            "secondary_height_mm",
            secondary_height_mm,
        )
        object.__setattr__(self, "depth_mm", depth_mm)
        object.__setattr__(self, "max_width_mm", max_width_mm)
        object.__setattr__(
            self,
            "graduation_cap",
            graduation_cap,
        )
        object.__setattr__(
            self,
            "birthday_cake",
            birthday_cake,
        )
        object.__setattr__(
            self,
            "home",
            home,
        )
