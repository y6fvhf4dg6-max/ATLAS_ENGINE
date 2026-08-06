from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalysis,
)
from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailDecision,
)


def _normalize_identifier(
    value,
    *,
    field_name,
):
    normalized = "_".join(
        str(value).strip().lower().split()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class AtlasFacadeStructuralDetail:
    detail_index: int
    detail_kind: str
    u_center: float
    min_z: float
    max_z: float
    action: str
    resolved_size_mm: float
    scaled_size_mm: float
    minimum_printable_mm: float
    scale_factor: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.detail_index, bool)
            or not isinstance(self.detail_index, int)
            or self.detail_index < 0
        ):
            raise ValueError(
                "detail_index must be a non-negative integer"
            )

        detail_kind = _normalize_identifier(
            self.detail_kind,
            field_name="detail_kind",
        )
        action = _normalize_identifier(
            self.action,
            field_name="action",
        )

        if action not in {
            "preserve",
            "enlarge",
        }:
            raise ValueError(
                "placed structural detail action must be "
                "preserve or enlarge"
            )

        u_center = float(self.u_center)
        min_z = float(self.min_z)
        max_z = float(self.max_z)
        resolved_size_mm = float(
            self.resolved_size_mm
        )
        scaled_size_mm = float(
            self.scaled_size_mm
        )
        minimum_printable_mm = float(
            self.minimum_printable_mm
        )
        scale_factor = float(
            self.scale_factor
        )

        if (
            u_center < 0.0
            or u_center > 1.0
        ):
            raise ValueError(
                "u_center must be in the range [0, 1]"
            )

        if max_z <= min_z:
            raise ValueError(
                "max_z must be greater than min_z"
            )

        if resolved_size_mm <= 0.0:
            raise ValueError(
                "resolved_size_mm must be positive"
            )

        if scaled_size_mm <= 0.0:
            raise ValueError(
                "scaled_size_mm must be positive"
            )

        if minimum_printable_mm <= 0.0:
            raise ValueError(
                "minimum_printable_mm must be positive"
            )

        if scale_factor <= 0.0:
            raise ValueError(
                "scale_factor must be positive"
            )

        object.__setattr__(
            self,
            "detail_kind",
            detail_kind,
        )
        object.__setattr__(
            self,
            "action",
            action,
        )
        object.__setattr__(
            self,
            "u_center",
            u_center,
        )
        object.__setattr__(
            self,
            "min_z",
            min_z,
        )
        object.__setattr__(
            self,
            "max_z",
            max_z,
        )
        object.__setattr__(
            self,
            "resolved_size_mm",
            resolved_size_mm,
        )
        object.__setattr__(
            self,
            "scaled_size_mm",
            scaled_size_mm,
        )
        object.__setattr__(
            self,
            "minimum_printable_mm",
            minimum_printable_mm,
        )
        object.__setattr__(
            self,
            "scale_factor",
            scale_factor,
        )


@dataclass(frozen=True, slots=True)
class AtlasFacadeStructuralDetailAnalysis:
    detail_kind: str
    action: str
    details: tuple[
        AtlasFacadeStructuralDetail,
        ...,
    ]

    def __post_init__(self) -> None:
        detail_kind = _normalize_identifier(
            self.detail_kind,
            field_name="detail_kind",
        )
        action = _normalize_identifier(
            self.action,
            field_name="action",
        )
        details = tuple(
            self.details
        )

        if action not in {
            "preserve",
            "enlarge",
            "omit",
        }:
            raise ValueError(
                "action must be preserve, enlarge, or omit"
            )

        if any(
            not isinstance(
                detail,
                AtlasFacadeStructuralDetail,
            )
            for detail in details
        ):
            raise TypeError(
                "details must contain "
                "AtlasFacadeStructuralDetail instances"
            )

        if action == "omit" and details:
            raise ValueError(
                "omitted structural details must be empty"
            )

        if action != "omit" and not details:
            raise ValueError(
                "preserved structural details must not be empty"
            )

        if any(
            detail.detail_kind != detail_kind
            or detail.action != action
            for detail in details
        ):
            raise ValueError(
                "detail records must match analysis contract"
            )

        object.__setattr__(
            self,
            "detail_kind",
            detail_kind,
        )
        object.__setattr__(
            self,
            "action",
            action,
        )
        object.__setattr__(
            self,
            "details",
            details,
        )

    @property
    def detail_count(self):
        return len(
            self.details
        )


class AtlasFacadeStructuralDetailLayout:
    SUPPORTED_DETAIL_KINDS = {
        "column",
        "buttress",
    }

    @classmethod
    def create(
        cls,
        *,
        bay_analysis,
        detail_kind,
        physical_decision,
    ) -> AtlasFacadeStructuralDetailAnalysis:
        if not isinstance(
            bay_analysis,
            AtlasFacadeBayAnalysis,
        ):
            raise TypeError(
                "bay_analysis must be an "
                "AtlasFacadeBayAnalysis instance"
            )

        if not isinstance(
            physical_decision,
            AtlasPhysicalDetailDecision,
        ):
            raise TypeError(
                "physical_decision must be an "
                "AtlasPhysicalDetailDecision instance"
            )

        detail_kind = _normalize_identifier(
            detail_kind,
            field_name="detail_kind",
        )

        if detail_kind not in (
            cls.SUPPORTED_DETAIL_KINDS
        ):
            raise ValueError(
                "detail_kind must be column or buttress"
            )

        action = _normalize_identifier(
            physical_decision.action,
            field_name="action",
        )

        if action == "omit":
            return AtlasFacadeStructuralDetailAnalysis(
                detail_kind=detail_kind,
                action=action,
                details=(),
            )

        first_level_bays = (
            bay_analysis.bays_for_level(0)
        )

        if not first_level_bays:
            raise ValueError(
                "bay_analysis must contain first-level bays"
            )

        min_z = min(
            bay.min_z
            for bay in bay_analysis.bays
        )
        max_z = max(
            bay.max_z
            for bay in bay_analysis.bays
        )

        boundary_positions = [
            first_level_bays[0].u_min,
            *(
                bay.u_max
                for bay in first_level_bays
            ),
        ]

        details = tuple(
            AtlasFacadeStructuralDetail(
                detail_index=detail_index,
                detail_kind=detail_kind,
                u_center=u_center,
                min_z=min_z,
                max_z=max_z,
                action=action,
                resolved_size_mm=(
                    physical_decision.resolved_size_mm
                ),
                scaled_size_mm=(
                    physical_decision.scaled_size_mm
                ),
                minimum_printable_mm=(
                    physical_decision.minimum_printable_mm
                ),
                scale_factor=(
                    physical_decision.scale_factor
                ),
            )
            for detail_index, u_center
            in enumerate(
                boundary_positions
            )
        )

        return AtlasFacadeStructuralDetailAnalysis(
            detail_kind=detail_kind,
            action=action,
            details=details,
        )
