from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefDetailScaleProfile:
    minimum_feature_mm: float = 0.8
    activity_threshold: float = 0.02
    minimum_density: float = 0.25

    def __post_init__(self) -> None:
        minimum_feature_mm = self._finite(
            self.minimum_feature_mm,
            name="minimum_feature_mm",
        )
        activity_threshold = self._finite(
            self.activity_threshold,
            name="activity_threshold",
        )
        minimum_density = self._finite(
            self.minimum_density,
            name="minimum_density",
        )

        if minimum_feature_mm <= 0.0:
            raise ValueError(
                "minimum_feature_mm must be greater than zero"
            )

        if activity_threshold < 0.0:
            raise ValueError(
                "activity_threshold must not be negative"
            )

        if not 0.0 < minimum_density <= 1.0:
            raise ValueError(
                "minimum_density must be in the range 0.0..1.0"
            )

        object.__setattr__(
            self,
            "minimum_feature_mm",
            minimum_feature_mm,
        )
        object.__setattr__(
            self,
            "activity_threshold",
            activity_threshold,
        )
        object.__setattr__(
            self,
            "minimum_density",
            minimum_density,
        )

    @staticmethod
    def _finite(
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


class AtlasArchitecturalReliefDetailScaleFilter:
    _NEIGHBORS = (
        (-1, 0),
        (0, -1),
        (0, 1),
        (1, 0),
    )

    @staticmethod
    def _positive_dimension(
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

        if (
            not math.isfinite(numeric)
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be greater than zero"
            )

        return numeric

    @staticmethod
    def _detail_array(
        values: Any,
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
                "detail_map must be numeric"
            ) from exc

        if array.ndim != 2:
            raise ValueError(
                "detail_map must be two-dimensional"
            )

        if array.size == 0:
            raise ValueError(
                "detail_map must not be empty"
            )

        if not np.isfinite(array).all():
            raise ValueError(
                "detail_map must contain only finite values"
            )

        return array.copy()

    @classmethod
    def _connected_components(
        cls,
        active_mask: np.ndarray,
    ) -> tuple[tuple[tuple[int, int], ...], ...]:
        rows, columns = active_mask.shape
        visited = np.zeros(
            active_mask.shape,
            dtype=bool,
        )
        components = []

        for start_row in range(rows):
            for start_column in range(columns):
                if (
                    not active_mask[
                        start_row,
                        start_column,
                    ]
                    or visited[
                        start_row,
                        start_column,
                    ]
                ):
                    continue

                queue = deque(
                    (
                        (
                            start_row,
                            start_column,
                        ),
                    )
                )
                visited[
                    start_row,
                    start_column,
                ] = True
                coordinates = []

                while queue:
                    row, column = queue.popleft()
                    coordinates.append(
                        (
                            row,
                            column,
                        )
                    )

                    for (
                        row_offset,
                        column_offset,
                    ) in cls._NEIGHBORS:
                        neighbor_row = (
                            row + row_offset
                        )
                        neighbor_column = (
                            column
                            + column_offset
                        )

                        if (
                            neighbor_row < 0
                            or neighbor_row >= rows
                            or neighbor_column < 0
                            or neighbor_column >= columns
                        ):
                            continue

                        if (
                            active_mask[
                                neighbor_row,
                                neighbor_column,
                            ]
                            and not visited[
                                neighbor_row,
                                neighbor_column,
                            ]
                        ):
                            visited[
                                neighbor_row,
                                neighbor_column,
                            ] = True
                            queue.append(
                                (
                                    neighbor_row,
                                    neighbor_column,
                                )
                            )

                components.append(
                    tuple(coordinates)
                )

        return tuple(components)

    @classmethod
    def filter(
        cls,
        *,
        detail_map: Any,
        width_mm: float,
        depth_mm: float,
        profile: AtlasArchitecturalReliefDetailScaleProfile,
    ) -> dict[str, Any]:
        detail = cls._detail_array(
            detail_map
        )
        physical_width = cls._positive_dimension(
            width_mm,
            name="width_mm",
        )
        physical_depth = cls._positive_dimension(
            depth_mm,
            name="depth_mm",
        )

        if not isinstance(
            profile,
            AtlasArchitecturalReliefDetailScaleProfile,
        ):
            raise TypeError(
                "profile must be an "
                "AtlasArchitecturalReliefDetailScaleProfile"
            )

        rows, columns = detail.shape
        pixel_pitch_x_mm = (
            physical_width / columns
        )
        pixel_pitch_y_mm = (
            physical_depth / rows
        )

        active_mask = (
            np.abs(detail)
            >= profile.activity_threshold
        )

        components = cls._connected_components(
            active_mask
        )

        retention_map = np.zeros(
            detail.shape,
            dtype=np.float64,
        )
        component_reports = []
        retained_component_count = 0
        culled_component_count = 0

        for component_index, coordinates in enumerate(
            components
        ):
            component_rows = [
                row
                for row, _ in coordinates
            ]
            component_columns = [
                column
                for _, column in coordinates
            ]

            min_row = min(component_rows)
            max_row = max(component_rows)
            min_column = min(component_columns)
            max_column = max(component_columns)

            bounding_rows = (
                max_row - min_row + 1
            )
            bounding_columns = (
                max_column - min_column + 1
            )
            bounding_pixel_count = (
                bounding_rows
                * bounding_columns
            )
            pixel_count = len(coordinates)

            density_ratio = (
                pixel_count
                / bounding_pixel_count
            )
            physical_width_mm = (
                bounding_columns
                * pixel_pitch_x_mm
            )
            physical_height_mm = (
                bounding_rows
                * pixel_pitch_y_mm
            )
            maximum_span_mm = max(
                physical_width_mm,
                physical_height_mm,
            )

            retained = bool(
                maximum_span_mm
                >= profile.minimum_feature_mm
                and density_ratio
                >= profile.minimum_density
            )

            if retained:
                retained_component_count += 1

                for row, column in coordinates:
                    retention_map[
                        row,
                        column,
                    ] = 1.0
            else:
                culled_component_count += 1

            component_reports.append(
                {
                    "component_index": (
                        component_index
                    ),
                    "pixel_count": pixel_count,
                    "bounds": (
                        min_row,
                        min_column,
                        max_row,
                        max_column,
                    ),
                    "bounding_pixel_count": (
                        bounding_pixel_count
                    ),
                    "density_ratio": (
                        float(density_ratio)
                    ),
                    "physical_width_mm": (
                        float(physical_width_mm)
                    ),
                    "physical_height_mm": (
                        float(physical_height_mm)
                    ),
                    "maximum_span_mm": (
                        float(maximum_span_mm)
                    ),
                    "retained": retained,
                }
            )

        filtered_detail = (
            detail
            * retention_map
        )

        return {
            "type": (
                "architectural_relief_detail_scale_filter"
            ),
            "shape": (
                rows,
                columns,
            ),
            "width_mm": physical_width,
            "depth_mm": physical_depth,
            "pixel_pitch_x_mm": (
                float(pixel_pitch_x_mm)
            ),
            "pixel_pitch_y_mm": (
                float(pixel_pitch_y_mm)
            ),
            "profile": profile,
            "active_mask": (
                active_mask.astype(
                    bool,
                    copy=True,
                )
            ),
            "retention_map": retention_map,
            "filtered_detail": (
                filtered_detail.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "component_reports": tuple(
                component_reports
            ),
            "component_count": len(
                components
            ),
            "retained_component_count": (
                retained_component_count
            ),
            "culled_component_count": (
                culled_component_count
            ),
        }
