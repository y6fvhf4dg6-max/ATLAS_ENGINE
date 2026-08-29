import dataclasses

import pytest

from CORE.atlas_canonical_head_digital_physical_failure_classification import (
    AtlasCanonicalHeadDigitalPhysicalFailureClassification,
)


def make_classification(**overrides):
    values = dict(
        representation_id="portrait_relief_v1",
        representation_kind="relief",
        failure_id="failure_a",
        observation_state="OBSERVED",
        failure_attribution="slicer",
        evidence_provenance="controlled physical failure audit",
        attribution_basis="slice completed with reproducible geometry error",
    )
    values.update(overrides)
    return AtlasCanonicalHeadDigitalPhysicalFailureClassification(**values)


def test_contract_is_frozen():
    classification = make_classification()

    with pytest.raises(dataclasses.FrozenInstanceError):
        classification.failure_id = "failure_b"


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
    classification = make_classification(
        representation_kind=kind,
    )

    assert classification.representation_kind == kind


def test_representation_kind_is_normalized():
    classification = make_classification(
        representation_kind=" Story Kit Component ",
    )

    assert classification.representation_kind == "story_kit_component"


@pytest.mark.parametrize(
    "attribution",
    (
        "reconstruction",
        "canonical_to_physical_adapter",
        "lod",
        "slicer",
        "printer",
        "material",
        "post_processing",
    ),
)
def test_supported_failure_attributions(attribution):
    classification = make_classification(
        failure_attribution=attribution,
    )

    assert classification.failure_attribution == attribution


def test_failure_attribution_is_normalized():
    classification = make_classification(
        failure_attribution=" Post Processing ",
    )

    assert classification.failure_attribution == "post_processing"


@pytest.mark.parametrize(
    "field_name",
    (
        "representation_id",
        "failure_id",
        "evidence_provenance",
        "attribution_basis",
    ),
)
def test_required_text_fields_reject_blank(field_name):
    with pytest.raises(ValueError):
        make_classification(
            **{field_name: "   "}
        )


@pytest.mark.parametrize(
    "state",
    (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_supported_observation_states(state):
    kwargs = {
        "observation_state": state,
    }

    if state != "OBSERVED":
        kwargs["failure_attribution"] = state.lower()

    classification = make_classification(**kwargs)

    assert classification.observation_state == state


def test_observation_state_is_normalized():
    classification = make_classification(
        observation_state=" observed ",
    )

    assert classification.observation_state == "OBSERVED"


def test_unknown_observation_state_is_rejected():
    with pytest.raises(ValueError):
        make_classification(
            observation_state="ESTIMATED",
        )


def test_unknown_failure_attribution_is_rejected():
    with pytest.raises(ValueError):
        make_classification(
            failure_attribution="shipping",
        )


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_non_observed_states_require_matching_unresolved_attribution(state):
    classification = make_classification(
        observation_state=state,
        failure_attribution=state.lower(),
    )

    assert classification.failure_attribution == state.lower()


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_non_observed_states_reject_specific_failure_attribution(state):
    with pytest.raises(ValueError):
        make_classification(
            observation_state=state,
            failure_attribution="printer",
        )


def test_observed_rejects_unresolved_attribution():
    with pytest.raises(ValueError):
        make_classification(
            observation_state="OBSERVED",
            failure_attribution="unresolved",
        )


def test_observed_rejects_not_observable_attribution():
    with pytest.raises(ValueError):
        make_classification(
            observation_state="OBSERVED",
            failure_attribution="not_observable",
        )


def test_contract_does_not_claim_failure_severity():
    classification = make_classification()

    assert not hasattr(classification, "failure_severity")
    assert not hasattr(classification, "severity_score")


def test_contract_does_not_claim_production_decision():
    classification = make_classification()

    assert not hasattr(classification, "production_decision")
    assert not hasattr(classification, "go_hold_reject")


def test_contract_does_not_claim_likeness_or_metric_accuracy():
    classification = make_classification()

    assert not hasattr(classification, "likeness_score")
    assert not hasattr(classification, "metric_accuracy")
    assert not hasattr(classification, "metric_score")


def test_contract_does_not_claim_repair_recommendation():
    classification = make_classification()

    assert not hasattr(classification, "repair_recommendation")
    assert not hasattr(classification, "repair_action")


def test_contract_does_not_claim_phase_9_authorization():
    classification = make_classification()

    assert not hasattr(classification, "phase_9_authorized")
