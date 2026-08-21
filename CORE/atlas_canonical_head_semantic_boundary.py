from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadSemanticBoundary:
    canonical_head_regions: tuple[str, ...]
    separate_components: tuple[str, ...]
    optional_detail_layers: tuple[str, ...]

    @classmethod
    def production_v1(
        cls,
    ) -> "AtlasCanonicalHeadSemanticBoundary":
        return cls(
            canonical_head_regions=(
                "face",
                "left_ear",
                "right_ear",
                "jaw",
                "chin",
                "neck",
                "left_eye_region",
                "right_eye_region",
            ),
            separate_components=(
                "hair",
                "left_eyeball",
                "right_eyeball",
            ),
            optional_detail_layers=(
                "beard",
                "moustache",
            ),
        )

    def owner_of(
        self,
        semantic_name: object,
    ) -> str:
        normalized = self._normalize_semantic_name(
            semantic_name
        )

        if normalized in self.canonical_head_regions:
            return "canonical_head"

        if normalized in self.separate_components:
            return "separate_component"

        if normalized in self.optional_detail_layers:
            return "optional_detail_layer"

        raise KeyError(
            "semantic ownership is not defined for "
            f"{normalized!r}."
        )

    @staticmethod
    def _normalize_semantic_name(
        value: object,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise KeyError(
                "semantic ownership requires a non-blank name."
            )

        return normalized
