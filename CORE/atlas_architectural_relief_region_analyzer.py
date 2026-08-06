from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefRegionComponent:
    component_index: int
    pixel_count: int
    bounds: tuple[int, int, int, int]

    def __post_init__(self) -> None:
        if (
            isinstance(self.component_index, bool)
            or not isinstance(self.component_index, int)
            or self.component_index < 0
        ):
            raise ValueError(
                "component_index must be a non-negative integer"
            )

        if (
            isinstance(self.pixel_count, bool)
            or not isinstance(self.pixel_count, int)
            or self.pixel_count < 1
        ):
            raise ValueError(
                "pixel_count must be a positive integer"
            )

        try:
            min_row, min_column, max_row, max_column = (
                self.bounds
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "bounds must contain four integer values"
            ) from exc

        bounds = tuple(
            int(value)
            for value in (
                min_row,
                min_column,
                max_row,
                max_column,
            )
        )

        if (
            bounds[0] < 0
            or bounds[1] < 0
            or bounds[2] < bounds[0]
            or bounds[3] < bounds[1]
        ):
            raise ValueError(
                "bounds must define a valid inclusive region"
            )

        object.__setattr__(
            self,
            "bounds",
            bounds,
        )


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefRegion:
    material_id: int
    material_name: str
    pixel_count: int
    coverage_ratio: float
    bounds: tuple[int, int, int, int] | None
    components: tuple[
        AtlasArchitecturalReliefRegionComponent,
        ...,
    ]

    def __post_init__(self) -> None:
        if (
            isinstance(self.material_id, bool)
            or not isinstance(self.material_id, int)
            or self.material_id < 0
        ):
            raise ValueError(
                "material_id must be a non-negative integer"
            )

        material_name = str(
            self.material_name
        ).strip()

        if not material_name:
            raise ValueError(
                "material_name must not be blank"
            )

        if (
            isinstance(self.pixel_count, bool)
            or not isinstance(self.pixel_count, int)
            or self.pixel_count < 0
        ):
            raise ValueError(
                "pixel_count must be a non-negative integer"
            )

        coverage_ratio = float(
            self.coverage_ratio
        )

        if not 0.0 <= coverage_ratio <= 1.0:
            raise ValueError(
                "coverage_ratio must be in the range 0.0..1.0"
            )

        components = tuple(
            self.components
        )

        if any(
            not isinstance(
                component,
                AtlasArchitecturalReliefRegionComponent,
            )
            for component in components
        ):
            raise TypeError(
                "components must contain relief region components"
            )

        if self.pixel_count == 0:
            if self.bounds is not None:
                raise ValueError(
                    "empty regions must not define bounds"
                )

            if components:
                raise ValueError(
                    "empty regions must not define components"
                )
        else:
            if self.bounds is None:
                raise ValueError(
                    "non-empty regions must define bounds"
                )

            if not components:
                raise ValueError(
                    "non-empty regions must define components"
                )

            if sum(
                component.pixel_count
                for component in components
            ) != self.pixel_count:
                raise ValueError(
                    "component pixels must match region pixel_count"
                )

        object.__setattr__(
            self,
            "material_name",
            material_name,
        )
        object.__setattr__(
            self,
            "coverage_ratio",
            coverage_ratio,
        )
        object.__setattr__(
            self,
            "components",
            components,
        )

    @property
    def component_count(self) -> int:
        return len(
            self.components
        )


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefRegionAnalysis:
    shape: tuple[int, int]
    total_pixel_count: int
    regions: tuple[
        AtlasArchitecturalReliefRegion,
        ...,
    ]

    def __post_init__(self) -> None:
        try:
            rows, columns = self.shape
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "shape must contain exactly two dimensions"
            ) from exc

        shape = (
            int(rows),
            int(columns),
        )

        if shape[0] <= 0 or shape[1] <= 0:
            raise ValueError(
                "shape dimensions must be positive"
            )

        total_pixel_count = int(
            self.total_pixel_count
        )

        if total_pixel_count != (
            shape[0] * shape[1]
        ):
            raise ValueError(
                "total_pixel_count must match shape"
            )

        regions = tuple(
            self.regions
        )

        if any(
            not isinstance(
                region,
                AtlasArchitecturalReliefRegion,
            )
            for region in regions
        ):
            raise TypeError(
                "regions must contain architectural relief regions"
            )

        if tuple(
            region.material_id
            for region in regions
        ) != tuple(
            range(len(regions))
        ):
            raise ValueError(
                "region material ids must be ordered and contiguous"
            )

        if len(
            {
                region.material_name
                for region in regions
            }
        ) != len(regions):
            raise ValueError(
                "duplicate material names"
            )

        if sum(
            region.pixel_count
            for region in regions
        ) != total_pixel_count:
            raise ValueError(
                "region pixels must cover the complete material map"
            )

        object.__setattr__(
            self,
            "shape",
            shape,
        )
        object.__setattr__(
            self,
            "total_pixel_count",
            total_pixel_count,
        )
        object.__setattr__(
            self,
            "regions",
            regions,
        )

    @property
    def region_count(self) -> int:
        return len(
            self.regions
        )

    def region_for_material(
        self,
        material_name,
    ) -> AtlasArchitecturalReliefRegion:
        normalized_name = str(
            material_name
        ).strip()

        for region in self.regions:
            if (
                region.material_name
                == normalized_name
            ):
                return region

        raise KeyError(
            f"unknown material: {normalized_name}"
        )


class AtlasArchitecturalReliefRegionAnalyzer:
    _NEIGHBORS = (
        (-1, 0),
        (0, -1),
        (0, 1),
        (1, 0),
    )

    @staticmethod
    def _normalize_material_names(
        material_names,
    ) -> tuple[str, ...]:
        try:
            values = tuple(
                material_names
            )
        except TypeError as exc:
            raise TypeError(
                "material_names must be iterable"
            ) from exc

        if not values:
            raise ValueError(
                "material_names must not be empty"
            )

        normalized = tuple(
            str(value).strip()
            for value in values
        )

        if any(
            not value
            for value in normalized
        ):
            raise ValueError(
                "material names must not be blank"
            )

        if len(set(normalized)) != len(
            normalized
        ):
            raise ValueError(
                "material names must be unique"
            )

        return normalized

    @classmethod
    def _components_for_mask(
        cls,
        mask,
    ) -> tuple[
        AtlasArchitecturalReliefRegionComponent,
        ...,
    ]:
        rows, columns = mask.shape
        visited = np.zeros(
            mask.shape,
            dtype=bool,
        )
        components = []

        for start_row in range(rows):
            for start_column in range(
                columns
            ):
                if (
                    not mask[
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

                pixel_count = 0
                min_row = start_row
                max_row = start_row
                min_column = start_column
                max_column = start_column

                while queue:
                    row, column = (
                        queue.popleft()
                    )
                    pixel_count += 1

                    min_row = min(
                        min_row,
                        row,
                    )
                    max_row = max(
                        max_row,
                        row,
                    )
                    min_column = min(
                        min_column,
                        column,
                    )
                    max_column = max(
                        max_column,
                        column,
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
                            or neighbor_column
                            >= columns
                        ):
                            continue

                        if (
                            mask[
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
                    AtlasArchitecturalReliefRegionComponent(
                        component_index=len(
                            components
                        ),
                        pixel_count=(
                            pixel_count
                        ),
                        bounds=(
                            min_row,
                            min_column,
                            max_row,
                            max_column,
                        ),
                    )
                )

        return tuple(
            components
        )

    @classmethod
    def analyze(
        cls,
        *,
        material_id_map,
        material_names,
    ) -> AtlasArchitecturalReliefRegionAnalysis:
        material_map = np.asarray(
            material_id_map
        )

        if material_map.ndim != 2:
            raise ValueError(
                "material_id_map must be two-dimensional"
            )

        if material_map.size == 0:
            raise ValueError(
                "material_id_map must not be empty"
            )

        if not (
            np.issubdtype(
                material_map.dtype,
                np.integer,
            )
            or np.issubdtype(
                material_map.dtype,
                np.bool_,
            )
        ):
            raise TypeError(
                "material_id_map must contain integer ids"
            )

        material_map = material_map.astype(
            np.int64,
            copy=False,
        )

        if np.any(
            material_map < 0
        ):
            raise ValueError(
                "material_id_map must contain non-negative ids"
            )

        normalized_names = (
            cls._normalize_material_names(
                material_names
            )
        )

        if int(
            material_map.max()
        ) >= len(normalized_names):
            raise ValueError(
                "material_id_map contains ids outside material_names"
            )

        total_pixel_count = int(
            material_map.size
        )
        regions = []

        for material_id, material_name in enumerate(
            normalized_names
        ):
            mask = (
                material_map
                == material_id
            )
            coordinates = np.argwhere(
                mask
            )
            pixel_count = int(
                coordinates.shape[0]
            )

            if pixel_count == 0:
                bounds = None
                components = ()
            else:
                bounds = (
                    int(
                        coordinates[:, 0].min()
                    ),
                    int(
                        coordinates[:, 1].min()
                    ),
                    int(
                        coordinates[:, 0].max()
                    ),
                    int(
                        coordinates[:, 1].max()
                    ),
                )
                components = (
                    cls._components_for_mask(
                        mask
                    )
                )

            regions.append(
                AtlasArchitecturalReliefRegion(
                    material_id=material_id,
                    material_name=material_name,
                    pixel_count=pixel_count,
                    coverage_ratio=(
                        pixel_count
                        / total_pixel_count
                    ),
                    bounds=bounds,
                    components=components,
                )
            )

        return AtlasArchitecturalReliefRegionAnalysis(
            shape=tuple(
                int(value)
                for value in material_map.shape
            ),
            total_pixel_count=(
                total_pixel_count
            ),
            regions=tuple(regions),
        )
