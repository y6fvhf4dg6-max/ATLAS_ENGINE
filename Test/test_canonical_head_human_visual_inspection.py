import dataclasses

import pytest

from CORE.atlas_canonical_head_human_visual_inspection import (
    AtlasCanonicalHeadHumanVisualInspection,
)


def make_inspection(**overrides):
    values = dict(
        representation_id="portrait_relief_v1",
        representation_kind="relief",
        inspection_id="inspection_a",
        view_conditions=(
            "front",
            "three_quarter",
            "profile",
        ),
        viewing_distance_mm=600.0,
        illumination_condition="diffuse neutral indoor light",
        camera_view_comparison_condition=(
            "matched framing and comparison orientation"
        ),
        inspection_state="OBSERVED",
        evidence_provenance="controlled human visual inspection",
        evidence_kind="SUBJECTIVE",
    )
    values.update(overrides)
    return AtlasCanonicalHeadHumanVisualInspection(**values)


def test_contract_is_frozen():
    inspection = make_inspection()

    with pytest.raises(dataclasses.FrozenInstanceError):
        inspection.inspection_id = "inspection_b"


@pytest.mark.parametrize(
    "kind",
    (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    ),
)
def test_supported_representation_kinds(kind):
    inspection = make_inspection(
        representation_kind=kind,
    )

    assert inspection.representation_kind == kind


def test_representation_kind_is_normalized():
    inspection = make_inspection(
        representation_kind=" Story Kit Component ",
    )

    assert inspection.representation_kind == "story_kit_component"


@pytest.mark.parametrize(
    "field_name",
    (
        "representation_id",
        "inspection_id",
        "illumination_condition",
        "camera_view_comparison_condition",
        "evidence_provenance",
    ),
)
def test_required_text_fields_reject_blank(field_name):
    with pytest.raises(ValueError):
        make_inspection(
            **{field_name: "   "}
        )


@pytest.mark.parametrize(
    "view",
    (
        "front",
        "three_quarter",
        "profile",
    ),
)
def test_supported_view_conditions(view):
    inspection = make_inspection(
        view_conditions=(view,),
    )

    assert inspection.view_conditions == (view,)


def test_view_conditions_are_normalized_and_deduplicated():
    inspection = make_inspection(
        view_conditions=(
            " Front ",
            "Three Quarter",
            "profile",
            "front",
        ),
    )

    assert inspection.view_conditions == (
        "front",
        "three_quarter",
        "profile",
    )


def test_view_conditions_reject_string_collection():
    with pytest.raises(TypeError):
        make_inspection(
            view_conditions="front",
        )


def test_view_conditions_reject_none():
    with pytest.raises(TypeError):
        make_inspection(
            view_conditions=None,
        )


def test_view_conditions_require_at_least_one_view():
    with pytest.raises(ValueError):
        make_inspection(
            view_conditions=(),
        )


def test_unknown_view_condition_is_rejected():
    with pytest.raises(ValueError):
        make_inspection(
            view_conditions=("rear",),
        )


@pytest.mark.parametrize(
    "distance",
    (
        1.0,
        350.0,
        600,
        1500.5,
    ),
)
def test_viewing_distance_accepts_positive_finite_values(distance):
    inspection = make_inspection(
        viewing_distance_mm=distance,
    )

    assert inspection.viewing_distance_mm == pytest.approx(
        float(distance)
    )


@pytest.mark.parametrize(
    "distance",
    (
        0.0,
        -1.0,
        float("inf"),
        float("-inf"),
        float("nan"),
    ),
)
def test_viewing_distance_rejects_non_positive_or_non_finite(distance):
    with pytest.raises(ValueError):
        make_inspection(
            viewing_distance_mm=distance,
        )


def test_viewing_distance_rejects_non_numeric_value():
    with pytest.raises(ValueError):
        make_inspection(
            viewing_distance_mm="far",
        )


@pytest.mark.parametrize(
    "state",
    (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_PERFORMED",
    ),
)
def test_supported_inspection_states(state):
    inspection = make_inspection(
        inspection_state=state,
    )

    assert inspection.inspection_state == state


def test_inspection_state_is_normalized():
    inspection = make_inspection(
        inspection_state=" not performed ",
    )

    assert inspection.inspection_state == "NOT_PERFORMED"


def test_unknown_inspection_state_is_rejected():
    with pytest.raises(ValueError):
        make_inspection(
            inspection_state="ESTIMATED",
        )


def test_evidence_kind_is_subjective():
    inspection = make_inspection(
        evidence_kind=" subjective ",
    )

    assert inspection.evidence_kind == "SUBJECTIVE"


@pytest.mark.parametrize(
    "evidence_kind",
    (
        "OBJECTIVE",
        "METRIC",
        "AUTOMATED",
        "VERIFIED",
    ),
)
def test_non_subjective_evidence_kind_is_rejected(evidence_kind):
    with pytest.raises(ValueError):
        make_inspection(
            evidence_kind=evidence_kind,
        )


def test_contract_preserves_explicit_control_conditions():
    inspection = make_inspection()

    assert inspection.view_conditions == (
        "front",
        "three_quarter",
        "profile",
    )
    assert inspection.viewing_distance_mm == pytest.approx(600.0)
    assert (
        inspection.illumination_condition
        == "diffuse neutral indoor light"
    )
    assert (
        inspection.camera_view_comparison_condition
        == "matched framing and comparison orientation"
    )
    assert inspection.evidence_kind == "SUBJECTIVE"


def test_contract_does_not_claim_likeness_or_acceptance():
    inspection = make_inspection()

    assert not hasattr(inspection, "likeness_score")
    assert not hasattr(inspection, "customer_visible_score")
    assert not hasattr(inspection, "commercial_acceptance")
    assert not hasattr(inspection, "acceptance_state")


def test_contract_does_not_claim_regional_preservation():
    inspection = make_inspection()

    assert not hasattr(inspection, "preservation_state")
    assert not hasattr(inspection, "affected_regions")


def test_contract_does_not_claim_metric_result():
    inspection = make_inspection()

    assert not hasattr(inspection, "metric_score")
    assert not hasattr(inspection, "threshold")
    assert not hasattr(inspection, "pass_fail")


def test_contract_does_not_claim_production_or_phase_decision():
    inspection = make_inspection()

    assert not hasattr(inspection, "production_decision")
    assert not hasattr(inspection, "phase_9_authorized")
