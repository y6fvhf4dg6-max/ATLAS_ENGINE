from __future__ import annotations

from dataclasses import dataclass


def _non_negative_integer(value, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")

    if value < 0:
        raise ValueError(f"{name} must be non-negative")

    return value


@dataclass(frozen=True)
class AtlasColorChangeAnalysis:
    color_change_count: int
    maximum_color_changes: int
    excess_color_changes: int
    is_excessive: bool


class AtlasColorChangeAnalyzer:
    @classmethod
    def analyze(
        cls,
        *,
        color_change_count: int,
        maximum_color_changes: int,
    ) -> AtlasColorChangeAnalysis:
        count = _non_negative_integer(
            color_change_count,
            name="color_change_count",
        )
        maximum = _non_negative_integer(
            maximum_color_changes,
            name="maximum_color_changes",
        )

        excess = max(
            0,
            count - maximum,
        )

        return AtlasColorChangeAnalysis(
            color_change_count=count,
            maximum_color_changes=maximum,
            excess_color_changes=excess,
            is_excessive=excess > 0,
        )
