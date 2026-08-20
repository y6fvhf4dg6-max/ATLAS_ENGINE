from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_expression_compatibility_gate import (
    AtlasCanonicalHeadExpressionCompatibilityGate,
)
from CORE.atlas_canonical_head_expression_displacement import (
    AtlasCanonicalHeadExpressionDisplacement,
)
from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadExpressionComposition:
    identity_shape: AtlasCanonicalHeadIdentityShape
    expression_displacement: AtlasCanonicalHeadExpressionDisplacement

    def __post_init__(self) -> None:
        if not isinstance(
            self.identity_shape,
            AtlasCanonicalHeadIdentityShape,
        ):
            raise TypeError(
                "identity_shape must be an "
                "AtlasCanonicalHeadIdentityShape."
            )

        if not isinstance(
            self.expression_displacement,
            AtlasCanonicalHeadExpressionDisplacement,
        ):
            raise TypeError(
                "expression_displacement must be an "
                "AtlasCanonicalHeadExpressionDisplacement."
            )

        compatibility = (
            AtlasCanonicalHeadExpressionCompatibilityGate.evaluate(
                identity_shape=self.identity_shape,
                expression_displacement=self.expression_displacement,
            )
        )

        if not compatibility.compatible:
            raise ValueError(
                compatibility.blocked_reasons[0]
            )

    @property
    def connectivity_signature(
        self,
    ) -> str:
        return self.identity_shape.connectivity_signature

    @property
    def resolved_geometry(
        self,
    ) -> AtlasCanonicalHeadGeometry:
        identity_geometry = self.identity_shape.resolved_geometry

        return AtlasCanonicalHeadGeometry(
            topology=identity_geometry.topology,
            vertices=(
                identity_geometry.vertices
                + self.expression_displacement.displacement
            ),
        )
