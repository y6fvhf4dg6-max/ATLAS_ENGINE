from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailResolver,
)


@dataclass(frozen=True, slots=True)
class AtlasFacadeOrnamentCandidate:
    source_index: int
    ornament_kind: str
    priority: float
    real_size_m: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.source_index, bool)
            or not isinstance(self.source_index, int)
            or self.source_index < 0
        ):
            raise ValueError(
                "source_index must be a non-negative integer"
            )

        ornament_kind = "_".join(
            str(self.ornament_kind)
            .strip()
            .lower()
            .split()
        )

        if not ornament_kind:
            raise ValueError(
                "ornament_kind must not be blank"
            )

        priority = float(self.priority)
        real_size_m = float(self.real_size_m)

        if real_size_m <= 0.0:
            raise ValueError(
                "real_size_m must be positive"
            )

        object.__setattr__(
            self,
            "ornament_kind",
            ornament_kind,
        )
        object.__setattr__(
            self,
            "priority",
            priority,
        )
        object.__setattr__(
            self,
            "real_size_m",
            real_size_m,
        )


@dataclass(frozen=True, slots=True)
class AtlasFacadeResolvedOrnament:
    source_index: int
    ornament_kind: str
    priority: float
    action: str
    scaled_size_mm: float
    minimum_printable_mm: float
    resolved_size_mm: float
    scale_factor: float
    selection_status: str

    def __post_init__(self) -> None:
        action = str(self.action).strip().lower()
        selection_status = (
            str(self.selection_status)
            .strip()
            .lower()
        )

        if action not in {
            "preserve",
            "enlarge",
            "omit",
        }:
            raise ValueError(
                "action must be preserve, enlarge, or omit"
            )

        if selection_status not in {
            "selected",
            "physical_omit",
            "density_omit",
        }:
            raise ValueError(
                "invalid selection_status"
            )

        object.__setattr__(
            self,
            "action",
            action,
        )
        object.__setattr__(
            self,
            "selection_status",
            selection_status,
        )


@dataclass(frozen=True, slots=True)
class AtlasFacadeOrnamentDensityAnalysis:
    density_level: str
    selected: tuple[
        AtlasFacadeResolvedOrnament,
        ...,
    ]
    omitted: tuple[
        AtlasFacadeResolvedOrnament,
        ...,
    ]
    candidate_count: int
    printable_count: int
    detail_budget: int

    def __post_init__(self) -> None:
        density_level = (
            str(self.density_level)
            .strip()
            .lower()
        )

        if density_level not in {
            "low",
            "medium",
            "high",
        }:
            raise ValueError(
                "density_level must be low, medium, or high"
            )

        selected = tuple(self.selected)
        omitted = tuple(self.omitted)

        if any(
            not isinstance(
                item,
                AtlasFacadeResolvedOrnament,
            )
            for item in selected + omitted
        ):
            raise TypeError(
                "selected and omitted must contain "
                "AtlasFacadeResolvedOrnament instances"
            )

        object.__setattr__(
            self,
            "density_level",
            density_level,
        )
        object.__setattr__(
            self,
            "selected",
            selected,
        )
        object.__setattr__(
            self,
            "omitted",
            omitted,
        )

    @property
    def selected_count(self):
        return len(self.selected)

    @property
    def omitted_count(self):
        return len(self.omitted)


class AtlasFacadeOrnamentDensityResolver:
    DENSITY_BUDGETS = {
        "low": 3,
        "medium": 6,
        "high": None,
    }

    @classmethod
    def resolve(
        cls,
        *,
        candidates,
        density_level,
        scale_ratio,
        nozzle_diameter_mm,
    ) -> AtlasFacadeOrnamentDensityAnalysis:
        candidates = tuple(candidates)

        if any(
            not isinstance(
                candidate,
                AtlasFacadeOrnamentCandidate,
            )
            for candidate in candidates
        ):
            raise TypeError(
                "candidates must contain "
                "AtlasFacadeOrnamentCandidate instances"
            )

        source_indices = tuple(
            candidate.source_index
            for candidate in candidates
        )

        if len(set(source_indices)) != len(
            source_indices
        ):
            raise ValueError(
                "duplicate ornament source_index"
            )

        density_level = (
            str(density_level)
            .strip()
            .lower()
        )

        if density_level not in cls.DENSITY_BUDGETS:
            raise ValueError(
                "density_level must be low, medium, or high"
            )

        scale_ratio = float(scale_ratio)
        nozzle_diameter_mm = float(
            nozzle_diameter_mm
        )

        printable = []
        physical_omitted = []

        for input_order, candidate in enumerate(
            candidates
        ):
            decision = (
                AtlasPhysicalDetailResolver.resolve(
                    real_size_m=(
                        candidate.real_size_m
                    ),
                    scale_ratio=scale_ratio,
                    nozzle_diameter_mm=(
                        nozzle_diameter_mm
                    ),
                    detail_type=(
                        candidate.ornament_kind
                    ),
                )
            )

            resolved = {
                "candidate": candidate,
                "input_order": input_order,
                "decision": decision,
            }

            if decision.action == "omit":
                physical_omitted.append(
                    resolved
                )
            else:
                printable.append(
                    resolved
                )

        printable.sort(
            key=lambda item: (
                -item["candidate"].priority,
                item["input_order"],
            )
        )

        configured_budget = (
            cls.DENSITY_BUDGETS[
                density_level
            ]
        )

        detail_budget = (
            len(printable)
            if configured_budget is None
            else configured_budget
        )

        selected_raw = printable[
            :detail_budget
        ]
        density_omitted_raw = printable[
            detail_budget:
        ]

        def build_item(
            raw,
            selection_status,
        ):
            candidate = raw["candidate"]
            decision = raw["decision"]

            return AtlasFacadeResolvedOrnament(
                source_index=(
                    candidate.source_index
                ),
                ornament_kind=(
                    candidate.ornament_kind
                ),
                priority=candidate.priority,
                action=decision.action,
                scaled_size_mm=(
                    decision.scaled_size_mm
                ),
                minimum_printable_mm=(
                    decision.minimum_printable_mm
                ),
                resolved_size_mm=(
                    decision.resolved_size_mm
                ),
                scale_factor=(
                    decision.scale_factor
                ),
                selection_status=(
                    selection_status
                ),
            )

        selected = tuple(
            build_item(
                raw,
                "selected",
            )
            for raw in selected_raw
        )

        omitted_by_input_order = sorted(
            (
                (
                    raw,
                    "physical_omit",
                )
                for raw in physical_omitted
            ),
            key=lambda item: item[0][
                "input_order"
            ],
        )

        omitted = tuple(
            build_item(
                raw,
                selection_status,
            )
            for raw, selection_status in (
                omitted_by_input_order
            )
        ) + tuple(
            build_item(
                raw,
                "density_omit",
            )
            for raw in density_omitted_raw
        )

        return AtlasFacadeOrnamentDensityAnalysis(
            density_level=density_level,
            selected=selected,
            omitted=omitted,
            candidate_count=len(candidates),
            printable_count=len(printable),
            detail_budget=detail_budget,
        )
