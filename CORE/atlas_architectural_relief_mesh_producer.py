from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_architectural_relief_physical_profile import (
    AtlasArchitecturalReliefPhysicalProfile,
)
from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)


class AtlasArchitecturalReliefMeshProducer:
    @classmethod
    def build(
        cls,
        *,
        height_map: Any,
        width_mm: float,
        depth_mm: float,
        physical_profile: (
            AtlasArchitecturalReliefPhysicalProfile
        ),
    ) -> dict[str, Any]:
        source = cls._validated_height_map(
            height_map
        )

        if not isinstance(
            physical_profile,
            AtlasArchitecturalReliefPhysicalProfile,
        ):
            raise TypeError(
                "physical_profile must be an "
                "AtlasArchitecturalReliefPhysicalProfile"
            )

        physical_plan = (
            physical_profile.resolve(
                width_mm=width_mm,
                depth_mm=depth_mm,
            )
        )

        sampling_plan = physical_plan[
            "sampling_plan"
        ]

        resampled = (
            AtlasHeightMapEngine
            .resample_bilinear(
                source,
                target_rows=(
                    sampling_plan.row_count
                ),
                target_columns=(
                    sampling_plan.column_count
                ),
            )
        )

        mesh = AtlasReliefMeshBuilder.build(
            resampled,
            **physical_plan["mesh_kwargs"],
        )

        topology_report = (
            AtlasMeshValidator
            ._topology_report(
                mesh
            )
        )

        triangle_count = len(
            mesh["triangles"]
        )

        expected_triangle_count = (
            physical_plan[
                "triangle_count"
            ]
        )

        if (
            triangle_count
            != expected_triangle_count
        ):
            raise ValueError(
                "Generated architectural relief mesh "
                "triangle count does not match "
                "the physical plan"
            )

        is_printable_topology = bool(
            topology_report[
                "open_edge_count"
            ] == 0
            and topology_report[
                "non_manifold_edge_count"
            ] == 0
        )

        return {
            "type": (
                "architectural_relief_mesh_production"
            ),
            "physical_profile": (
                physical_profile
            ),
            "physical_plan": (
                physical_plan
            ),
            "source_height_map": (
                source.copy()
            ),
            "resampled_height_map": (
                resampled.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "mesh": mesh,
            "triangle_count": (
                triangle_count
            ),
            "expected_triangle_count": (
                expected_triangle_count
            ),
            "topology_report": (
                topology_report
            ),
            "is_printable_topology": (
                is_printable_topology
            ),
        }

    @staticmethod
    def _validated_height_map(
        values: Any,
    ) -> np.ndarray:
        try:
            height_map = np.asarray(
                values,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "height_map must be numeric"
            ) from exc

        if height_map.ndim != 2:
            raise ValueError(
                "height_map must be two-dimensional"
            )

        if (
            height_map.shape[0] < 2
            or height_map.shape[1] < 2
        ):
            raise ValueError(
                "height_map must contain at least "
                "two rows and two columns"
            )

        if not np.isfinite(
            height_map
        ).all():
            raise ValueError(
                "height_map must contain only finite values"
            )

        tolerance = 1e-12

        if (
            float(height_map.min())
            < -tolerance
            or float(height_map.max())
            > 1.0 + tolerance
        ):
            raise ValueError(
                "height_map values must be normalized "
                "to the 0.0..1.0 range"
            )

        return np.clip(
            height_map,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=True,
        )
