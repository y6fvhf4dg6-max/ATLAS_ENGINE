from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_expression_displacement import (
    AtlasCanonicalHeadExpressionDisplacement,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadExpressionCompatibilityResult:
    compatible: bool
    status: str
    blocked_reasons: tuple[str, ...]
    connectivity_signature: str | None


class AtlasCanonicalHeadExpressionCompatibilityGate:
    @classmethod
    def evaluate(
        cls,
        *,
        identity_shape: AtlasCanonicalHeadIdentityShape,
        expression_displacement: AtlasCanonicalHeadExpressionDisplacement,
    ) -> AtlasCanonicalHeadExpressionCompatibilityResult:
        if not isinstance(
            identity_shape,
            AtlasCanonicalHeadIdentityShape,
        ):
            raise TypeError(
                "identity_shape must be an "
                "AtlasCanonicalHeadIdentityShape."
            )

        if not isinstance(
            expression_displacement,
            AtlasCanonicalHeadExpressionDisplacement,
        ):
            raise TypeError(
                "expression_displacement must be an "
                "AtlasCanonicalHeadExpressionDisplacement."
            )

        identity_signature = (
            identity_shape.connectivity_signature
        )
        expression_signature = (
            expression_displacement.connectivity_signature
        )

        if identity_signature != expression_signature:
            return AtlasCanonicalHeadExpressionCompatibilityResult(
                compatible=False,
                status="BLOCKED",
                blocked_reasons=(
                    "BLOCKED_IDENTITY_EXPRESSION_CONNECTIVITY_MISMATCH",
                ),
                connectivity_signature=None,
            )

        return AtlasCanonicalHeadExpressionCompatibilityResult(
            compatible=True,
            status="ACCEPTED",
            blocked_reasons=(),
            connectivity_signature=identity_signature,
        )
