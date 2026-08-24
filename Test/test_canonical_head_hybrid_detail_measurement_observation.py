from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_hybrid_detail_measurement_observation import (
    AtlasCanonicalHeadHybridDetailMeasurementObservation,
)


def _measurement(**overrides):
    values = {
        "measurement_id": "subject-01-front-hybrid-detail",
        "source_view_id": "subject_01_front",
        "image_reference_span_px": 322.499195,
        "canonical_reference_span": 0.163734844,
        "scale_factor": 0.000507706211,
        "mapped_vertex_count": 264,
        "active_vertex_count": 264,
        "clipped_vertex_count": 0,
        "maximum_absolute_amplitude": 0.00163734844,
        "raw_absolute_max": 0.000500000,
        "weighted_absolute_max": 0.000364225,
        "bounded_absolute_max": 0.000364225,
        "weighted_absolute_p95": 0.000228876,
        "weighted_absolute_p99": 0.000320031,
        "connectivity_signature": "abc123",
    }

    values.update(
        overrides
    )

    return AtlasCanonicalHeadHybridDetailMeasurementObservation(
        **values
    )


def test_preserves_raw_quantitative_hybrid_detail_measurement():
    measurement = _measurement()

    assert measurement.measurement_id == (
        "subject-01-front-hybrid-detail"
    )
    assert measurement.source_view_id == "subject_01_front"

    assert measurement.image_reference_span_px == pytest.approx(
        322.499195
    )
    assert measurement.canonical_reference_span == pytest.approx(
        0.163734844
    )
    assert measurement.scale_factor == pytest.approx(
        0.000507706211
    )

    assert measurement.mapped_vertex_count == 264
    assert measurement.active_vertex_count == 264
    assert measurement.clipped_vertex_count == 0

    assert measurement.maximum_absolute_amplitude == pytest.approx(
        0.00163734844
    )
    assert measurement.raw_absolute_max == pytest.approx(
        0.000500000
    )
    assert measurement.weighted_absolute_max == pytest.approx(
        0.000364225
    )
    assert measurement.bounded_absolute_max == pytest.approx(
        0.000364225
    )
    assert measurement.weighted_absolute_p95 == pytest.approx(
        0.000228876
    )
    assert measurement.weighted_absolute_p99 == pytest.approx(
        0.000320031
    )

    assert measurement.clipped_vertex_fraction == pytest.approx(
        0.0
    )

    assert measurement.connectivity_signature == "abc123"


def test_clipped_fraction_is_derived_from_active_vertex_count():
    measurement = _measurement(
        active_vertex_count=227,
        clipped_vertex_count=1,
    )

    assert measurement.clipped_vertex_fraction == pytest.approx(
        1.0 / 227.0
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "measurement_id",
        "source_view_id",
        "connectivity_signature",
    ),
)
def test_identifiers_must_be_non_blank(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _measurement(
            **{
                field_name: "   ",
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "image_reference_span_px",
        "canonical_reference_span",
        "scale_factor",
        "maximum_absolute_amplitude",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
    ),
)
def test_positive_measurements_must_be_finite_and_positive(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _measurement(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "raw_absolute_max",
        "weighted_absolute_max",
        "bounded_absolute_max",
        "weighted_absolute_p95",
        "weighted_absolute_p99",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        -0.01,
        float("nan"),
        float("inf"),
    ),
)
def test_amplitude_measurements_must_be_finite_and_nonnegative(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _measurement(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "mapped_vertex_count",
        "active_vertex_count",
        "clipped_vertex_count",
    ),
)
def test_vertex_counts_must_be_integers(
    field_name,
):
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        _measurement(
            **{
                field_name: 1.5,
            }
        )


def test_rejects_invalid_vertex_count_relationships():
    with pytest.raises(
        ValueError,
        match="active_vertex_count",
    ):
        _measurement(
            mapped_vertex_count=100,
            active_vertex_count=101,
        )

    with pytest.raises(
        ValueError,
        match="clipped_vertex_count",
    ):
        _measurement(
            active_vertex_count=10,
            clipped_vertex_count=11,
        )


def test_rejects_bounded_amplitude_above_explicit_maximum():
    with pytest.raises(
        ValueError,
        match="bounded_absolute_max",
    ):
        _measurement(
            maximum_absolute_amplitude=0.001,
            bounded_absolute_max=0.002,
        )


def test_measurement_is_immutable():
    measurement = _measurement()

    with pytest.raises(
        FrozenInstanceError
    ):
        measurement.active_vertex_count = 1


def test_raw_measurement_does_not_claim_support_or_gate_decision():
    measurement = _measurement()

    for forbidden_attribute in (
        "identity_preservation_support",
        "multi_view_consistency",
        "physical_suitability",
        "support_score",
        "decision",
        "phase_9_authorized",
    ):
        assert not hasattr(
            measurement,
            forbidden_attribute,
        )
