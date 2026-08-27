import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_mesh_unit_normalizer import (
    AtlasCanonicalHeadMetricMeshUnitNormalizer,
)


def test_converts_metre_vertices_to_millimetres():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [0.125, -0.050, 1.712],
        ],
        dtype=np.float64,
    )

    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=source,
        source_units="m",
        unit_provenance="FORMAT_STANDARD_DEFINED",
        unit_provenance_reference="test-fixture-explicit-metric-unit",
    )

    assert result.source_units == "m"
    assert result.target_units == "mm"
    assert result.scale_factor == pytest.approx(1000.0)
    np.testing.assert_allclose(
        result.vertices_mm,
        np.asarray(
            [
                [0.0, 0.0, 0.0],
                [125.0, -50.0, 1712.0],
            ],
            dtype=np.float64,
        ),
    )


@pytest.mark.parametrize(
    ("source_units", "expected_scale"),
    (
        ("mm", 1.0),
        ("cm", 10.0),
        ("m", 1000.0),
    ),
)
def test_supports_explicit_metric_source_units(
    source_units,
    expected_scale,
):
    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=np.asarray([[1.0, 2.0, 3.0]]),
        source_units=source_units,
        unit_provenance="FORMAT_STANDARD_DEFINED",
        unit_provenance_reference="test-fixture-explicit-metric-unit",
    )

    assert result.scale_factor == pytest.approx(expected_scale)


def test_does_not_mutate_source_vertices():
    source = np.asarray([[1.0, 2.0, 3.0]])
    before = source.copy()

    AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=source,
        source_units="cm",
        unit_provenance="FORMAT_STANDARD_DEFINED",
        unit_provenance_reference="test-fixture-explicit-metric-unit",
    )

    assert np.array_equal(source, before)


def test_rejects_unsupported_source_units():
    with pytest.raises(ValueError, match="source_units"):
        AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
            vertices=np.asarray([[1.0, 2.0, 3.0]]),
            source_units="px",
            unit_provenance="FORMAT_STANDARD_DEFINED",
            unit_provenance_reference="test-fixture-explicit-metric-unit",
        )


def test_rejects_nonfinite_vertices():
    with pytest.raises(ValueError, match="vertices"):
        AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
            vertices=np.asarray([[1.0, np.nan, 3.0]]),
            source_units="m",
            unit_provenance="FORMAT_STANDARD_DEFINED",
            unit_provenance_reference="test-fixture-explicit-metric-unit",
        )

# === PHASE 8 ITEM 10.2 UNIT CERTAINTY ===


def test_requires_explicit_unit_provenance_for_normalization():
    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=np.asarray([[1.0, 2.0, 3.0]]),
        source_units="m",
        unit_provenance="METADATA_DECLARED",
        unit_provenance_reference="RealityCapture CoordinateSystemOutputUnits=m",
    )

    assert result.source_units == "m"
    assert result.unit_provenance == "METADATA_DECLARED"
    assert result.unit_provenance_reference == (
        "RealityCapture CoordinateSystemOutputUnits=m"
    )


@pytest.mark.parametrize(
    "unit_provenance",
    (
        "FORMAT_STANDARD_DEFINED",
        "METADATA_DECLARED",
        "CALIBRATION_DERIVED",
    ),
)
def test_accepts_explicit_resolved_unit_provenance_classes(unit_provenance):
    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=np.asarray([[1.0, 2.0, 3.0]]),
        source_units="mm",
        unit_provenance=unit_provenance,
        unit_provenance_reference="verified-unit-source",
    )

    assert result.unit_provenance == unit_provenance


def test_rejects_unresolved_source_units_instead_of_inferring_scale():
    with pytest.raises(
        ValueError,
        match="source_units|unresolved",
    ):
        AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
            vertices=np.asarray([[1.0, 2.0, 3.0]]),
            source_units="unresolved",
            unit_provenance="UNRESOLVED",
            unit_provenance_reference="UNRESOLVED",
        )


def test_rejects_resolved_units_with_unresolved_unit_provenance():
    with pytest.raises(
        ValueError,
        match="unit_provenance",
    ):
        AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
            vertices=np.asarray([[1.0, 2.0, 3.0]]),
            source_units="mm",
            unit_provenance="UNRESOLVED",
            unit_provenance_reference="UNRESOLVED",
        )


def test_rejects_resolved_unit_provenance_with_unresolved_reference():
    with pytest.raises(
        ValueError,
        match="unit_provenance_reference",
    ):
        AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
            vertices=np.asarray([[1.0, 2.0, 3.0]]),
            source_units="mm",
            unit_provenance="METADATA_DECLARED",
            unit_provenance_reference="UNRESOLVED",
        )


def test_result_records_traceable_unit_transform():
    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=np.asarray([[1.0, 2.0, 3.0]]),
        source_units="cm",
        unit_provenance="FORMAT_STANDARD_DEFINED",
        unit_provenance_reference="source-format-unit-contract",
    )

    assert result.source_units == "cm"
    assert result.target_units == "mm"
    assert result.scale_factor == pytest.approx(10.0)
    assert result.unit_transform_kind == "EXPLICIT_METRIC_UNIT_CONVERSION"


def test_declared_mm_is_not_marked_as_metrologically_traceable():
    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=np.asarray([[1.0, 2.0, 3.0]]),
        source_units="mm",
        unit_provenance="METADATA_DECLARED",
        unit_provenance_reference="provider-metadata",
    )

    assert result.metrological_traceability_established is False
