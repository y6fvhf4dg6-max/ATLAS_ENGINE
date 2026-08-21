from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_semantic_boundary import (
    AtlasCanonicalHeadSemanticBoundary,
)
from CORE.atlas_canonical_head_semantic_boundary_compatibility_gate import (
    AtlasCanonicalHeadSemanticBoundaryCompatibilityGate,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadSemanticRegionResolver:
    topology: AtlasCanonicalHeadTopology
    boundary: AtlasCanonicalHeadSemanticBoundary

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.topology,
            AtlasCanonicalHeadTopology,
        ):
            raise TypeError(
                "topology must be an "
                "AtlasCanonicalHeadTopology."
            )

        if not isinstance(
            self.boundary,
            AtlasCanonicalHeadSemanticBoundary,
        ):
            raise TypeError(
                "boundary must be an "
                "AtlasCanonicalHeadSemanticBoundary."
            )

        compatibility = (
            AtlasCanonicalHeadSemanticBoundaryCompatibilityGate.evaluate(
                topology=self.topology,
                boundary=self.boundary,
            )
        )

        if not compatibility.compatible:
            raise ValueError(
                compatibility.blocked_reasons[0]
            )

    def vertex_indices(
        self,
        semantic_name: object,
    ) -> tuple[int, ...]:
        normalized = self._normalize_semantic_name(
            semantic_name
        )

        owner = self.boundary.owner_of(
            normalized
        )

        if owner != "canonical_head":
            raise ValueError(
                f"{normalized!r} is owned by {owner}; "
                "it is not a canonical-head topology region."
            )

        return tuple(
            self.topology.semantic_vertex_regions[
                normalized
            ]
        )

    @staticmethod
    def _normalize_semantic_name(
        value: object,
    ) -> str:
        return "_".join(
            str(value).strip().lower().split()
        )
