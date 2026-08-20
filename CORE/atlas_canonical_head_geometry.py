from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadGeometry:
    topology: AtlasCanonicalHeadTopology
    vertices: np.ndarray

    def __post_init__(self) -> None:
        if not isinstance(
            self.topology,
            AtlasCanonicalHeadTopology,
        ):
            raise TypeError(
                "topology must be an "
                "AtlasCanonicalHeadTopology."
            )

        try:
            vertices = np.asarray(
                self.vertices,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "vertices must be numeric."
            ) from exc

        expected_shape = (
            self.topology.vertex_count,
            3,
        )

        if vertices.shape != expected_shape:
            raise ValueError(
                "vertices must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            vertices
        ).all():
            raise ValueError(
                "vertices must contain only finite values."
            )

        vertices = vertices.copy()
        vertices.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "vertices",
            vertices,
        )

    @property
    def vertex_count(self) -> int:
        return self.topology.vertex_count

    @property
    def face_count(self) -> int:
        return len(
            self.topology.faces
        )

    @property
    def connectivity_signature(
        self,
    ) -> str:
        return (
            self.topology.connectivity_signature
        )

    def semantic_region_vertices(
        self,
        region_name: str,
    ) -> np.ndarray:
        normalized_name = "_".join(
            str(region_name)
            .strip()
            .lower()
            .split()
        )

        indices = (
            self.topology
            .semantic_vertex_regions[
                normalized_name
            ]
        )

        points = self.vertices[
            np.asarray(
                indices,
                dtype=np.int64,
            )
        ].copy()

        points.setflags(
            write=False
        )

        return points
