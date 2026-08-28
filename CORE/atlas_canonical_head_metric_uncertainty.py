from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricUncertaintyComponent:
    source_family: str
    evidence_state: str
    uncertainty_mm: float | None
    provenance_reference: str

    SOURCE_FAMILIES = (
        "GT_ACQUISITION_SCANNER",
        "CALIBRATION",
        "SEGMENTATION",
        "LANDMARK_LOCALIZATION",
        "ALIGNMENT",
        "CORRESPONDENCE",
        "SAMPLING",
        "EXPRESSION_POSTURE_MISMATCH",
        "PREDICTION_RECONSTRUCTION",
        "REPEAT_CAPTURE",
    )

    EVIDENCE_STATES = (
        "QUANTIFIED",
        "UNRESOLVED",
    )

    GT_SIDE_SOURCE_FAMILIES = (
        "GT_ACQUISITION_SCANNER",
        "CALIBRATION",
        "SEGMENTATION",
    )

    def __post_init__(self) -> None:
        source_family = self._normalize_state(
            self.source_family,
            name="source_family",
        )
        evidence_state = self._normalize_state(
            self.evidence_state,
            name="evidence_state",
        )

        if source_family not in self.SOURCE_FAMILIES:
            raise ValueError(
                f"source_family must be one of {self.SOURCE_FAMILIES}."
            )

        if evidence_state not in self.EVIDENCE_STATES:
            raise ValueError(
                f"evidence_state must be one of {self.EVIDENCE_STATES}."
            )

        provenance_reference = self.provenance_reference
        if (
            not isinstance(provenance_reference, str)
            or not provenance_reference.strip()
        ):
            raise ValueError(
                "provenance_reference must be a non-empty string."
            )

        provenance_reference = provenance_reference.strip()

        if evidence_state == "QUANTIFIED":
            if self.uncertainty_mm is None:
                raise ValueError(
                    "QUANTIFIED uncertainty requires uncertainty_mm."
                )

            uncertainty_mm = float(
                self.uncertainty_mm
            )

            if (
                not np.isfinite(uncertainty_mm)
                or uncertainty_mm < 0.0
            ):
                raise ValueError(
                    "uncertainty_mm must be finite and non-negative."
                )
        else:
            if self.uncertainty_mm is not None:
                raise ValueError(
                    "UNRESOLVED uncertainty cannot carry numeric "
                    "uncertainty_mm."
                )

            uncertainty_mm = None

        object.__setattr__(
            self,
            "source_family",
            source_family,
        )
        object.__setattr__(
            self,
            "evidence_state",
            evidence_state,
        )
        object.__setattr__(
            self,
            "uncertainty_mm",
            uncertainty_mm,
        )
        object.__setattr__(
            self,
            "provenance_reference",
            provenance_reference,
        )

    @staticmethod
    def _normalize_state(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = "_".join(
            value.strip().upper().replace("-", "_").split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricUncertaintyEvaluationResult:
    components: tuple[AtlasCanonicalHeadMetricUncertaintyComponent, ...]
    gt_uncertainty_floor_mm: float | None
    gt_uncertainty_floor_state: str
    observed_metric_error_mm: float
    precise_anatomical_error_state: str

    GT_FLOOR_STATES = (
        "ESTABLISHED",
        "UNRESOLVED",
    )

    PRECISE_ERROR_STATES = (
        "NOT_RESOLVED_BELOW_OR_AT_GT_FLOOR",
        "ABOVE_GT_FLOOR_OBSERVED_DIFFERENCE",
        "UNRESOLVED_GT_FLOOR",
    )

    def __post_init__(self) -> None:
        if not isinstance(self.components, tuple):
            raise TypeError(
                "components must be a tuple."
            )

        if not self.components:
            raise ValueError(
                "components must not be empty."
            )

        normalized_components = []

        for component in self.components:
            if not isinstance(
                component,
                AtlasCanonicalHeadMetricUncertaintyComponent,
            ):
                raise TypeError(
                    "components must contain only "
                    "AtlasCanonicalHeadMetricUncertaintyComponent."
                )

            try:
                component = AtlasCanonicalHeadMetricUncertaintyComponent(
                    source_family=component.source_family,
                    evidence_state=component.evidence_state,
                    uncertainty_mm=component.uncertainty_mm,
                    provenance_reference=component.provenance_reference,
                )
            except AttributeError as exc:
                raise ValueError(
                    "uncertainty components must satisfy the complete "
                    "AtlasCanonicalHeadMetricUncertaintyComponent contract."
                ) from exc

            normalized_components.append(component)

        normalized_components = tuple(normalized_components)

        object.__setattr__(
            self,
            "components",
            normalized_components,
        )

        gt_floor_state = (
            AtlasCanonicalHeadMetricUncertaintyComponent
            ._normalize_state(
                self.gt_uncertainty_floor_state,
                name="gt_uncertainty_floor_state",
            )
        )

        if gt_floor_state not in self.GT_FLOOR_STATES:
            raise ValueError(
                "gt_uncertainty_floor_state must be one of "
                f"{self.GT_FLOOR_STATES}."
            )

        observed_metric_error_mm = float(
            self.observed_metric_error_mm
        )

        if (
            not np.isfinite(observed_metric_error_mm)
            or observed_metric_error_mm < 0.0
        ):
            raise ValueError(
                "observed_metric_error_mm must be finite and non-negative."
            )

        if gt_floor_state == "ESTABLISHED":
            if self.gt_uncertainty_floor_mm is None:
                raise ValueError(
                    "ESTABLISHED GT uncertainty floor requires "
                    "gt_uncertainty_floor_mm."
                )

            gt_floor_mm = float(
                self.gt_uncertainty_floor_mm
            )

            if (
                not np.isfinite(gt_floor_mm)
                or gt_floor_mm < 0.0
            ):
                raise ValueError(
                    "gt_uncertainty_floor_mm must be finite "
                    "and non-negative."
                )

            quantified_gt_components = tuple(
                component
                for component in self.components
                if (
                    component.source_family
                    in AtlasCanonicalHeadMetricUncertaintyComponent
                    .GT_SIDE_SOURCE_FAMILIES
                    and component.evidence_state == "QUANTIFIED"
                )
            )

            if not quantified_gt_components:
                raise ValueError(
                    "ESTABLISHED GT uncertainty floor requires "
                    "quantified GT-side uncertainty evidence."
                )

            if not any(
                np.isclose(
                    gt_floor_mm,
                    component.uncertainty_mm,
                    rtol=0.0,
                    atol=1e-12,
                )
                for component in quantified_gt_components
            ):
                raise ValueError(
                    "ESTABLISHED GT uncertainty floor must match a "
                    "quantified GT-side uncertainty evidence value; "
                    "no combined uncertainty model is defined."
                )

            precise_state = (
                "NOT_RESOLVED_BELOW_OR_AT_GT_FLOOR"
                if observed_metric_error_mm <= gt_floor_mm
                else "ABOVE_GT_FLOOR_OBSERVED_DIFFERENCE"
            )
        else:
            if self.gt_uncertainty_floor_mm is not None:
                raise ValueError(
                    "UNRESOLVED GT uncertainty floor cannot carry "
                    "numeric gt_uncertainty_floor_mm."
                )

            gt_floor_mm = None
            precise_state = "UNRESOLVED_GT_FLOOR"

        supplied_precise_state = (
            AtlasCanonicalHeadMetricUncertaintyComponent
            ._normalize_state(
                self.precise_anatomical_error_state,
                name="precise_anatomical_error_state",
            )
        )

        if supplied_precise_state not in self.PRECISE_ERROR_STATES:
            raise ValueError(
                "precise_anatomical_error_state must be one of "
                f"{self.PRECISE_ERROR_STATES}."
            )

        if supplied_precise_state != precise_state:
            raise ValueError(
                "precise_anatomical_error_state must be derived "
                "from the GT uncertainty floor and observed metric error."
            )

        object.__setattr__(
            self,
            "gt_uncertainty_floor_mm",
            gt_floor_mm,
        )
        object.__setattr__(
            self,
            "gt_uncertainty_floor_state",
            gt_floor_state,
        )
        object.__setattr__(
            self,
            "observed_metric_error_mm",
            observed_metric_error_mm,
        )
        object.__setattr__(
            self,
            "precise_anatomical_error_state",
            precise_state,
        )


class AtlasCanonicalHeadMetricUncertaintyEvaluation:
    @classmethod
    def evaluate(
        cls,
        *,
        components: object,
        gt_uncertainty_floor_mm: object,
        gt_uncertainty_floor_state: object,
        observed_metric_error_mm: object,
    ) -> AtlasCanonicalHeadMetricUncertaintyEvaluationResult:
        try:
            normalized_components = tuple(
                components
            )
        except TypeError as exc:
            raise TypeError(
                "components must be iterable."
            ) from exc

        normalized_gt_floor_state = (
            AtlasCanonicalHeadMetricUncertaintyComponent
            ._normalize_state(
                gt_uncertainty_floor_state,
                name="gt_uncertainty_floor_state",
            )
        )

        observed_error = float(
            observed_metric_error_mm
        )

        if normalized_gt_floor_state == "ESTABLISHED":
            floor = float(
                gt_uncertainty_floor_mm
            )
            precise_state = (
                "NOT_RESOLVED_BELOW_OR_AT_GT_FLOOR"
                if observed_error <= floor
                else "ABOVE_GT_FLOOR_OBSERVED_DIFFERENCE"
            )
        else:
            precise_state = "UNRESOLVED_GT_FLOOR"

        return AtlasCanonicalHeadMetricUncertaintyEvaluationResult(
            components=normalized_components,
            gt_uncertainty_floor_mm=gt_uncertainty_floor_mm,
            gt_uncertainty_floor_state=normalized_gt_floor_state,
            observed_metric_error_mm=observed_error,
            precise_anatomical_error_state=precise_state,
        )
