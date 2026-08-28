from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_physical_adapter_isolation import (
    AtlasCanonicalHeadPhysicalAdapterIsolation,
    AtlasCanonicalHeadPhysicalTransform,
)


def _transform(**overrides):
    values = {
        "operation": "scale",
        "classification": "identity_neutral",
        "parameters": (("factor", "0.42"),),
    }
    values.update(overrides)
    return AtlasCanonicalHeadPhysicalTransform(**values)


def _isolation(**overrides):
    values = {
        "source_identity_id": "person-a",
        "source_topology_signature": "topology-before",
        "source_geometry_signature_before": "geometry-before",
        "source_geometry_signature_after": "geometry-before",
        "source_provenance": "canonical:person-a",
        "representation_id": "person-a-relief-v1",
        "representation_kind": "relief",
        "physical_unit": "mm",
        "output_topology_signature": "physical-topology-v1",
        "transform_ledger": (
            _transform(),
        ),
    }
    values.update(overrides)
    return AtlasCanonicalHeadPhysicalAdapterIsolation(**values)


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
    isolation = _isolation(
        representation_kind=representation_kind,
    )

    assert isolation.representation_kind == representation_kind


def test_rejects_unknown_representation_kind():
    with pytest.raises(ValueError, match="representation_kind"):
        _isolation(representation_kind="generic_mesh")


@pytest.mark.parametrize(
    "classification",
    (
        "identity_neutral",
        "identity_sensitive",
        "topology_changing",
    ),
)
def test_accepts_transform_classifications(classification):
    transform = _transform(
        classification=classification,
    )

    assert transform.classification == classification


def test_rejects_unknown_transform_classification():
    with pytest.raises(ValueError, match="classification"):
        _transform(classification="harmless")


@pytest.mark.parametrize(
    ("operation", "classification"),
    (
        ("scale", "identity_neutral"),
        ("orientation", "identity_neutral"),
        ("translation", "identity_neutral"),
        ("clipping", "identity_sensitive"),
        ("relief_depth_mapping", "identity_sensitive"),
        ("relief_depth_compression", "identity_sensitive"),
        ("lod_decimation", "topology_changing"),
        ("shell_thickness", "identity_neutral"),
        ("smoothing", "identity_sensitive"),
        ("repair", "identity_neutral"),
        ("feature_exaggeration", "identity_sensitive"),
        ("topology_change", "topology_changing"),
    ),
)
def test_accepts_traceable_physical_transform_operations(
    operation,
    classification,
):
    transform = _transform(
        operation=operation,
        classification=classification,
    )

    assert transform.operation == operation
    assert transform.classification == classification


def test_rejects_unknown_transform_operation():
    with pytest.raises(ValueError, match="operation"):
        _transform(operation="magic_fix")


def test_transform_parameters_are_immutable_snapshot():
    parameters = [["factor", "0.42"]]

    transform = _transform(
        parameters=parameters,
    )

    parameters[0][1] = "9.99"

    assert transform.parameters == (
        ("factor", "0.42"),
    )

    with pytest.raises(FrozenInstanceError):
        transform.operation = "translation"


def test_source_and_output_identity_are_explicit():
    isolation = _isolation()

    assert isolation.source_identity_id == "person-a"
    assert isolation.representation_id == "person-a-relief-v1"
    assert isolation.source_identity_id != isolation.representation_id


def test_source_provenance_is_required():
    with pytest.raises(ValueError, match="source_provenance"):
        _isolation(source_provenance="   ")


def test_source_identity_is_required():
    with pytest.raises(ValueError, match="source_identity_id"):
        _isolation(source_identity_id="")


def test_representation_id_is_required():
    with pytest.raises(ValueError, match="representation_id"):
        _isolation(representation_id=" ")


def test_physical_unit_is_explicit_mm():
    isolation = _isolation()

    assert isolation.physical_unit == "mm"


@pytest.mark.parametrize(
    "physical_unit",
    (
        "",
        "cm",
        "m",
        "unitless",
    ),
)
def test_rejects_non_mm_or_missing_physical_unit(physical_unit):
    with pytest.raises(ValueError, match="physical_unit"):
        _isolation(physical_unit=physical_unit)


def test_transform_ledger_preserves_declared_order():
    ledger = (
        _transform(
            operation="scale",
            classification="identity_neutral",
        ),
        _transform(
            operation="relief_depth_compression",
            classification="identity_sensitive",
        ),
        _transform(
            operation="lod_decimation",
            classification="topology_changing",
        ),
    )

    isolation = _isolation(
        transform_ledger=ledger,
    )

    assert tuple(
        transform.operation
        for transform in isolation.transform_ledger
    ) == (
        "scale",
        "relief_depth_compression",
        "lod_decimation",
    )


def test_rejects_empty_transform_ledger():
    with pytest.raises(ValueError, match="transform_ledger"):
        _isolation(transform_ledger=())


def test_rejects_non_transform_ledger_member():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadPhysicalTransform",
    ):
        _isolation(
            transform_ledger=(
                {"operation": "scale"},
            ),
        )


def test_source_signature_must_survive_adapter_unchanged():
    isolation = _isolation()

    assert isolation.source_is_unchanged is True
    assert isolation.isolation_state == "ISOLATED"


def test_changed_source_signature_fails_isolation():
    isolation = _isolation(
        source_geometry_signature_after="geometry-mutated",
    )

    assert isolation.source_is_unchanged is False
    assert isolation.isolation_state == "SOURCE_MUTATED"


def test_output_topology_signature_is_explicit():
    isolation = _isolation()

    assert (
        isolation.output_topology_signature
        == "physical-topology-v1"
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "source_topology_signature",
        "source_geometry_signature_before",
        "source_geometry_signature_after",
        "output_topology_signature",
    ),
)
def test_signatures_must_be_nonblank(field_name):
    with pytest.raises(ValueError, match=field_name):
        _isolation(**{field_name: "   "})


def test_isolation_record_is_immutable():
    isolation = _isolation()

    with pytest.raises(FrozenInstanceError):
        isolation.representation_kind = "bust"


def test_contract_does_not_claim_identity_quality_or_phase_gate():
    isolation = _isolation()

    for forbidden in (
        "likeness_score",
        "identity_preservation_support",
        "support_score",
        "decision",
        "production_status",
        "phase8_go",
        "phase_9_authorized",
    ):
        assert not hasattr(isolation, forbidden)


def test_source_and_derived_representation_ids_must_be_distinct():
    with pytest.raises(
        ValueError,
        match="representation_id",
    ):
        _isolation(
            representation_id="person-a",
        )


@pytest.mark.parametrize(
    "operation",
    (
        "topology_change",
        "lod_decimation",
    ),
)
def test_topology_changing_operations_require_topology_changing_classification(
    operation,
):
    with pytest.raises(
        ValueError,
        match="classification",
    ):
        _transform(
            operation=operation,
            classification="identity_neutral",
        )


@pytest.mark.parametrize(
    "operation",
    (
        "clipping",
        "relief_depth_mapping",
        "relief_depth_compression",
        "smoothing",
        "feature_exaggeration",
    ),
)
def test_identity_sensitive_operations_cannot_be_declared_identity_neutral(
    operation,
):
    with pytest.raises(
        ValueError,
        match="classification",
    ):
        _transform(
            operation=operation,
            classification="identity_neutral",
        )


def test_transform_requires_at_least_one_parameter():
    with pytest.raises(
        ValueError,
        match="parameters",
    ):
        _transform(
            parameters=(),
        )


def test_transform_parameter_keys_must_be_unique():
    with pytest.raises(
        ValueError,
        match="parameter",
    ):
        _transform(
            parameters=(
                ("factor", "0.42"),
                ("factor", "0.50"),
            ),
        )
