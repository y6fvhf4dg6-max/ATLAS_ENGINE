from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_lod_identity_preservation import (
    AtlasCanonicalHeadLoDIdentityPreservation,
)


def _observation(**overrides):
    values = {
        "representation_id": "person-a-relief-v1",
        "source_lod_level": 4,
        "target_lod_level": 2,
        "region_name": "nose",
        "pre_lod_measurement": 1.0,
        "post_lod_measurement": 0.8,
        "measurement_state": "OBSERVED",
        "measurement_provenance": "synthetic lod fixture",
    }
    values.update(overrides)
    return AtlasCanonicalHeadLoDIdentityPreservation(**values)


@pytest.mark.parametrize(
    "region_name",
    (
        "silhouette",
        "profile",
        "nose",
        "jaw_chin",
        "orbital_cheek",
        "mouth",
    ),
)
def test_accepts_required_identity_regions(region_name):
    observation = _observation(region_name=region_name)

    assert observation.region_name == region_name


def test_rejects_unknown_region():
    with pytest.raises(ValueError, match="region_name"):
        _observation(region_name="forehead")


def test_requires_actual_lod_reduction():
    with pytest.raises(ValueError, match="target_lod_level"):
        _observation(
            source_lod_level=2,
            target_lod_level=2,
        )


def test_rejects_target_lod_above_source():
    with pytest.raises(ValueError, match="target_lod_level"):
        _observation(
            source_lod_level=2,
            target_lod_level=3,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "source_lod_level",
        "target_lod_level",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        -1,
        5,
        True,
        1.5,
        "2",
    ),
)
def test_lod_levels_must_be_integers_in_zero_to_four(
    field_name,
    value,
):
    with pytest.raises((TypeError, ValueError), match=field_name):
        _observation(**{field_name: value})


def test_observed_preservation_ratio_is_derived():
    observation = _observation(
        pre_lod_measurement=2.0,
        post_lod_measurement=1.5,
    )

    assert observation.preservation_ratio == pytest.approx(0.75)


def test_observed_loss_fraction_is_derived():
    observation = _observation(
        pre_lod_measurement=2.0,
        post_lod_measurement=1.5,
    )

    assert observation.loss_fraction == pytest.approx(0.25)


def test_equal_measurement_is_preserved():
    observation = _observation(
        pre_lod_measurement=2.0,
        post_lod_measurement=2.0,
    )

    assert observation.preservation_state == "PRESERVED"
    assert observation.loss_fraction == pytest.approx(0.0)


def test_reduced_measurement_is_degraded():
    observation = _observation(
        pre_lod_measurement=2.0,
        post_lod_measurement=1.0,
    )

    assert observation.preservation_state == "DEGRADED"


def test_zero_post_lod_measurement_is_lost():
    observation = _observation(
        pre_lod_measurement=2.0,
        post_lod_measurement=0.0,
    )

    assert observation.preservation_ratio == pytest.approx(0.0)
    assert observation.loss_fraction == pytest.approx(1.0)
    assert observation.preservation_state == "LOST"


def test_larger_post_lod_measurement_is_exaggerated():
    observation = _observation(
        pre_lod_measurement=2.0,
        post_lod_measurement=2.5,
    )

    assert observation.preservation_ratio == pytest.approx(1.25)
    assert observation.loss_fraction is None
    assert observation.preservation_state == "EXAGGERATED"


def test_near_equal_but_lower_measurement_is_not_silently_preserved():
    observation = _observation(
        pre_lod_measurement=2.0,
        post_lod_measurement=1.999,
    )

    assert observation.preservation_state == "DEGRADED"


def test_unresolved_state_requires_missing_measurements():
    observation = _observation(
        pre_lod_measurement=None,
        post_lod_measurement=None,
        measurement_state="UNRESOLVED",
    )

    assert observation.pre_lod_measurement is None
    assert observation.post_lod_measurement is None
    assert observation.preservation_ratio is None
    assert observation.loss_fraction is None
    assert observation.preservation_state == "UNRESOLVED"


@pytest.mark.parametrize(
    ("pre_lod_measurement", "post_lod_measurement"),
    (
        (1.0, None),
        (None, 0.5),
        (1.0, 0.5),
    ),
)
def test_unresolved_state_rejects_partial_or_numeric_measurements(
    pre_lod_measurement,
    post_lod_measurement,
):
    with pytest.raises(ValueError, match="UNRESOLVED"):
        _observation(
            pre_lod_measurement=pre_lod_measurement,
            post_lod_measurement=post_lod_measurement,
            measurement_state="UNRESOLVED",
        )


@pytest.mark.parametrize(
    ("pre_lod_measurement", "post_lod_measurement"),
    (
        (None, 0.5),
        (1.0, None),
    ),
)
def test_observed_state_requires_both_measurements(
    pre_lod_measurement,
    post_lod_measurement,
):
    with pytest.raises(ValueError, match="OBSERVED"):
        _observation(
            pre_lod_measurement=pre_lod_measurement,
            post_lod_measurement=post_lod_measurement,
            measurement_state="OBSERVED",
        )


@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_pre_lod_measurement_must_be_positive_finite(value):
    with pytest.raises(ValueError, match="pre_lod_measurement"):
        _observation(pre_lod_measurement=value)


@pytest.mark.parametrize(
    "value",
    (
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_post_lod_measurement_must_be_nonnegative_finite(value):
    with pytest.raises(ValueError, match="post_lod_measurement"):
        _observation(post_lod_measurement=value)


def test_numeric_measurements_are_coerced():
    observation = _observation(
        pre_lod_measurement="2.0",
        post_lod_measurement="1.0",
    )

    assert observation.pre_lod_measurement == pytest.approx(2.0)
    assert observation.post_lod_measurement == pytest.approx(1.0)


def test_measurement_state_is_normalized():
    observation = _observation(
        pre_lod_measurement=None,
        post_lod_measurement=None,
        measurement_state="  unresolved  ",
    )

    assert observation.measurement_state == "UNRESOLVED"


def test_unknown_measurement_state_is_rejected():
    with pytest.raises(ValueError, match="measurement_state"):
        _observation(measurement_state="ESTIMATED")


def test_requires_nonblank_representation_id():
    with pytest.raises(ValueError, match="representation_id"):
        _observation(representation_id="   ")


def test_requires_measurement_provenance():
    with pytest.raises(ValueError, match="measurement_provenance"):
        _observation(measurement_provenance="   ")


def test_contract_does_not_claim_printability_or_phase_decision():
    observation = _observation()

    assert not hasattr(observation, "printability")
    assert not hasattr(observation, "decision")
    assert not hasattr(observation, "production_status")
    assert not hasattr(observation, "phase_9_authorized")


def test_record_is_immutable():
    observation = _observation()

    with pytest.raises(FrozenInstanceError):
        observation.post_lod_measurement = 0.5
