from __future__ import annotations

from dataclasses import dataclass


def _non_negative_integer(value, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")

    if value < 0:
        raise ValueError(f"{name} must be non-negative")

    return value


@dataclass(frozen=True)
class AtlasTriangleFileCountAnalysis:
    triangle_count: int
    maximum_triangle_count: int
    file_count: int
    maximum_file_count: int
    excess_triangle_count: int
    excess_file_count: int
    is_triangle_count_excessive: bool
    is_file_count_excessive: bool
    has_excessive_counts: bool


class AtlasTriangleFileCountAnalyzer:
    @classmethod
    def analyze(
        cls,
        *,
        triangle_count: int,
        maximum_triangle_count: int,
        file_count: int,
        maximum_file_count: int,
    ) -> AtlasTriangleFileCountAnalysis:
        triangles = _non_negative_integer(
            triangle_count,
            name="triangle_count",
        )
        maximum_triangles = _non_negative_integer(
            maximum_triangle_count,
            name="maximum_triangle_count",
        )
        files = _non_negative_integer(
            file_count,
            name="file_count",
        )
        maximum_files = _non_negative_integer(
            maximum_file_count,
            name="maximum_file_count",
        )

        excess_triangles = max(
            0,
            triangles - maximum_triangles,
        )
        excess_files = max(
            0,
            files - maximum_files,
        )

        triangle_excessive = excess_triangles > 0
        file_excessive = excess_files > 0

        return AtlasTriangleFileCountAnalysis(
            triangle_count=triangles,
            maximum_triangle_count=maximum_triangles,
            file_count=files,
            maximum_file_count=maximum_files,
            excess_triangle_count=excess_triangles,
            excess_file_count=excess_files,
            is_triangle_count_excessive=triangle_excessive,
            is_file_count_excessive=file_excessive,
            has_excessive_counts=(
                triangle_excessive
                or file_excessive
            ),
        )
