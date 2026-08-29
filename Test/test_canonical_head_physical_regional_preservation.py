import dataclasses

import pytest

from CORE.atlas_canonical_head_physical_regional_preservation import (
    AtlasCanonicalHeadPhysicalRegionalPreservation,
)


def make_observation(**overrides):
    values = dict(
        representation_id="portrait_relief_v1",
        representation_kind="relief",
        region_name="nose",
        observation_state="OBSERVED",
        digital_reference="canonical nose geometry",
        physical_reference="printed nose geometry",
        observation_provenance="controlled physical inspection",
        preservation_state="PRESERVED",
    )
    values.update(overrides)
    return AtlasCanonicalHeadPhysicalRegionalPreservation(**values)


def test_contract_is_frozen():
    observation = make_observation()

    with pytest.raises(dataclasses.FrozenInstanceError):
        observation.region_name = "jaw_chin"


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
def test_supported_regions(region):
    observation = make_observation(
        region_name=region,
    )

    assert observation.region_name == region


def test_region_name_is_normalized():
    observation = make_observation(
        region_name=" Jaw Chin ",
    )

    assert observation.region_name == "jaw_chin"


def test_unknown_region_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            region_name="hair",
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
    kwargs = {"observation_state": state}

    if state != "OBSERVED":
        kwargs.update(
            digital_reference=None,
            physical_reference=None,
            preservation_state=state,
        )

    observation = make_observation(**kwargs)

    assert observation.observation_state == state


def test_observation_state_is_normalized():
    observation = make_observation(
        observation_state=" not observable ",
        digital_reference=None,
        physical_reference=None,
        preservation_state="not observable",
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
        "PRESERVED",
        "DEGRADED",
        "LOST",
    ),
)
def test_observed_supports_physical_preservation_states(state):
    observation = make_observation(
        preservation_state=state,
    )

    assert observation.preservation_state == state


def test_preservation_state_is_normalized():
    observation = make_observation(
        preservation_state=" degraded ",
    )

    assert observation.preservation_state == "DEGRADED"


def test_unknown_preservation_state_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            preservation_state="IMPROVED",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "representation_id",
        "observation_provenance",
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
        "digital_reference",
        "physical_reference",
    ),
)
def test_observed_requires_nonblank_references(field_name):
    with pytest.raises(ValueError):
        make_observation(
            **{field_name: "   "}
        )


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_non_observed_states_require_no_references(state):
    observation = make_observation(
        observation_state=state,
        digital_reference=None,
        physical_reference=None,
        preservation_state=state,
    )

    assert observation.digital_reference is None
    assert observation.physical_reference is None


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
@pytest.mark.parametrize(
    "field_name",
    (
        "digital_reference",
        "physical_reference",
    ),
)
def test_non_observed_states_reject_references(
    state,
    field_name,
):
    kwargs = dict(
        observation_state=state,
        digital_reference=None,
        physical_reference=None,
        preservation_state=state,
    )
    kwargs[field_name] = "fabricated evidence"

    with pytest.raises(ValueError):
        make_observation(**kwargs)


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_non_observed_preservation_state_must_match_observation_state(
    state,
):
    with pytest.raises(ValueError):
        make_observation(
            observation_state=state,
            digital_reference=None,
            physical_reference=None,
            preservation_state="PRESERVED",
        )


@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    ),
)
def test_observed_rejects_non_observed_preservation_states(state):
    with pytest.raises(ValueError):
        make_observation(
            observation_state="OBSERVED",
            preservation_state=state,
        )


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


def test_contract_does_not_claim_dimensional_fidelity():
    observation = make_observation()

    assert not hasattr(
        observation,
        "absolute_error_mm",
    )
    assert not hasattr(
        observation,
        "fidelity_state",
    )
