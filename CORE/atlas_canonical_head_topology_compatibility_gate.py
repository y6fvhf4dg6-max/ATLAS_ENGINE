from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadTopologyCompatibilityResult:
    compatible: bool
    status: str
    blocked_reasons: tuple[str, ...]
    missing_regions: tuple[str, ...]


class AtlasCanonicalHeadTopologyCompatibilityGate:
    REQUIRED_SEMANTIC_REGIONS = (
        "face",
        "nose",
        "left_eye",
        "right_eye",
    )

    @classmethod
    def evaluate(
        cls,
        topology: AtlasCanonicalHeadTopology,
    ) -> AtlasCanonicalHeadTopologyCompatibilityResult:
        if not isinstance(
            topology,
            AtlasCanonicalHeadTopology,
        ):
            raise TypeError(
                "topology must be an "
                "AtlasCanonicalHeadTopology."
            )

        available_regions = set(
            topology.semantic_vertex_regions
        )

        missing_regions = tuple(
            region
            for region in cls.REQUIRED_SEMANTIC_REGIONS
            if region not in available_regions
        )

        blocked_reasons = (
            (
                "BLOCKED_MISSING_CANONICAL_SEMANTIC_REGION",
            )
            if missing_regions
            else ()
        )

        compatible = not missing_regions

        return (
            AtlasCanonicalHeadTopologyCompatibilityResult(
                compatible=compatible,
                status=(
                    "ACCEPTED"
                    if compatible
                    else "BLOCKED"
                ),
                blocked_reasons=blocked_reasons,
                missing_regions=missing_regions,
            )
        )
