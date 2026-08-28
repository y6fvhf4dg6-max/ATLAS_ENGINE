from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_physical_scale_class import (
    AtlasCanonicalHeadPhysicalScaleClass,
)


def _scale_class(**overrides):
    values = {
        "representation_id": "person-a-relief-v1",
        "representation_kind": "relief",
        "head_width_mm": 34.0,
        "head_height_mm": 42.0,
        "head_depth_mm": 18.0,
        "output_width_mm": 80.0,
        "output_height_mm": 100.0,
        "output_depth_mm": 4.0,
        "physical_unit": "mm",
        "measurement_provenance": "mesh_bounds:person-a-relief-v1",
        "head_width_state": "OBSERVED",
        "head_height_state": "OBSERVED",
        "head_depth_state": "OBSERVED",
        "output_width_state": "OBSERVED",
        "output_height_state": "OBSERVED",
        "output_depth_state": "OBSERVED",
    }
    values.update(overrides)
    return AtlasCanonicalHeadPhysicalScaleClass(**values)


@pytest.mark.parametrize(
    "representation_kind",
    (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    ),
)
def test_accepts_required_representation_kinds(representation_kind):
    scale_class = _scale_class(
        representation_kind=representation_kind,
    )

    assert scale_class.representation_kind == representation_kind


def test_rejects_unknown_representation_kind():
    with pytest.raises(
        ValueError,
        match="representation_kind",
    ):
        _scale_class(
            representation_kind="generic_mesh",
        )


def test_normalizes_representation_id_and_kind():
    scale_class = _scale_class(
        representation_id="  Person A Relief V1  ",
        representation_kind="  RELIEF  ",
    )

    assert scale_class.representation_id == "Person A Relief V1"
    assert scale_class.representation_kind == "relief"


@pytest.mark.parametrize(
    "field_name",
    (
        "head_width_mm",
        "head_height_mm",
        "head_depth_mm",
        "output_width_mm",
        "output_height_mm",
        "output_depth_mm",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -0.01,
        float("inf"),
        float("-inf"),
        float("nan"),
    ),
)
def test_dimensions_must_be_finite_and_positive(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _scale_class(
            **{field_name: value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "head_width_mm",
        "head_height_mm",
        "head_depth_mm",
        "output_width_mm",
        "output_height_mm",
        "output_depth_mm",
    ),
)
def test_dimensions_are_normalized_to_float(field_name):
    scale_class = _scale_class(
        **{field_name: 12}
    )

    assert getattr(scale_class, field_name) == 12.0
    assert isinstance(
        getattr(scale_class, field_name),
        float,
    )


def test_physical_unit_is_locked_to_mm():
    scale_class = _scale_class()

    assert scale_class.physical_unit == "mm"


@pytest.mark.parametrize(
    "physical_unit",
    (
        "",
        "cm",
        "m",
        "unitless",
    ),
)
def test_rejects_non_mm_physical_unit(physical_unit):
    with pytest.raises(
        ValueError,
        match="physical_unit",
    ):
        _scale_class(
            physical_unit=physical_unit,
        )


def test_measurement_provenance_is_required():
    with pytest.raises(
        ValueError,
        match="measurement_provenance",
    ):
        _scale_class(
            measurement_provenance="   ",
        )


def test_representation_id_is_required():
    with pytest.raises(
        ValueError,
        match="representation_id",
    ):
        _scale_class(
            representation_id="",
        )


@pytest.mark.parametrize(
    "state",
    (
        "OBSERVED",
        "NOT_APPLICABLE",
        "UNRESOLVED",
    ),
)
def test_accepts_dimension_measurement_states(state):
    scale_class = _scale_class(
        head_depth_mm=(
            18.0
            if state == "OBSERVED"
            else None
        ),
        head_depth_state=state,
    )

    assert scale_class.head_depth_state == state


@pytest.mark.parametrize(
    "field_name",
    (
        "head_width_state",
        "head_height_state",
        "head_depth_state",
        "output_width_state",
        "output_height_state",
        "output_depth_state",
    ),
)
def test_rejects_unknown_dimension_measurement_state(field_name):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _scale_class(
            **{field_name: "ASSUMED"}
        )


def test_dimension_states_are_normalized():
    scale_class = _scale_class(
        head_depth_mm=None,
        head_depth_state="  not applicable  ",
        output_depth_mm=None,
        output_depth_state=" unresolved ",
    )

    assert scale_class.head_depth_state == "NOT_APPLICABLE"
    assert scale_class.output_depth_state == "UNRESOLVED"


def test_contract_records_actual_dimensions_not_target_dimensions():
    scale_class = _scale_class()

    assert scale_class.head_height_mm == 42.0

    for forbidden in (
        "target_head_height_mm",
        "target_output_width_mm",
        "target_output_height_mm",
        "target_output_depth_mm",
    ):
        assert not hasattr(
            scale_class,
            forbidden,
        )


def test_output_dimensions_and_head_dimensions_remain_distinct():
    scale_class = _scale_class(
        head_width_mm=34.0,
        head_height_mm=42.0,
        head_depth_mm=18.0,
        output_width_mm=80.0,
        output_height_mm=100.0,
        output_depth_mm=4.0,
    )

    assert (
        scale_class.head_width_mm,
        scale_class.head_height_mm,
        scale_class.head_depth_mm,
    ) == (
        34.0,
        42.0,
        18.0,
    )

    assert (
        scale_class.output_width_mm,
        scale_class.output_height_mm,
        scale_class.output_depth_mm,
    ) == (
        80.0,
        100.0,
        4.0,
    )


def test_contract_is_immutable():
    scale_class = _scale_class()

    with pytest.raises(FrozenInstanceError):
        scale_class.head_height_mm = 50.0


def test_contract_does_not_invent_named_size_bands_or_gate_decisions():
    scale_class = _scale_class()

    for forbidden in (
        "scale_class_name",
        "size_band",
        "small",
        "medium",
        "large",
        "decision",
        "production_status",
        "support_score",
        "likeness_score",
        "phase_9_authorized",
    ):
        assert not hasattr(
            scale_class,
            forbidden,
        )


@pytest.mark.parametrize(
    ("dimension_field", "state_field", "state"),
    (
        ("head_width_mm", "head_width_state", "UNRESOLVED"),
        ("head_width_mm", "head_width_state", "NOT_APPLICABLE"),
        ("head_height_mm", "head_height_state", "UNRESOLVED"),
        ("head_height_mm", "head_height_state", "NOT_APPLICABLE"),
        ("head_depth_mm", "head_depth_state", "UNRESOLVED"),
        ("head_depth_mm", "head_depth_state", "NOT_APPLICABLE"),
        ("output_width_mm", "output_width_state", "UNRESOLVED"),
        ("output_width_mm", "output_width_state", "NOT_APPLICABLE"),
        ("output_height_mm", "output_height_state", "UNRESOLVED"),
        ("output_height_mm", "output_height_state", "NOT_APPLICABLE"),
        ("output_depth_mm", "output_depth_state", "UNRESOLVED"),
        ("output_depth_mm", "output_depth_state", "NOT_APPLICABLE"),
    ),
)
def test_non_observed_dimension_state_accepts_missing_measurement(
    dimension_field,
    state_field,
    state,
):
    scale_class = _scale_class(
        **{
            dimension_field: None,
            state_field: state,
        }
    )

    assert getattr(scale_class, dimension_field) is None
    assert getattr(scale_class, state_field) == state


@pytest.mark.parametrize(
    ("dimension_field", "state_field"),
    (
        ("head_width_mm", "head_width_state"),
        ("head_height_mm", "head_height_state"),
        ("head_depth_mm", "head_depth_state"),
        ("output_width_mm", "output_width_state"),
        ("output_height_mm", "output_height_state"),
        ("output_depth_mm", "output_depth_state"),
    ),
)
def test_observed_dimension_requires_numeric_measurement(
    dimension_field,
    state_field,
):
    with pytest.raises(
        (TypeError, ValueError),
        match=dimension_field,
    ):
        _scale_class(
            **{
                dimension_field: None,
                state_field: "OBSERVED",
            }
        )


@pytest.mark.parametrize(
    ("dimension_field", "state_field", "state"),
    (
        ("head_depth_mm", "head_depth_state", "UNRESOLVED"),
        ("head_depth_mm", "head_depth_state", "NOT_APPLICABLE"),
        ("output_depth_mm", "output_depth_state", "UNRESOLVED"),
        ("output_depth_mm", "output_depth_state", "NOT_APPLICABLE"),
    ),
)
def test_non_observed_dimension_does_not_require_fabricated_positive_value(
    dimension_field,
    state_field,
    state,
):
    scale_class = _scale_class(
        **{
            dimension_field: None,
            state_field: state,
        }
    )

    assert getattr(scale_class, dimension_field) is None


@pytest.mark.parametrize(
    ("dimension_field", "state_field"),
    (
        ("head_width_mm", "head_width_state"),
        ("head_height_mm", "head_height_state"),
        ("head_depth_mm", "head_depth_state"),
        ("output_width_mm", "output_width_state"),
        ("output_height_mm", "output_height_state"),
        ("output_depth_mm", "output_depth_state"),
    ),
)
@pytest.mark.parametrize(
    "state",
    (
        "UNRESOLVED",
        "NOT_APPLICABLE",
    ),
)
def test_non_observed_dimension_state_rejects_numeric_measurement(
    dimension_field,
    state_field,
    state,
):
    with pytest.raises(
        ValueError,
        match=dimension_field,
    ):
        _scale_class(
            **{
                dimension_field: 12.0,
                state_field: state,
            }
        )
