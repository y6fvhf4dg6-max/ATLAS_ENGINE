import dataclasses

import pytest

from CORE.atlas_canonical_head_topology_manufacturability import (
    AtlasCanonicalHeadTopologyManufacturability,
)


def make_observation(**overrides):
    values = dict(
        representation_id="portrait_relief_v1",
        representation_kind="relief",
        open_edge_count=0,
        non_manifold_edge_count=0,
        self_intersection_count=0,
        degenerate_geometry_count=0,
        minimum_observed_thickness_mm=0.80,
        minimum_required_thickness_mm=0.60,
        unsupported_structure_count=0,
        unintended_disconnected_component_count=0,
        measurement_state="OBSERVED",
        measurement_provenance="phase8 item11.6 test fixture",
    )
    values.update(overrides)
    return AtlasCanonicalHeadTopologyManufacturability(**values)


def test_contract_is_frozen():
    observation = make_observation()

    with pytest.raises(dataclasses.FrozenInstanceError):
        observation.open_edge_count = 1


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
        representation_kind="  Figurine Head  ",
    )

    assert observation.representation_kind == "figurine_head"


@pytest.mark.parametrize(
    "field_name",
    (
        "representation_id",
        "measurement_provenance",
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


def test_observed_clean_mesh_derives_satisfied_states():
    observation = make_observation()

    assert observation.closed_manifold_state == "SATISFIED"
    assert observation.self_intersection_state == "SATISFIED"
    assert observation.degenerate_geometry_state == "SATISFIED"
    assert observation.thickness_state == "SATISFIED"
    assert observation.unsupported_structure_state == "SATISFIED"
    assert observation.disconnected_geometry_state == "SATISFIED"
    assert observation.manufacturability_state == "SATISFIED"


def test_open_edge_violation_is_derived():
    observation = make_observation(
        open_edge_count=2,
    )

    assert observation.closed_manifold_state == "VIOLATED"
    assert observation.manufacturability_state == "VIOLATED"


def test_non_manifold_violation_is_derived():
    observation = make_observation(
        non_manifold_edge_count=1,
    )

    assert observation.closed_manifold_state == "VIOLATED"
    assert observation.manufacturability_state == "VIOLATED"


def test_self_intersection_violation_is_derived():
    observation = make_observation(
        self_intersection_count=3,
    )

    assert observation.self_intersection_state == "VIOLATED"
    assert observation.manufacturability_state == "VIOLATED"


def test_degenerate_geometry_violation_is_derived():
    observation = make_observation(
        degenerate_geometry_count=4,
    )

    assert observation.degenerate_geometry_state == "VIOLATED"
    assert observation.manufacturability_state == "VIOLATED"


def test_thickness_equal_to_requirement_is_satisfied():
    observation = make_observation(
        minimum_observed_thickness_mm=0.60,
        minimum_required_thickness_mm=0.60,
    )

    assert observation.thickness_state == "SATISFIED"


def test_thickness_below_requirement_is_violated():
    observation = make_observation(
        minimum_observed_thickness_mm=0.59,
        minimum_required_thickness_mm=0.60,
    )

    assert observation.thickness_state == "VIOLATED"
    assert observation.manufacturability_state == "VIOLATED"


def test_unsupported_structure_violation_is_derived():
    observation = make_observation(
        unsupported_structure_count=1,
    )

    assert observation.unsupported_structure_state == "VIOLATED"
    assert observation.manufacturability_state == "VIOLATED"


def test_unintended_disconnected_geometry_violation_is_derived():
    observation = make_observation(
        unintended_disconnected_component_count=2,
    )

    assert observation.disconnected_geometry_state == "VIOLATED"
    assert observation.manufacturability_state == "VIOLATED"


@pytest.mark.parametrize(
    "field_name",
    (
        "open_edge_count",
        "non_manifold_edge_count",
        "self_intersection_count",
        "degenerate_geometry_count",
        "unsupported_structure_count",
        "unintended_disconnected_component_count",
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
    "field_name",
    (
        "minimum_observed_thickness_mm",
        "minimum_required_thickness_mm",
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
def test_thickness_fields_require_positive_finite_values(
    field_name,
    bad_value,
):
    with pytest.raises(ValueError):
        make_observation(
            **{field_name: bad_value},
        )


@pytest.mark.parametrize(
    "state",
    (
        "OBSERVED",
        "UNRESOLVED",
    ),
)
def test_supported_measurement_states(state):
    if state == "OBSERVED":
        observation = make_observation(
            measurement_state=state,
        )
    else:
        observation = make_observation(
            open_edge_count=None,
            non_manifold_edge_count=None,
            self_intersection_count=None,
            degenerate_geometry_count=None,
            minimum_observed_thickness_mm=None,
            minimum_required_thickness_mm=None,
            unsupported_structure_count=None,
            unintended_disconnected_component_count=None,
            measurement_state=state,
        )

    assert observation.measurement_state == state


def test_measurement_state_is_normalized():
    observation = make_observation(
        measurement_state=" unresolved ",
        open_edge_count=None,
        non_manifold_edge_count=None,
        self_intersection_count=None,
        degenerate_geometry_count=None,
        minimum_observed_thickness_mm=None,
        minimum_required_thickness_mm=None,
        unsupported_structure_count=None,
        unintended_disconnected_component_count=None,
    )

    assert observation.measurement_state == "UNRESOLVED"


def test_unknown_measurement_state_is_rejected():
    with pytest.raises(ValueError):
        make_observation(
            measurement_state="ESTIMATED",
        )


def test_unresolved_requires_all_measurements_absent():
    with pytest.raises(ValueError):
        make_observation(
            measurement_state="UNRESOLVED",
            open_edge_count=0,
            non_manifold_edge_count=None,
            self_intersection_count=None,
            degenerate_geometry_count=None,
            minimum_observed_thickness_mm=None,
            minimum_required_thickness_mm=None,
            unsupported_structure_count=None,
            unintended_disconnected_component_count=None,
        )


def test_observed_requires_all_measurements_present():
    with pytest.raises(ValueError):
        make_observation(
            minimum_observed_thickness_mm=None,
        )


def test_unresolved_derives_unresolved_states():
    observation = make_observation(
        open_edge_count=None,
        non_manifold_edge_count=None,
        self_intersection_count=None,
        degenerate_geometry_count=None,
        minimum_observed_thickness_mm=None,
        minimum_required_thickness_mm=None,
        unsupported_structure_count=None,
        unintended_disconnected_component_count=None,
        measurement_state="UNRESOLVED",
    )

    assert observation.closed_manifold_state == "UNRESOLVED"
    assert observation.self_intersection_state == "UNRESOLVED"
    assert observation.degenerate_geometry_state == "UNRESOLVED"
    assert observation.thickness_state == "UNRESOLVED"
    assert observation.unsupported_structure_state == "UNRESOLVED"
    assert observation.disconnected_geometry_state == "UNRESOLVED"
    assert observation.manufacturability_state == "UNRESOLVED"


def test_contract_does_not_claim_slicer_validity_or_phase_decision():
    observation = make_observation()

    assert not hasattr(observation, "slicer_valid")
    assert not hasattr(observation, "production_decision")
    assert not hasattr(observation, "phase_9_authorized")
    assert not hasattr(observation, "identity_preservation_score")
