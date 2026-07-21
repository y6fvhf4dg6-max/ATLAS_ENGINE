from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from CORE.atlas_portrait_reconstruction_evaluation import (
    AtlasPortraitReconstructionEvaluation,
)


@dataclass(frozen=True)
class AtlasPortraitReconstructionSelectionResult:
    """
    Immutable reconstruction candidate selection result.

    The result records the primary and backup reconstruction
    candidates, the deterministic eligible ranking, explicit
    rejection reasons, policy version, and metadata.

    It performs no model research, installation, inference,
    fitting, canonical conversion, projection, compression,
    rendering, or STL generation.
    """

    primary: AtlasPortraitReconstructionEvaluation
    backup: AtlasPortraitReconstructionEvaluation

    ranked_candidates: tuple[
        AtlasPortraitReconstructionEvaluation,
        ...,
    ]

    rejected_candidates: Mapping[str, str]

    policy_version: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(
            self.primary,
            AtlasPortraitReconstructionEvaluation,
        ):
            raise TypeError(
                "primary must be an "
                "AtlasPortraitReconstructionEvaluation."
            )

        if not isinstance(
            self.backup,
            AtlasPortraitReconstructionEvaluation,
        ):
            raise TypeError(
                "backup must be an "
                "AtlasPortraitReconstructionEvaluation."
            )

        if self.primary is self.backup:
            raise ValueError(
                "primary and backup must be different "
                "candidates."
            )

        ranked_candidates = tuple(
            self.ranked_candidates,
        )

        if len(
            ranked_candidates,
        ) < 2:
            raise ValueError(
                "ranked_candidates must contain at least "
                "two candidates."
            )

        if not all(
            isinstance(
                candidate,
                AtlasPortraitReconstructionEvaluation,
            )
            for candidate in ranked_candidates
        ):
            raise TypeError(
                "ranked_candidates must contain only "
                "AtlasPortraitReconstructionEvaluation "
                "instances."
            )

        if ranked_candidates[0] is not self.primary:
            raise ValueError(
                "primary must be the first ranked candidate."
            )

        if ranked_candidates[1] is not self.backup:
            raise ValueError(
                "backup must be the second ranked candidate."
            )

        if not isinstance(
            self.rejected_candidates,
            Mapping,
        ):
            raise TypeError(
                "rejected_candidates must be a mapping."
            )

        rejected_candidates = MappingProxyType(
            {
                str(
                    model_name,
                ): str(
                    reason,
                )
                for model_name, reason in sorted(
                    self.rejected_candidates.items(),
                    key=lambda item: str(
                        item[0],
                    ),
                )
            }
        )

        policy_version = self._normalize_required_text(
            self.policy_version,
            name="policy_version",
        )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        object.__setattr__(
            self,
            "ranked_candidates",
            ranked_candidates,
        )

        object.__setattr__(
            self,
            "rejected_candidates",
            rejected_candidates,
        )

        object.__setattr__(
            self,
            "policy_version",
            policy_version,
        )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "primary_model_name": (
                self.primary.model_name
            ),
            "primary_model_version": (
                self.primary.model_version
            ),
            "backup_model_name": (
                self.backup.model_name
            ),
            "backup_model_version": (
                self.backup.model_version
            ),
            "ranked_model_names": [
                candidate.model_name
                for candidate in self.ranked_candidates
            ],
            "ranked_candidates": [
                candidate.to_dict()
                for candidate in self.ranked_candidates
            ],
            "rejected_candidates": {
                model_name: self.rejected_candidates[
                    model_name
                ]
                for model_name in sorted(
                    self.rejected_candidates,
                )
            },
            "policy_version": self.policy_version,
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_required_text(
        value: Any,
        *,
        name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{name} must not be empty."
            )

        text = str(
            value,
        ).strip()

        if not text:
            raise ValueError(
                f"{name} must not be empty."
            )

        return text

    @staticmethod
    def _normalize_metadata(
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        copied = {
            str(
                key,
            ): item
            for key, item in value.items()
        }

        return MappingProxyType(
            {
                key: copied[key]
                for key in sorted(
                    copied,
                )
            }
        )


class AtlasPortraitReconstructionSelector:
    """
    Deterministically selects primary and backup portrait
    reconstruction candidates.

    Eligibility policy:
    - commercial use must be allowed
    - single-image input must be supported
    - surface normals must be supported
    - identity parameters must be supported
    - pose parameters must be supported
    - deterministic output must be supported
    - deterministic fixture generation must be supported

    Eligible ranking priority:
    - higher ATLAS adapter feasibility
    - lower maintenance risk
    - fixed topology
    - multi-view support
    - landmark-to-vertex mapping
    - more semantic regions
    - lower runtime
    - lower peak memory
    - deterministic model-name and version tie-break
    """

    DEFAULT_POLICY_VERSION = (
        "portrait-reconstruction-selection-v1"
    )

    _FEASIBILITY_RANK = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    _MAINTENANCE_RISK_RANK = {
        "low": 0,
        "medium": 1,
        "high": 2,
    }

    @classmethod
    def select(
        cls,
        candidates: Iterable[
            AtlasPortraitReconstructionEvaluation
        ],
        *,
        policy_version: str = DEFAULT_POLICY_VERSION,
        metadata: Mapping[str, Any] | None = None,
    ) -> AtlasPortraitReconstructionSelectionResult:
        if isinstance(
            candidates,
            (
                str,
                bytes,
            ),
        ):
            raise TypeError(
                "candidates must be an iterable of "
                "AtlasPortraitReconstructionEvaluation "
                "instances."
            )

        try:
            normalized_candidates = tuple(
                candidates,
            )
        except TypeError as exc:
            raise TypeError(
                "candidates must be an iterable of "
                "AtlasPortraitReconstructionEvaluation "
                "instances."
            ) from exc

        if len(
            normalized_candidates,
        ) < 2:
            raise ValueError(
                "candidates must contain at least two "
                "entries."
            )

        if not all(
            isinstance(
                candidate,
                AtlasPortraitReconstructionEvaluation,
            )
            for candidate in normalized_candidates
        ):
            raise TypeError(
                "candidates must contain only "
                "AtlasPortraitReconstructionEvaluation "
                "instances."
            )

        eligible_candidates: list[
            AtlasPortraitReconstructionEvaluation
        ] = []

        rejected_candidates: dict[str, str] = {}

        for candidate in normalized_candidates:
            rejection_reason = cls._rejection_reason(
                candidate,
            )

            if rejection_reason is None:
                eligible_candidates.append(
                    candidate,
                )
            else:
                rejected_candidates[
                    candidate.model_name
                ] = rejection_reason

        if len(
            eligible_candidates,
        ) < 2:
            raise ValueError(
                "Selection requires at least two eligible "
                "candidates."
            )

        ranked_candidates = tuple(
            sorted(
                eligible_candidates,
                key=cls._ranking_key,
            )
        )

        normalized_metadata: Mapping[str, Any]

        if metadata is None:
            normalized_metadata = {}
        else:
            normalized_metadata = metadata

        return AtlasPortraitReconstructionSelectionResult(
            primary=ranked_candidates[0],
            backup=ranked_candidates[1],
            ranked_candidates=ranked_candidates,
            rejected_candidates=rejected_candidates,
            policy_version=policy_version,
            metadata=normalized_metadata,
        )

    @classmethod
    def _rejection_reason(
        cls,
        candidate: AtlasPortraitReconstructionEvaluation,
    ) -> str | None:
        checks = (
            (
                candidate.commercial_use_allowed,
                "commercial_use_not_allowed",
            ),
            (
                candidate.supports_single_image,
                "single_image_not_supported",
            ),
            (
                candidate.supports_surface_normals,
                "surface_normals_not_supported",
            ),
            (
                candidate.supports_identity_parameters,
                "identity_parameters_not_supported",
            ),
            (
                candidate.supports_pose_parameters,
                "pose_parameters_not_supported",
            ),
            (
                candidate.deterministic_output,
                "deterministic_output_not_supported",
            ),
            (
                candidate.fixture_generation_supported,
                "fixture_generation_not_supported",
            ),
        )

        for passed, reason in checks:
            if not passed:
                return reason

        return None

    @classmethod
    def _ranking_key(
        cls,
        candidate: AtlasPortraitReconstructionEvaluation,
    ) -> tuple[Any, ...]:
        return (
            cls._FEASIBILITY_RANK[
                candidate.atlas_adapter_feasibility
            ],
            cls._MAINTENANCE_RISK_RANK[
                candidate.maintenance_risk
            ],
            0
            if candidate.topology_type == "fixed"
            else 1,
            0
            if candidate.supports_multi_view
            else 1,
            0
            if candidate.supports_landmark_vertex_map
            else 1,
            -len(
                candidate.semantic_regions,
            ),
            candidate.runtime_seconds,
            candidate.peak_memory_mb,
            candidate.model_name.casefold(),
            candidate.model_version.casefold(),
        )
