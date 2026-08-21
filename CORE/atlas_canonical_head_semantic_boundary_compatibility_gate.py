from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_semantic_boundary import (
    AtlasCanonicalHeadSemanticBoundary,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadSemanticBoundaryCompatibilityResult:
    compatible: bool
    status: str
    blocked_reasons: tuple[str, ...]
    missing_canonical_regions: tuple[str, ...]


class AtlasCanonicalHeadSemanticBoundaryCompatibilityGate:
    @classmethod
    def evaluate(
        cls,
        *,
        topology: AtlasCanonicalHeadTopology,
        boundary: AtlasCanonicalHeadSemanticBoundary,
    ) -> AtlasCanonicalHeadSemanticBoundaryCompatibilityResult:
        if not isinstance(
            topology,
            AtlasCanonicalHeadTopology,
        ):
            raise TypeError(
                "topology must be an "
                "AtlasCanonicalHeadTopology."
            )

        if not isinstance(
            boundary,
            AtlasCanonicalHeadSemanticBoundary,
        ):
            raise TypeError(
                "boundary must be an "
                "AtlasCanonicalHeadSemanticBoundary."
            )

        topology_regions = set(
            topology.semantic_vertex_regions
        )

        missing = tuple(
            region
            for region in boundary.canonical_head_regions
            if region not in topology_regions
        )

        if missing:
            return (
                AtlasCanonicalHeadSemanticBoundaryCompatibilityResult(
                    compatible=False,
                    status="BLOCKED",
                    blocked_reasons=(
                        "BLOCKED_MISSING_CANONICAL_HEAD_SEMANTIC_REGION",
                    ),
                    missing_canonical_regions=missing,
                )
            )

        return (
            AtlasCanonicalHeadSemanticBoundaryCompatibilityResult(
                compatible=True,
                status="ACCEPTED",
                blocked_reasons=(),
                missing_canonical_regions=(),
            )
        )
