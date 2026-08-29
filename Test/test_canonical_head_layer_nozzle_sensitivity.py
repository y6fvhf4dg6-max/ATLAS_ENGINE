import dataclasses
import math

import pytest

from CORE.atlas_canonical_head_layer_nozzle_sensitivity import (
    AtlasCanonicalHeadLayerNozzleSensitivity,
)


def make_observation(**overrides):
    values = dict(
        representation_id="portrait_relief_v1",
        representation_kind="relief",
        reference_nozzle_diameter_mm=0.4,
        reference_layer_height_mm=0.2,
        evaluated_nozzle_diameter_mm=0.6,
        evaluated_layer_height_mm=0.3,
        observation_state="OBSERVED",
        evidence_provenance="controlled manufacturing profile comparison",
        affected_regions=(),
        sensitivity_state="NO_MATERIAL_CHANGE",
    )
    values.update(overrides)
    return AtlasCanonicalHeadLayerNozzleSensitivity(**values)


def test_contract_is_frozen():
    observation = make_observation()

    with pytest.raises(dataclasses.FrozenInstanceError):
        observation.evaluated_nozzle_diameter_mm = 0.8


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
        "evidence_provenance",
    ),
)
def test_required_text_fields_reject_blank(field_name):
    with pytest.raises(ValueError):
        make_observation(
            **{field_name: "   "}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "reference_nozzle_diameter_mm",
        "reference_layer_height_mm",
        "evaluated_nozzle_diameter_mm",
        "evaluated_layer_height_mm",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -0.1,
        math.nan,
        math.inf,
        -math.inf,
    ),
)
def test_profile_dimensions_require_positive_finite_values(
    field_name,
    value,
):
    with pytest.raises((TypeError, ValueError)):
        make_observation(
            **{field_name: value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "reference_nozzle_diameter_mm",
        "reference_layer_height_mm",
        "evaluated_nozzle_diameter_mm",
        "evaluated_layer_height_mm",
    ),
)
def test_profile_dimensions_reject_non_numeric_values(field_name):
    with pytest.raises((TypeError, ValueError)):
        make_observation(
            **{field_name: "not-a-number"}
        )


def test_profile_dimensions_are_normalized_to_float():
    observation = make_observation(
        reference_nozzle_diameter_mm="0.4",
        reference_layer_height_mm="0.2",
        evaluated_nozzle_diameter_mm="0.6",
        evaluated_layer_height_mm="0.3",
    )

    assert observation.reference_nozzle_diameter_mm == pytest.approx(0.4)
    assert observation.reference_layer_height_mm == pytest.approx(0.2)
    assert observation.evaluated_nozzle_diameter_mm == pytest.approx(0.6)
    assert observation.evaluated_layer_height_mm == pytest.approx(0.3)


@pytest.mark.parametrize(
    "state",
    (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_supported_observation_states(state):
    kwargs = {"observation_state": state}

    if state != "OBSERVED":
        kwargs.update(
            affected_regions=(),
            sensitivity_state=state,
        )

    observation = make_observation(**kwargs)

    assert observation.observation_state == state


def test_observation_state_is_normalized():
    observation = make_observation(
        observation_state=" not observable ",
        sensitivity_state="not observable",
        affected_regions=(),
    )

    assert observation.observation_state == "NOT_OBSERVABLE"


def test_unknown_observation_state_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            observation_state="ESTIMATED",
        )


@pytest.mark.parametrize(
    "state",
    (
        "NO_MATERIAL_CHANGE",
        "MATERIAL_CHANGE",
    ),
)
def test_observed_supports_material_sensitivity_states(state):
    observation = make_observation(
        sensitivity_state=state,
        affected_regions=(
            ("nose",)
            if state == "MATERIAL_CHANGE"
            else ()
        ),
    )

    assert observation.sensitivity_state == state


def test_sensitivity_state_is_normalized():
    observation = make_observation(
        sensitivity_state=" material change ",
        affected_regions=("nose",),
    )

    assert observation.sensitivity_state == "MATERIAL_CHANGE"


def test_unknown_sensitivity_state_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            sensitivity_state="MINOR_CHANGE",
        )


@pytest.mark.parametrize(
    "region",
    (
        "nose",
        "jaw_chin",
        "orbital",
        "cheek_midface",
        "mouth_perioral",
        "forehead_cranial",
        "silhouette",
        "profile",
    ),
)
def test_supported_affected_regions(region):
    observation = make_observation(
        affected_regions=(region,),
        sensitivity_state="MATERIAL_CHANGE",
    )

    assert observation.affected_regions == (region,)


def test_affected_regions_are_normalized_and_deduplicated():
    observation = make_observation(
        affected_regions=(
            " Nose ",
            "profile",
            "nose",
        ),
        sensitivity_state="MATERIAL_CHANGE",
    )

    assert observation.affected_regions == (
        "nose",
        "profile",
    )


def test_unknown_affected_region_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            affected_regions=("hair",),
            sensitivity_state="MATERIAL_CHANGE",
        )


def test_no_material_change_requires_no_affected_regions():
    observation = make_observation(
        sensitivity_state="NO_MATERIAL_CHANGE",
        affected_regions=(),
    )

    assert observation.affected_regions == ()


def test_no_material_change_rejects_affected_regions():
    with pytest.raises(ValueError):
        make_observation(
            sensitivity_state="NO_MATERIAL_CHANGE",
            affected_regions=("nose",),
        )


def test_material_change_requires_affected_regions():
    with pytest.raises(ValueError):
        make_observation(
            sensitivity_state="MATERIAL_CHANGE",
            affected_regions=(),
        )


def test_material_change_accepts_affected_regions():
    observation = make_observation(
        sensitivity_state="MATERIAL_CHANGE",
        affected_regions=("nose", "profile"),
    )

    assert observation.affected_regions == (
        "nose",
        "profile",
    )


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_non_observed_states_require_matching_sensitivity_state(state):
    observation = make_observation(
        observation_state=state,
        sensitivity_state=state,
        affected_regions=(),
    )

    assert observation.sensitivity_state == state


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_non_observed_states_reject_material_claims(state):
    with pytest.raises(ValueError):
        make_observation(
            observation_state=state,
            sensitivity_state="MATERIAL_CHANGE",
            affected_regions=("nose",),
        )


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_non_observed_states_reject_affected_regions(state):
    with pytest.raises(ValueError):
        make_observation(
            observation_state=state,
            sensitivity_state=state,
            affected_regions=("nose",),
        )


def test_observed_rejects_unresolved_sensitivity_state():
    with pytest.raises(ValueError):
        make_observation(
            observation_state="OBSERVED",
            sensitivity_state="UNRESOLVED",
            affected_regions=(),
        )


def test_contract_does_not_claim_material():
    observation = make_observation()

    assert not hasattr(observation, "material")
    assert not hasattr(observation, "material_profile")


def test_contract_does_not_claim_slicer_gate():
    observation = make_observation()

    assert not hasattr(observation, "slicer_gate_state")
    assert not hasattr(observation, "slice_completed")


def test_contract_does_not_claim_identity_score():
    observation = make_observation()

    assert not hasattr(
        observation,
        "identity_preservation_score",
    )


def test_contract_does_not_claim_production_decision():
    observation = make_observation()

    assert not hasattr(
        observation,
        "production_decision",
    )
    assert not hasattr(
        observation,
        "phase_9_authorized",
    )
