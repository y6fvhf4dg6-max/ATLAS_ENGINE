from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)
from CORE.atlas_canonical_head_residual_detail_compatibility_gate import (
    AtlasCanonicalHeadResidualDetailCompatibilityGate,
)
from CORE.atlas_canonical_head_residual_detail_displacement import (
    AtlasCanonicalHeadResidualDetailDisplacement,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailComposition:
    identity_shape: AtlasCanonicalHeadIdentityShape
    residual_detail_displacement: (
        AtlasCanonicalHeadResidualDetailDisplacement
    )

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
            self.residual_detail_displacement,
            AtlasCanonicalHeadResidualDetailDisplacement,
        ):
            raise TypeError(
                "residual_detail_displacement must be an "
                "AtlasCanonicalHeadResidualDetailDisplacement."
            )

        compatibility = (
            AtlasCanonicalHeadResidualDetailCompatibilityGate.evaluate(
                identity_shape=self.identity_shape,
                residual_detail_displacement=(
                    self.residual_detail_displacement
                ),
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
                + self.residual_detail_displacement.displacement
            ),
        )
