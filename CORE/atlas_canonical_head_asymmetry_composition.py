from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_asymmetry_compatibility_gate import (
    AtlasCanonicalHeadAsymmetryCompatibilityGate,
)
from CORE.atlas_canonical_head_asymmetry_displacement import (
    AtlasCanonicalHeadAsymmetryDisplacement,
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
class AtlasCanonicalHeadAsymmetryComposition:
    identity_shape: AtlasCanonicalHeadIdentityShape
    asymmetry_displacement: AtlasCanonicalHeadAsymmetryDisplacement

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
            self.asymmetry_displacement,
            AtlasCanonicalHeadAsymmetryDisplacement,
        ):
            raise TypeError(
                "asymmetry_displacement must be an "
                "AtlasCanonicalHeadAsymmetryDisplacement."
            )

        compatibility = (
            AtlasCanonicalHeadAsymmetryCompatibilityGate.evaluate(
                identity_shape=self.identity_shape,
                asymmetry_displacement=self.asymmetry_displacement,
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
                + self.asymmetry_displacement.displacement
            ),
        )
