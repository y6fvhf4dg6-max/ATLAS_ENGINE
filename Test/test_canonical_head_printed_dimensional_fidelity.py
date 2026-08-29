import dataclasses
import math

import pytest

from CORE.atlas_canonical_head_printed_dimensional_fidelity import (
    AtlasCanonicalHeadPrintedDimensionalFidelity,
)


def make_observation(**overrides):
    values = dict(
        representation_id="portrait_relief_v1",
        representation_kind="relief",
        feature_name="head_height",
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=41.8,
        tolerance_mm=0.5,
        measurement_state="OBSERVED",
        measurement_provenance="digital caliper measurement",
    )
    values.update(overrides)
    return AtlasCanonicalHeadPrintedDimensionalFidelity(**values)


def test_contract_is_frozen():
    observation = make_observation()

    with pytest.raises(dataclasses.FrozenInstanceError):
        observation.tolerance_mm = 1.0


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
        "feature_name",
        "measurement_provenance",
    ),
)
def test_required_text_fields_must_not_be_blank(field_name):
    with pytest.raises(ValueError):
        make_observation(**{field_name: "   "})


@pytest.mark.parametrize(
    "field_name",
    (
        "intended_digital_dimension_mm",
        "tolerance_mm",
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
        None,
    ),
)
def test_required_positive_finite_values_reject_invalid(
    field_name,
    bad_value,
):
    with pytest.raises((TypeError, ValueError)):
        make_observation(**{field_name: bad_value})


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
def test_observed_printed_dimension_must_be_positive_finite(
    bad_value,
):
    with pytest.raises(ValueError):
        make_observation(
            measured_printed_dimension_mm=bad_value,
        )


def test_observed_requires_printed_measurement():
    with pytest.raises(ValueError):
        make_observation(
            measured_printed_dimension_mm=None,
        )


@pytest.mark.parametrize(
    "state",
    (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_MEASURABLE",
    ),
)
def test_supported_measurement_states(state):
    kwargs = {"measurement_state": state}

    if state != "OBSERVED":
        kwargs["measured_printed_dimension_mm"] = None

    observation = make_observation(**kwargs)

    assert observation.measurement_state == state


def test_measurement_state_is_normalized():
    observation = make_observation(
        measurement_state=" not measurable ",
        measured_printed_dimension_mm=None,
    )

    assert observation.measurement_state == "NOT_MEASURABLE"


def test_unknown_measurement_state_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            measurement_state="ESTIMATED",
        )


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_MEASURABLE",
    ),
)
def test_non_observed_states_reject_printed_measurement(state):
    with pytest.raises(ValueError):
        make_observation(
            measurement_state=state,
            measured_printed_dimension_mm=41.8,
        )


def test_absolute_error_is_derived():
    observation = make_observation(
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=41.8,
    )

    assert observation.absolute_error_mm == pytest.approx(0.2)


def test_relative_error_is_derived_from_digital_dimension():
    observation = make_observation(
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=41.8,
    )

    assert observation.relative_error == pytest.approx(
        0.2 / 42.0
    )


def test_equal_dimensions_have_zero_error():
    observation = make_observation(
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=42.0,
    )

    assert observation.absolute_error_mm == pytest.approx(0.0)
    assert observation.relative_error == pytest.approx(0.0)
    assert observation.fidelity_state == "WITHIN_TOLERANCE"


def test_error_equal_to_tolerance_is_within_tolerance():
    observation = make_observation(
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=41.5,
        tolerance_mm=0.5,
    )

    assert observation.absolute_error_mm == pytest.approx(0.5)
    assert observation.fidelity_state == "WITHIN_TOLERANCE"


def test_error_below_tolerance_is_within_tolerance():
    observation = make_observation(
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=41.7,
        tolerance_mm=0.5,
    )

    assert observation.fidelity_state == "WITHIN_TOLERANCE"


def test_error_above_tolerance_is_outside_tolerance():
    observation = make_observation(
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=41.4,
        tolerance_mm=0.5,
    )

    assert observation.fidelity_state == "OUTSIDE_TOLERANCE"


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_MEASURABLE",
    ),
)
def test_non_observed_states_do_not_fabricate_error_metrics(state):
    observation = make_observation(
        measurement_state=state,
        measured_printed_dimension_mm=None,
    )

    assert observation.absolute_error_mm is None
    assert observation.relative_error is None
    assert observation.fidelity_state == state


def test_printed_dimension_can_be_larger_than_digital():
    observation = make_observation(
        intended_digital_dimension_mm=42.0,
        measured_printed_dimension_mm=42.3,
        tolerance_mm=0.5,
    )

    assert observation.absolute_error_mm == pytest.approx(0.3)
    assert observation.fidelity_state == "WITHIN_TOLERANCE"


def test_contract_does_not_claim_identity_or_production_decision():
    observation = make_observation()

    assert not hasattr(observation, "identity_preservation_score")
    assert not hasattr(observation, "production_decision")
    assert not hasattr(observation, "phase_9_authorized")
    assert not hasattr(observation, "physical_regional_preservation")


def test_contract_does_not_treat_digital_dimension_as_print_measurement():
    observation = make_observation(
        measurement_state="UNRESOLVED",
        measured_printed_dimension_mm=None,
    )

    assert observation.intended_digital_dimension_mm == pytest.approx(42.0)
    assert observation.absolute_error_mm is None
    assert observation.fidelity_state == "UNRESOLVED"


@pytest.mark.parametrize(
    "value",
    (
        "42.0",
        42,
        42.0,
    ),
)
def test_numeric_digital_dimension_is_normalized_to_float(value):
    observation = make_observation(
        intended_digital_dimension_mm=value,
    )

    assert observation.intended_digital_dimension_mm == pytest.approx(42.0)
    assert isinstance(
        observation.intended_digital_dimension_mm,
        float,
    )


@pytest.mark.parametrize(
    "value",
    (
        "0.5",
        1,
        0.5,
    ),
)
def test_numeric_tolerance_is_normalized_to_float(value):
    observation = make_observation(
        tolerance_mm=value,
    )

    assert math.isfinite(observation.tolerance_mm)
    assert observation.tolerance_mm > 0.0
    assert isinstance(observation.tolerance_mm, float)
