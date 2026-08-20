from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadIdentityShapeCompatibilityResult:
    compatible: bool
    status: str
    blocked_reasons: tuple[str, ...]
    connectivity_signature: str | None
    identity_shape_count: int


class AtlasCanonicalHeadIdentityShapeCompatibilityGate:
    @classmethod
    def evaluate(
        cls,
        identity_shapes,
    ) -> AtlasCanonicalHeadIdentityShapeCompatibilityResult:
        try:
            shapes = tuple(
                identity_shapes
            )
        except TypeError as exc:
            raise TypeError(
                "identity_shapes must be an iterable of "
                "AtlasCanonicalHeadIdentityShape."
            ) from exc

        if not shapes:
            raise ValueError(
                "identity_shapes must not be empty."
            )

        for shape in shapes:
            if not isinstance(
                shape,
                AtlasCanonicalHeadIdentityShape,
            ):
                raise TypeError(
                    "identity_shapes must contain only "
                    "AtlasCanonicalHeadIdentityShape."
                )

        signatures = tuple(
            shape.connectivity_signature
            for shape in shapes
        )

        reference_signature = signatures[0]

        if any(
            signature != reference_signature
            for signature in signatures[1:]
        ):
            return (
                AtlasCanonicalHeadIdentityShapeCompatibilityResult(
                    compatible=False,
                    status="BLOCKED",
                    blocked_reasons=(
                        "BLOCKED_MIXED_CANONICAL_HEAD_CONNECTIVITY",
                    ),
                    connectivity_signature=None,
                    identity_shape_count=len(shapes),
                )
            )

        return (
            AtlasCanonicalHeadIdentityShapeCompatibilityResult(
                compatible=True,
                status="ACCEPTED",
                blocked_reasons=(),
                connectivity_signature=reference_signature,
                identity_shape_count=len(shapes),
            )
        )
