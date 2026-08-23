from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)
from CORE.atlas_canonical_head_residual_detail_displacement import (
    AtlasCanonicalHeadResidualDetailDisplacement,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailCompatibilityResult:
    compatible: bool
    status: str
    blocked_reasons: tuple[str, ...]
    connectivity_signature: str | None


class AtlasCanonicalHeadResidualDetailCompatibilityGate:
    @classmethod
    def evaluate(
        cls,
        *,
        identity_shape: AtlasCanonicalHeadIdentityShape,
        residual_detail_displacement: (
            AtlasCanonicalHeadResidualDetailDisplacement
        ),
    ) -> AtlasCanonicalHeadResidualDetailCompatibilityResult:
        if not isinstance(
            identity_shape,
            AtlasCanonicalHeadIdentityShape,
        ):
            raise TypeError(
                "identity_shape must be an "
                "AtlasCanonicalHeadIdentityShape."
            )

        if not isinstance(
            residual_detail_displacement,
            AtlasCanonicalHeadResidualDetailDisplacement,
        ):
            raise TypeError(
                "residual_detail_displacement must be an "
                "AtlasCanonicalHeadResidualDetailDisplacement."
            )

        identity_signature = (
            identity_shape.connectivity_signature
        )
        detail_signature = (
            residual_detail_displacement.connectivity_signature
        )

        if identity_signature != detail_signature:
            return (
                AtlasCanonicalHeadResidualDetailCompatibilityResult(
                    compatible=False,
                    status="BLOCKED",
                    blocked_reasons=(
                        "BLOCKED_IDENTITY_RESIDUAL_DETAIL_CONNECTIVITY_MISMATCH",
                    ),
                    connectivity_signature=None,
                )
            )

        return AtlasCanonicalHeadResidualDetailCompatibilityResult(
            compatible=True,
            status="ACCEPTED",
            blocked_reasons=(),
            connectivity_signature=identity_signature,
        )
