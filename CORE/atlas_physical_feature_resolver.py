from __future__ import annotations

from dataclasses import dataclass
import math


def _identifier(value, *, field_name):
    normalized = "_".join(
        str(value).strip().lower().split()
    )
    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )
    return normalized


def _positive_finite(value, *, field_name):
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{field_name} must be numeric"
        ) from exc

    if not math.isfinite(numeric) or numeric <= 0.0:
        raise ValueError(
            f"{field_name} must be finite and greater than zero"
        )

    return numeric


def _priority(value, *, field_name):
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{field_name} must be numeric"
        ) from exc

    if (
        not math.isfinite(numeric)
        or numeric < 0.0
        or numeric > 1.0
    ):
        raise ValueError(
            f"{field_name} must be finite and within 0..1"
        )

    return numeric


@dataclass(frozen=True, slots=True)
class AtlasPhysicalFeatureProfile:
    name: str
    nozzle_diameter_mm: float
    layer_height_mm: float
    product_size_mm: float
    material: str
    minimum_raised_width_mm: float
    minimum_raised_height_mm: float
    minimum_groove_width_mm: float | None = None
    minimum_groove_depth_mm: float | None = None
    maximum_unsupported_projection_mm: float | None = None
    minimum_connection_ratio: float | None = None
    maximum_unsupported_slope_degrees: float | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "name",
            _identifier(
                self.name,
                field_name="name",
            ),
        )
        object.__setattr__(
            self,
            "material",
            _identifier(
                self.material,
                field_name="material",
            ),
        )

        for field_name in (
            "nozzle_diameter_mm",
            "layer_height_mm",
            "product_size_mm",
            "minimum_raised_width_mm",
            "minimum_raised_height_mm",
        ):
            object.__setattr__(
                self,
                field_name,
                _positive_finite(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

        minimum_groove_width_mm = (
            self.nozzle_diameter_mm
            if self.minimum_groove_width_mm is None
            else _positive_finite(
                self.minimum_groove_width_mm,
                field_name="minimum_groove_width_mm",
            )
        )
        minimum_groove_depth_mm = (
            self.layer_height_mm
            if self.minimum_groove_depth_mm is None
            else _positive_finite(
                self.minimum_groove_depth_mm,
                field_name="minimum_groove_depth_mm",
            )
        )

        object.__setattr__(
            self,
            "minimum_groove_width_mm",
            minimum_groove_width_mm,
        )
        object.__setattr__(
            self,
            "minimum_groove_depth_mm",
            minimum_groove_depth_mm,
        )

        maximum_unsupported_projection_mm = (
            4.0 * self.nozzle_diameter_mm
            if self.maximum_unsupported_projection_mm is None
            else _positive_finite(
                self.maximum_unsupported_projection_mm,
                field_name="maximum_unsupported_projection_mm",
            )
        )

        object.__setattr__(
            self,
            "maximum_unsupported_projection_mm",
            maximum_unsupported_projection_mm,
        )

        minimum_connection_ratio = (
            0.20
            if self.minimum_connection_ratio is None
            else float(self.minimum_connection_ratio)
        )

        if (
            not math.isfinite(minimum_connection_ratio)
            or minimum_connection_ratio <= 0.0
            or minimum_connection_ratio > 1.0
        ):
            raise ValueError(
                "minimum_connection_ratio must be finite "
                "and within 0..1"
            )

        object.__setattr__(
            self,
            "minimum_connection_ratio",
            minimum_connection_ratio,
        )

        maximum_unsupported_slope_degrees = (
            45.0
            if self.maximum_unsupported_slope_degrees is None
            else float(self.maximum_unsupported_slope_degrees)
        )

        if (
            not math.isfinite(maximum_unsupported_slope_degrees)
            or maximum_unsupported_slope_degrees <= 0.0
            or maximum_unsupported_slope_degrees >= 90.0
        ):
            raise ValueError(
                "maximum_unsupported_slope_degrees must be finite "
                "and within 0..90"
            )

        object.__setattr__(
            self,
            "maximum_unsupported_slope_degrees",
            maximum_unsupported_slope_degrees,
        )


@dataclass(frozen=True, slots=True)
class AtlasSlopePhysicalFeatureDecision:
    feature_id: str
    semantic_class: str
    action: str
    unsupported_slope_degrees: float
    maximum_unsupported_slope_degrees: float
    semantic_importance: float
    readability_priority: float
    physical_feature_policy: str
    reason: str
    requires_operator_review: bool
    adjustments: tuple


@dataclass(frozen=True, slots=True)
class AtlasConnectionPhysicalFeatureDecision:
    feature_id: str
    semantic_class: str
    action: str
    connection_width_mm: float
    component_span_mm: float
    connection_ratio: float
    minimum_connection_ratio: float
    semantic_importance: float
    readability_priority: float
    physical_feature_policy: str
    reason: str
    requires_operator_review: bool
    adjustments: tuple


@dataclass(frozen=True, slots=True)
class AtlasProjectionPhysicalFeatureDecision:
    feature_id: str
    semantic_class: str
    action: str
    unsupported_projection_mm: float
    maximum_unsupported_projection_mm: float
    semantic_importance: float
    readability_priority: float
    physical_feature_policy: str
    reason: str
    requires_operator_review: bool
    adjustments: tuple


@dataclass(frozen=True, slots=True)
class AtlasGroovePhysicalFeatureDecision:
    feature_id: str
    semantic_class: str
    action: str
    measured_width_mm: float
    measured_depth_mm: float
    resolved_width_mm: float
    resolved_depth_mm: float
    semantic_importance: float
    readability_priority: float
    physical_feature_policy: str
    reason: str
    requires_operator_review: bool
    adjustments: tuple


@dataclass(frozen=True, slots=True)
class AtlasRepeatedPhysicalFeatureDecision:
    feature_id: str
    semantic_class: str
    action: str
    measured_repeat_count: int
    resolved_repeat_count: int
    semantic_importance: float
    readability_priority: float
    physical_feature_policy: str
    reason: str
    requires_operator_review: bool
    adjustments: tuple


@dataclass(frozen=True, slots=True)
class AtlasAdjacentPhysicalFeatureDecision:
    feature_ids: tuple[str, ...]
    semantic_class: str
    action: str
    measured_spacing_mm: float
    minimum_spacing_mm: float
    semantic_importance: float
    readability_priority: float
    physical_feature_policy: str
    reason: str
    requires_operator_review: bool
    adjustments: tuple


@dataclass(frozen=True, slots=True)
class AtlasPhysicalFeatureDecision:
    feature_id: str
    semantic_class: str
    action: str
    measured_width_mm: float
    measured_height_mm: float
    resolved_width_mm: float
    resolved_height_mm: float
    semantic_importance: float
    readability_priority: float
    physical_feature_policy: str
    reason: str
    requires_operator_review: bool
    adjustments: tuple


class AtlasPhysicalFeatureResolver:
    OMIT_THRESHOLD_RATIO = 0.25
    LOW_PRIORITY_THRESHOLD = 0.25

    @classmethod
    def resolve_scaled_raised_feature(
        cls,
        *,
        feature_id,
        semantic_class,
        source_width_mm_at_reference,
        source_height_mm_at_reference,
        reference_product_size_mm,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        source_width_mm_at_reference = _positive_finite(
            source_width_mm_at_reference,
            field_name="source_width_mm_at_reference",
        )
        source_height_mm_at_reference = _positive_finite(
            source_height_mm_at_reference,
            field_name="source_height_mm_at_reference",
        )
        reference_product_size_mm = _positive_finite(
            reference_product_size_mm,
            field_name="reference_product_size_mm",
        )

        scale_factor = (
            profile.product_size_mm
            / reference_product_size_mm
        )

        measured_width_mm = (
            source_width_mm_at_reference
            * scale_factor
        )
        measured_height_mm = (
            source_height_mm_at_reference
            * scale_factor
        )

        return cls.resolve_raised_feature(
            feature_id=feature_id,
            semantic_class=semantic_class,
            measured_width_mm=measured_width_mm,
            measured_height_mm=measured_height_mm,
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            profile=profile,
        )

    @classmethod
    def resolve_slope_feature(
        cls,
        *,
        feature_id,
        semantic_class,
        unsupported_slope_degrees,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        feature_id = _identifier(
            feature_id,
            field_name="feature_id",
        )
        semantic_class = _identifier(
            semantic_class,
            field_name="semantic_class",
        )

        try:
            unsupported_slope_degrees = float(
                unsupported_slope_degrees
            )
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "unsupported_slope_degrees must be numeric"
            ) from exc

        if (
            not math.isfinite(unsupported_slope_degrees)
            or unsupported_slope_degrees <= 0.0
            or unsupported_slope_degrees >= 90.0
        ):
            raise ValueError(
                "unsupported_slope_degrees must be finite "
                "and within 0..90"
            )

        semantic_importance = _priority(
            semantic_importance,
            field_name="semantic_importance",
        )
        readability_priority = _priority(
            readability_priority,
            field_name="readability_priority",
        )
        physical_feature_policy = _identifier(
            physical_feature_policy,
            field_name="physical_feature_policy",
        )

        if (
            unsupported_slope_degrees
            <= profile.maximum_unsupported_slope_degrees
        ):
            raise NotImplementedError(
                "supported slope decisions are not implemented yet"
            )

        return AtlasSlopePhysicalFeatureDecision(
            feature_id=feature_id,
            semantic_class=semantic_class,
            action="require_operator_review",
            unsupported_slope_degrees=unsupported_slope_degrees,
            maximum_unsupported_slope_degrees=(
                profile.maximum_unsupported_slope_degrees
            ),
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            reason="unsupported_slope_exceeds_profile_limit",
            requires_operator_review=True,
            adjustments=(),
        )

    @classmethod
    def resolve_connection_feature(
        cls,
        *,
        feature_id,
        semantic_class,
        connection_width_mm,
        component_span_mm,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        feature_id = _identifier(
            feature_id,
            field_name="feature_id",
        )
        semantic_class = _identifier(
            semantic_class,
            field_name="semantic_class",
        )
        connection_width_mm = _positive_finite(
            connection_width_mm,
            field_name="connection_width_mm",
        )
        component_span_mm = _positive_finite(
            component_span_mm,
            field_name="component_span_mm",
        )

        if connection_width_mm > component_span_mm:
            raise ValueError(
                "connection_width_mm must not exceed "
                "component_span_mm"
            )

        semantic_importance = _priority(
            semantic_importance,
            field_name="semantic_importance",
        )
        readability_priority = _priority(
            readability_priority,
            field_name="readability_priority",
        )
        physical_feature_policy = _identifier(
            physical_feature_policy,
            field_name="physical_feature_policy",
        )

        connection_ratio = (
            connection_width_mm / component_span_mm
        )

        if connection_ratio >= profile.minimum_connection_ratio:
            raise NotImplementedError(
                "safe connection decisions are not implemented yet"
            )

        return AtlasConnectionPhysicalFeatureDecision(
            feature_id=feature_id,
            semantic_class=semantic_class,
            action="require_operator_review",
            connection_width_mm=connection_width_mm,
            component_span_mm=component_span_mm,
            connection_ratio=connection_ratio,
            minimum_connection_ratio=(
                profile.minimum_connection_ratio
            ),
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            reason="fragile_connection_below_profile_ratio",
            requires_operator_review=True,
            adjustments=(),
        )

    @classmethod
    def resolve_projection_feature(
        cls,
        *,
        feature_id,
        semantic_class,
        unsupported_projection_mm,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        feature_id = _identifier(
            feature_id,
            field_name="feature_id",
        )
        semantic_class = _identifier(
            semantic_class,
            field_name="semantic_class",
        )
        unsupported_projection_mm = _positive_finite(
            unsupported_projection_mm,
            field_name="unsupported_projection_mm",
        )
        semantic_importance = _priority(
            semantic_importance,
            field_name="semantic_importance",
        )
        readability_priority = _priority(
            readability_priority,
            field_name="readability_priority",
        )
        physical_feature_policy = _identifier(
            physical_feature_policy,
            field_name="physical_feature_policy",
        )

        if (
            unsupported_projection_mm
            <= profile.maximum_unsupported_projection_mm
        ):
            raise NotImplementedError(
                "supported projection decisions are not implemented yet"
            )

        return AtlasProjectionPhysicalFeatureDecision(
            feature_id=feature_id,
            semantic_class=semantic_class,
            action="require_operator_review",
            unsupported_projection_mm=unsupported_projection_mm,
            maximum_unsupported_projection_mm=(
                profile.maximum_unsupported_projection_mm
            ),
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            reason=(
                "unsupported_projection_exceeds_profile_limit"
            ),
            requires_operator_review=True,
            adjustments=(),
        )

    @classmethod
    def resolve_groove_feature(
        cls,
        *,
        feature_id,
        semantic_class,
        measured_width_mm,
        measured_depth_mm,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        feature_id = _identifier(
            feature_id,
            field_name="feature_id",
        )
        semantic_class = _identifier(
            semantic_class,
            field_name="semantic_class",
        )
        measured_width_mm = _positive_finite(
            measured_width_mm,
            field_name="measured_width_mm",
        )
        measured_depth_mm = _positive_finite(
            measured_depth_mm,
            field_name="measured_depth_mm",
        )
        semantic_importance = _priority(
            semantic_importance,
            field_name="semantic_importance",
        )
        readability_priority = _priority(
            readability_priority,
            field_name="readability_priority",
        )
        physical_feature_policy = _identifier(
            physical_feature_policy,
            field_name="physical_feature_policy",
        )

        below_minimum = (
            measured_width_mm < profile.minimum_groove_width_mm
            or measured_depth_mm < profile.minimum_groove_depth_mm
        )

        if below_minimum:
            if physical_feature_policy != "enlarge_if_needed":
                raise NotImplementedError(
                    "sub-minimum groove policy "
                    "is not implemented yet"
                )

            resolved_width_mm = max(
                measured_width_mm,
                profile.minimum_groove_width_mm,
            )
            resolved_depth_mm = max(
                measured_depth_mm,
                profile.minimum_groove_depth_mm,
            )

            adjustments = []

            if resolved_width_mm > measured_width_mm:
                adjustments.append(
                    {
                        "field": "width_mm",
                        "from": measured_width_mm,
                        "to": resolved_width_mm,
                    }
                )

            if resolved_depth_mm > measured_depth_mm:
                adjustments.append(
                    {
                        "field": "depth_mm",
                        "from": measured_depth_mm,
                        "to": resolved_depth_mm,
                    }
                )

            return AtlasGroovePhysicalFeatureDecision(
                feature_id=feature_id,
                semantic_class=semantic_class,
                action="enlarge",
                measured_width_mm=measured_width_mm,
                measured_depth_mm=measured_depth_mm,
                resolved_width_mm=resolved_width_mm,
                resolved_depth_mm=resolved_depth_mm,
                semantic_importance=semantic_importance,
                readability_priority=readability_priority,
                physical_feature_policy=physical_feature_policy,
                reason="groove_below_minimum",
                requires_operator_review=False,
                adjustments=tuple(adjustments),
            )

        return AtlasGroovePhysicalFeatureDecision(
            feature_id=feature_id,
            semantic_class=semantic_class,
            action="preserve",
            measured_width_mm=measured_width_mm,
            measured_depth_mm=measured_depth_mm,
            resolved_width_mm=measured_width_mm,
            resolved_depth_mm=measured_depth_mm,
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            reason="groove_already_readable",
            requires_operator_review=False,
            adjustments=(),
        )

    @classmethod
    def resolve_repeated_detail(
        cls,
        *,
        feature_id,
        semantic_class,
        measured_repeat_count,
        maximum_readable_repeat_count,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        feature_id = _identifier(
            feature_id,
            field_name="feature_id",
        )
        semantic_class = _identifier(
            semantic_class,
            field_name="semantic_class",
        )

        if (
            isinstance(measured_repeat_count, bool)
            or not isinstance(measured_repeat_count, int)
            or measured_repeat_count <= 0
        ):
            raise ValueError(
                "measured_repeat_count must be a positive integer"
            )

        if (
            isinstance(maximum_readable_repeat_count, bool)
            or not isinstance(maximum_readable_repeat_count, int)
            or maximum_readable_repeat_count <= 0
        ):
            raise ValueError(
                "maximum_readable_repeat_count must be a positive integer"
            )

        semantic_importance = _priority(
            semantic_importance,
            field_name="semantic_importance",
        )
        readability_priority = _priority(
            readability_priority,
            field_name="readability_priority",
        )
        physical_feature_policy = _identifier(
            physical_feature_policy,
            field_name="physical_feature_policy",
        )

        if measured_repeat_count <= maximum_readable_repeat_count:
            raise NotImplementedError(
                "readable repeated-detail decisions "
                "are not implemented yet"
            )

        if physical_feature_policy != "simplify_if_needed":
            raise NotImplementedError(
                "over-dense repeated-detail policy "
                "is not implemented yet"
            )

        return AtlasRepeatedPhysicalFeatureDecision(
            feature_id=feature_id,
            semantic_class=semantic_class,
            action="simplify",
            measured_repeat_count=measured_repeat_count,
            resolved_repeat_count=maximum_readable_repeat_count,
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            reason=(
                "repeated_detail_density_above_readable_budget"
            ),
            requires_operator_review=False,
            adjustments=(
                {
                    "field": "repeat_count",
                    "from": measured_repeat_count,
                    "to": maximum_readable_repeat_count,
                },
            ),
        )

    @classmethod
    def resolve_adjacent_features(
        cls,
        *,
        feature_ids,
        semantic_class,
        measured_spacing_mm,
        minimum_spacing_mm,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        try:
            feature_ids = tuple(
                _identifier(
                    value,
                    field_name="feature_id",
                )
                for value in feature_ids
            )
        except TypeError as exc:
            raise TypeError(
                "feature_ids must be an iterable"
            ) from exc

        if len(feature_ids) < 2:
            raise ValueError(
                "feature_ids must contain at least two features"
            )

        if len(set(feature_ids)) != len(feature_ids):
            raise ValueError(
                "feature_ids must not contain duplicates"
            )

        semantic_class = _identifier(
            semantic_class,
            field_name="semantic_class",
        )
        measured_spacing_mm = _positive_finite(
            measured_spacing_mm,
            field_name="measured_spacing_mm",
        )
        minimum_spacing_mm = _positive_finite(
            minimum_spacing_mm,
            field_name="minimum_spacing_mm",
        )
        semantic_importance = _priority(
            semantic_importance,
            field_name="semantic_importance",
        )
        readability_priority = _priority(
            readability_priority,
            field_name="readability_priority",
        )
        physical_feature_policy = _identifier(
            physical_feature_policy,
            field_name="physical_feature_policy",
        )

        if measured_spacing_mm >= minimum_spacing_mm:
            raise NotImplementedError(
                "readable adjacent-feature decisions "
                "are not implemented yet"
            )

        if physical_feature_policy != "merge_if_needed":
            raise NotImplementedError(
                "sub-minimum adjacent-feature policy "
                "is not implemented yet"
            )

        return AtlasAdjacentPhysicalFeatureDecision(
            feature_ids=feature_ids,
            semantic_class=semantic_class,
            action="merge",
            measured_spacing_mm=measured_spacing_mm,
            minimum_spacing_mm=minimum_spacing_mm,
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            reason=(
                "adjacent_features_below_minimum_spacing"
            ),
            requires_operator_review=False,
            adjustments=(
                {
                    "field": "feature_count",
                    "from": len(feature_ids),
                    "to": 1,
                },
            ),
        )

    @classmethod
    def resolve_raised_feature(
        cls,
        *,
        feature_id,
        semantic_class,
        measured_width_mm,
        measured_height_mm,
        semantic_importance,
        readability_priority,
        physical_feature_policy,
        profile,
    ):
        if not isinstance(
            profile,
            AtlasPhysicalFeatureProfile,
        ):
            raise TypeError(
                "profile must be an AtlasPhysicalFeatureProfile"
            )

        feature_id = _identifier(
            feature_id,
            field_name="feature_id",
        )
        semantic_class = _identifier(
            semantic_class,
            field_name="semantic_class",
        )
        measured_width_mm = _positive_finite(
            measured_width_mm,
            field_name="measured_width_mm",
        )
        measured_height_mm = _positive_finite(
            measured_height_mm,
            field_name="measured_height_mm",
        )
        semantic_importance = _priority(
            semantic_importance,
            field_name="semantic_importance",
        )
        readability_priority = _priority(
            readability_priority,
            field_name="readability_priority",
        )
        physical_feature_policy = _identifier(
            physical_feature_policy,
            field_name="physical_feature_policy",
        )

        below_minimum = (
            measured_width_mm
            < profile.minimum_raised_width_mm
            or measured_height_mm
            < profile.minimum_raised_height_mm
        )

        if below_minimum:
            extremely_small = (
                measured_width_mm
                < profile.minimum_raised_width_mm
                * cls.OMIT_THRESHOLD_RATIO
                and measured_height_mm
                < profile.minimum_raised_height_mm
                * cls.OMIT_THRESHOLD_RATIO
            )
            low_priority = (
                semantic_importance
                <= cls.LOW_PRIORITY_THRESHOLD
                and readability_priority
                <= cls.LOW_PRIORITY_THRESHOLD
            )

            if extremely_small and low_priority:
                return AtlasPhysicalFeatureDecision(
                    feature_id=feature_id,
                    semantic_class=semantic_class,
                    action="omit",
                    measured_width_mm=measured_width_mm,
                    measured_height_mm=measured_height_mm,
                    resolved_width_mm=0.0,
                    resolved_height_mm=0.0,
                    semantic_importance=semantic_importance,
                    readability_priority=readability_priority,
                    physical_feature_policy=physical_feature_policy,
                    reason=(
                        "feature_below_meaningful_printable_scale"
                    ),
                    requires_operator_review=False,
                    adjustments=(
                        {
                            "field": "feature",
                            "from": "present",
                            "to": "omitted",
                        },
                    ),
                )

            if physical_feature_policy == "engrave_if_needed":
                resolved_width_mm = max(
                    measured_width_mm,
                    profile.nozzle_diameter_mm,
                )
                resolved_height_mm = max(
                    measured_height_mm,
                    profile.layer_height_mm,
                )

                adjustments = [
                    {
                        "field": "representation",
                        "from": "raised",
                        "to": "engraving",
                    },
                ]

                if resolved_width_mm > measured_width_mm:
                    adjustments.append(
                        {
                            "field": "width_mm",
                            "from": measured_width_mm,
                            "to": resolved_width_mm,
                        }
                    )

                if resolved_height_mm > measured_height_mm:
                    adjustments.append(
                        {
                            "field": "depth_mm",
                            "from": measured_height_mm,
                            "to": resolved_height_mm,
                        }
                    )

                return AtlasPhysicalFeatureDecision(
                    feature_id=feature_id,
                    semantic_class=semantic_class,
                    action="convert_to_engraving",
                    measured_width_mm=measured_width_mm,
                    measured_height_mm=measured_height_mm,
                    resolved_width_mm=resolved_width_mm,
                    resolved_height_mm=resolved_height_mm,
                    semantic_importance=semantic_importance,
                    readability_priority=readability_priority,
                    physical_feature_policy=physical_feature_policy,
                    reason=(
                        "raised_feature_better_preserved_as_engraving"
                    ),
                    requires_operator_review=False,
                    adjustments=tuple(adjustments),
                )

            high_priority = (
                semantic_importance >= 0.75
                or readability_priority >= 0.75
            )

            if (
                physical_feature_policy != "enlarge_if_needed"
                and high_priority
            ):
                return AtlasPhysicalFeatureDecision(
                    feature_id=feature_id,
                    semantic_class=semantic_class,
                    action="require_operator_review",
                    measured_width_mm=measured_width_mm,
                    measured_height_mm=measured_height_mm,
                    resolved_width_mm=measured_width_mm,
                    resolved_height_mm=measured_height_mm,
                    semantic_importance=semantic_importance,
                    readability_priority=readability_priority,
                    physical_feature_policy=physical_feature_policy,
                    reason=(
                        "important_feature_below_physical_minimum"
                    ),
                    requires_operator_review=True,
                    adjustments=(),
                )

            if physical_feature_policy != "enlarge_if_needed":
                raise NotImplementedError(
                    "sub-minimum raised-feature policy "
                    "is not implemented yet"
                )

            resolved_width_mm = max(
                measured_width_mm,
                profile.minimum_raised_width_mm,
            )
            resolved_height_mm = max(
                measured_height_mm,
                profile.minimum_raised_height_mm,
            )

            adjustments = []

            if resolved_width_mm > measured_width_mm:
                adjustments.append(
                    {
                        "field": "width_mm",
                        "from": measured_width_mm,
                        "to": resolved_width_mm,
                    }
                )

            if resolved_height_mm > measured_height_mm:
                adjustments.append(
                    {
                        "field": "height_mm",
                        "from": measured_height_mm,
                        "to": resolved_height_mm,
                    }
                )

            return AtlasPhysicalFeatureDecision(
                feature_id=feature_id,
                semantic_class=semantic_class,
                action="enlarge",
                measured_width_mm=measured_width_mm,
                measured_height_mm=measured_height_mm,
                resolved_width_mm=resolved_width_mm,
                resolved_height_mm=resolved_height_mm,
                semantic_importance=semantic_importance,
                readability_priority=readability_priority,
                physical_feature_policy=physical_feature_policy,
                reason="raised_feature_below_minimum",
                requires_operator_review=False,
                adjustments=tuple(adjustments),
            )

        return AtlasPhysicalFeatureDecision(
            feature_id=feature_id,
            semantic_class=semantic_class,
            action="preserve",
            measured_width_mm=measured_width_mm,
            measured_height_mm=measured_height_mm,
            resolved_width_mm=measured_width_mm,
            resolved_height_mm=measured_height_mm,
            semantic_importance=semantic_importance,
            readability_priority=readability_priority,
            physical_feature_policy=physical_feature_policy,
            reason="feature_already_readable",
            requires_operator_review=False,
            adjustments=(),
        )
