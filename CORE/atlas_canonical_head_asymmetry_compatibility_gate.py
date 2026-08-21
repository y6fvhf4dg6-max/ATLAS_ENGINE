from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_asymmetry_displacement import (
    AtlasCanonicalHeadAsymmetryDisplacement,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadAsymmetryCompatibilityResult:
    compatible: bool
    status: str
    blocked_reasons: tuple[str, ...]
    connectivity_signature: str | None


class AtlasCanonicalHeadAsymmetryCompatibilityGate:
    @classmethod
    def evaluate(
        cls,
        *,
        identity_shape: AtlasCanonicalHeadIdentityShape,
        asymmetry_displacement: AtlasCanonicalHeadAsymmetryDisplacement,
    ) -> AtlasCanonicalHeadAsymmetryCompatibilityResult:
        if not isinstance(
            identity_shape,
            AtlasCanonicalHeadIdentityShape,
        ):
            raise TypeError(
                "identity_shape must be an "
                "AtlasCanonicalHeadIdentityShape."
            )

        if not isinstance(
            asymmetry_displacement,
            AtlasCanonicalHeadAsymmetryDisplacement,
        ):
            raise TypeError(
                "asymmetry_displacement must be an "
                "AtlasCanonicalHeadAsymmetryDisplacement."
            )

        identity_signature = (
            identity_shape.connectivity_signature
        )
        asymmetry_signature = (
            asymmetry_displacement.connectivity_signature
        )

        if identity_signature != asymmetry_signature:
            return AtlasCanonicalHeadAsymmetryCompatibilityResult(
                compatible=False,
                status="BLOCKED",
                blocked_reasons=(
                    "BLOCKED_IDENTITY_ASYMMETRY_CONNECTIVITY_MISMATCH",
                ),
                connectivity_signature=None,
            )

        return AtlasCanonicalHeadAsymmetryCompatibilityResult(
            compatible=True,
            status="ACCEPTED",
            blocked_reasons=(),
            connectivity_signature=identity_signature,
        )
