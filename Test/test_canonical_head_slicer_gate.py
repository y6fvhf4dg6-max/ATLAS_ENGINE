import dataclasses

import pytest

from CORE.atlas_canonical_head_slicer_gate import (
    AtlasCanonicalHeadSlicerGateObservation,
)


def make_observation(**overrides):
    values = dict(
        representation_id="portrait_relief_v1",
        representation_kind="relief",
        slicer_name="Bambu Studio",
        slicer_version="2.3.0",
        printer_model="Bambu Lab P2S",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        slice_attempt_state="ATTEMPTED",
        slice_completed=True,
        slicer_error_count=0,
        mesh_repair_count=0,
        support_enabled=False,
        artifact_provenance="phase8 item11.7 test fixture",
    )
    values.update(overrides)
    return AtlasCanonicalHeadSlicerGateObservation(**values)


def test_contract_is_frozen():
    observation = make_observation()

    with pytest.raises(dataclasses.FrozenInstanceError):
        observation.slice_completed = False


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
    observation = make_observation(
        representation_kind=kind,
    )

    assert observation.representation_kind == kind


def test_representation_kind_is_normalized():
    observation = make_observation(
        representation_kind=" Story Kit Component ",
    )

    assert observation.representation_kind == "story_kit_component"


@pytest.mark.parametrize(
    "field_name",
    (
        "representation_id",
        "slicer_name",
        "slicer_version",
        "printer_model",
        "artifact_provenance",
    ),
)
def test_required_text_fields_must_not_be_blank(field_name):
    with pytest.raises(ValueError):
        make_observation(**{field_name: "   "})


def test_unknown_representation_kind_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            representation_kind="mask",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "nozzle_diameter_mm",
        "layer_height_mm",
    ),
)
@pytest.mark.parametrize(
    "bad_value",
    (
        0.0,
        -0.1,
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_positive_finite_physical_values_required(
    field_name,
    bad_value,
):
    with pytest.raises(ValueError):
        make_observation(
            **{field_name: bad_value},
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "slicer_error_count",
        "mesh_repair_count",
    ),
)
@pytest.mark.parametrize(
    "bad_value",
    (
        -1,
        True,
        1.5,
        "1",
    ),
)
def test_count_fields_require_nonnegative_strict_integers(
    field_name,
    bad_value,
):
    with pytest.raises((TypeError, ValueError)):
        make_observation(
            **{field_name: bad_value},
        )


@pytest.mark.parametrize(
    "state",
    (
        "ATTEMPTED",
        "NOT_ATTEMPTED",
        "UNRESOLVED",
    ),
)
def test_supported_slice_attempt_states(state):
    if state == "ATTEMPTED":
        observation = make_observation(
            slice_attempt_state=state,
        )
    else:
        observation = make_observation(
            slice_attempt_state=state,
            slice_completed=None,
            slicer_error_count=None,
            mesh_repair_count=None,
            support_enabled=None,
        )

    assert observation.slice_attempt_state == state


def test_slice_attempt_state_is_normalized():
    observation = make_observation(
        slice_attempt_state=" not attempted ",
        slice_completed=None,
        slicer_error_count=None,
        mesh_repair_count=None,
        support_enabled=None,
    )

    assert observation.slice_attempt_state == "NOT_ATTEMPTED"


def test_unknown_slice_attempt_state_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            slice_attempt_state="QUEUED",
        )


def test_attempted_requires_slice_completed_boolean():
    with pytest.raises(ValueError):
        make_observation(
            slice_completed=None,
        )


@pytest.mark.parametrize(
    "bad_value",
    (
        1,
        0,
        "true",
    ),
)
def test_slice_completed_requires_strict_boolean(bad_value):
    with pytest.raises(TypeError):
        make_observation(
            slice_completed=bad_value,
        )


@pytest.mark.parametrize(
    "bad_value",
    (
        1,
        0,
        "false",
    ),
)
def test_support_enabled_requires_strict_boolean(bad_value):
    with pytest.raises(TypeError):
        make_observation(
            support_enabled=bad_value,
        )


def test_successful_slice_derives_passed():
    observation = make_observation()

    assert observation.slicer_gate_state == "PASSED"


def test_incomplete_slice_derives_failed():
    observation = make_observation(
        slice_completed=False,
    )

    assert observation.slicer_gate_state == "FAILED"


def test_slicer_error_derives_failed():
    observation = make_observation(
        slicer_error_count=1,
    )

    assert observation.slicer_gate_state == "FAILED"


def test_mesh_repair_does_not_replace_slice_completion():
    observation = make_observation(
        mesh_repair_count=2,
    )

    assert observation.slice_completed is True
    assert observation.slicer_gate_state == "PASSED"


def test_not_attempted_derives_unresolved():
    observation = make_observation(
        slice_attempt_state="NOT_ATTEMPTED",
        slice_completed=None,
        slicer_error_count=None,
        mesh_repair_count=None,
        support_enabled=None,
    )

    assert observation.slicer_gate_state == "UNRESOLVED"


def test_unresolved_derives_unresolved():
    observation = make_observation(
        slice_attempt_state="UNRESOLVED",
        slice_completed=None,
        slicer_error_count=None,
        mesh_repair_count=None,
        support_enabled=None,
    )

    assert observation.slicer_gate_state == "UNRESOLVED"


@pytest.mark.parametrize(
    "state",
    (
        "NOT_ATTEMPTED",
        "UNRESOLVED",
    ),
)
@pytest.mark.parametrize(
    "field_name,value",
    (
        ("slice_completed", False),
        ("slicer_error_count", 0),
        ("mesh_repair_count", 0),
        ("support_enabled", False),
    ),
)
def test_non_attempted_states_reject_observed_slice_results(
    state,
    field_name,
    value,
):
    overrides = dict(
        slice_attempt_state=state,
        slice_completed=None,
        slicer_error_count=None,
        mesh_repair_count=None,
        support_enabled=None,
    )
    overrides[field_name] = value

    with pytest.raises(ValueError):
        make_observation(**overrides)


def test_digital_or_structural_validity_is_not_part_of_contract():
    observation = make_observation()

    assert not hasattr(observation, "digital_mesh_valid")
    assert not hasattr(observation, "is_structurally_valid")
    assert not hasattr(observation, "topology_valid")


def test_contract_does_not_claim_production_or_phase_decision():
    observation = make_observation()

    assert not hasattr(observation, "production_decision")
    assert not hasattr(observation, "phase_9_authorized")
    assert not hasattr(observation, "physical_print_passed")
    assert not hasattr(observation, "identity_preservation_score")
