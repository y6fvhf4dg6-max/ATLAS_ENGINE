from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_relief_depth_transfer import (
    AtlasCanonicalHeadReliefDepthTransfer,
)


def _transfer(**overrides):
    values = {
        "representation_id": "person-a-relief-v1",
        "canonical_depth_mm": 24.0,
        "relief_depth_mm": 2.4,
        "measurement_state": "OBSERVED",
        "measurement_provenance": "synthetic metric fixture",
        "clipped": False,
        "local_identity_shape_loss_observed": False,
    }
    values.update(overrides)
    return AtlasCanonicalHeadReliefDepthTransfer(**values)


def test_records_observed_metric_depth_transfer():
    transfer = _transfer()

    assert transfer.representation_id == "person-a-relief-v1"
    assert transfer.canonical_depth_mm == pytest.approx(24.0)
    assert transfer.relief_depth_mm == pytest.approx(2.4)
    assert transfer.measurement_state == "OBSERVED"


def test_observed_transfer_derives_depth_transfer_ratio():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=5.0,
    )

    assert transfer.depth_transfer_ratio == pytest.approx(0.25)


def test_observed_compression_derives_compression_fraction():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=5.0,
    )

    assert transfer.compression_fraction == pytest.approx(0.75)


def test_observed_compressed_transfer_is_classified():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=5.0,
    )

    assert transfer.transfer_state == "COMPRESSED"


def test_zero_relief_depth_is_flattened():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=0.0,
    )

    assert transfer.depth_transfer_ratio == pytest.approx(0.0)
    assert transfer.compression_fraction == pytest.approx(1.0)
    assert transfer.transfer_state == "FLATTENED"


def test_exaggerated_depth_is_classified():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=25.0,
    )

    assert transfer.depth_transfer_ratio == pytest.approx(1.25)
    assert transfer.compression_fraction is None
    assert transfer.transfer_state == "EXAGGERATED"


def test_exact_metric_depth_preservation_is_classified_without_invented_tolerance():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=20.0,
    )

    assert transfer.depth_transfer_ratio == pytest.approx(1.0)
    assert transfer.compression_fraction == pytest.approx(0.0)
    assert transfer.transfer_state == "PRESERVED"


def test_near_equal_but_not_equal_depth_is_not_silently_called_preserved():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=19.999,
    )

    assert transfer.transfer_state == "COMPRESSED"


def test_unresolved_state_requires_missing_metric_depths():
    transfer = _transfer(
        canonical_depth_mm=None,
        relief_depth_mm=None,
        measurement_state="UNRESOLVED",
    )

    assert transfer.canonical_depth_mm is None
    assert transfer.relief_depth_mm is None
    assert transfer.depth_transfer_ratio is None
    assert transfer.compression_fraction is None
    assert transfer.transfer_state == "UNRESOLVED"


@pytest.mark.parametrize(
    ("canonical_depth_mm", "relief_depth_mm"),
    (
        (20.0, None),
        (None, 2.0),
        (20.0, 2.0),
    ),
)
def test_unresolved_state_rejects_partial_or_numeric_metric_depths(
    canonical_depth_mm,
    relief_depth_mm,
):
    with pytest.raises(ValueError, match="UNRESOLVED"):
        _transfer(
            canonical_depth_mm=canonical_depth_mm,
            relief_depth_mm=relief_depth_mm,
            measurement_state="UNRESOLVED",
        )


@pytest.mark.parametrize(
    ("canonical_depth_mm", "relief_depth_mm"),
    (
        (None, 2.0),
        (20.0, None),
    ),
)
def test_observed_state_requires_both_metric_depths(
    canonical_depth_mm,
    relief_depth_mm,
):
    with pytest.raises(ValueError, match="OBSERVED"):
        _transfer(
            canonical_depth_mm=canonical_depth_mm,
            relief_depth_mm=relief_depth_mm,
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
def test_canonical_depth_must_be_positive_finite_when_observed(value):
    with pytest.raises(ValueError, match="canonical_depth_mm"):
        _transfer(canonical_depth_mm=value)


@pytest.mark.parametrize(
    "value",
    (
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_relief_depth_must_be_nonnegative_finite_when_observed(value):
    with pytest.raises(ValueError, match="relief_depth_mm"):
        _transfer(relief_depth_mm=value)


def test_numeric_depth_inputs_are_coerced():
    transfer = _transfer(
        canonical_depth_mm="20.0",
        relief_depth_mm="5.0",
    )

    assert transfer.canonical_depth_mm == pytest.approx(20.0)
    assert transfer.relief_depth_mm == pytest.approx(5.0)


def test_measurement_state_is_normalized():
    transfer = _transfer(
        canonical_depth_mm=None,
        relief_depth_mm=None,
        measurement_state="  unresolved  ",
    )

    assert transfer.measurement_state == "UNRESOLVED"


def test_unknown_measurement_state_is_rejected():
    with pytest.raises(ValueError, match="measurement_state"):
        _transfer(measurement_state="ESTIMATED")


def test_requires_nonblank_representation_id():
    with pytest.raises(ValueError, match="representation_id"):
        _transfer(representation_id="   ")


def test_requires_measurement_provenance():
    with pytest.raises(ValueError, match="measurement_provenance"):
        _transfer(measurement_provenance="   ")


@pytest.mark.parametrize(
    "field_name",
    (
        "clipped",
        "local_identity_shape_loss_observed",
    ),
)
def test_audit_flags_require_boolean_values(field_name):
    with pytest.raises(TypeError, match=field_name):
        _transfer(**{field_name: 1})


def test_clipping_is_recorded_without_rewriting_transfer_ratio():
    transfer = _transfer(
        canonical_depth_mm=20.0,
        relief_depth_mm=5.0,
        clipped=True,
    )

    assert transfer.clipped is True
    assert transfer.depth_transfer_ratio == pytest.approx(0.25)
    assert transfer.transfer_state == "COMPRESSED"


def test_local_identity_shape_loss_is_recorded_as_observation_only():
    transfer = _transfer(
        local_identity_shape_loss_observed=True,
    )

    assert transfer.local_identity_shape_loss_observed is True


def test_contract_does_not_claim_likeness_or_phase_decision():
    transfer = _transfer()

    assert not hasattr(transfer, "likeness_score")
    assert not hasattr(transfer, "identity_preservation_support")
    assert not hasattr(transfer, "decision")
    assert not hasattr(transfer, "production_status")
    assert not hasattr(transfer, "phase_9_authorized")


def test_record_is_immutable():
    transfer = _transfer()

    with pytest.raises(FrozenInstanceError):
        transfer.relief_depth_mm = 3.0
