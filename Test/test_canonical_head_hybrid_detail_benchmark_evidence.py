import pytest

from CORE.atlas_canonical_head_hybrid_detail_benchmark_evidence import (
    AtlasCanonicalHeadHybridDetailBenchmarkEvidence,
)
from CORE.atlas_canonical_head_hybrid_detail_measurement_observation import (
    AtlasCanonicalHeadHybridDetailMeasurementObservation,
)


def test_exposes_six_real_hybrid_detail_measurements():
    measurements = (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .measurements()
    )

    assert len(measurements) == 6

    assert all(
        isinstance(
            item,
            AtlasCanonicalHeadHybridDetailMeasurementObservation,
        )
        for item in measurements
    )

    assert tuple(
        item.source_view_id
        for item in measurements
    ) == (
        "subject_01_front",
        "subject_01_side_a",
        "subject_01_side_b",
        "subject_02_front",
        "subject_02_side_a",
        "subject_02_side_b",
    )


@pytest.mark.parametrize(
    (
        "source_view_id",
        "image_span",
        "scale_factor",
        "active_count",
        "clipped_count",
        "raw_max",
        "weighted_max",
        "bounded_max",
        "p95",
        "p99",
    ),
    (
        (
            "subject_01_front",
            322.4991950555889,
            0.000507706210515772,
            264,
            0,
            0.000970137864527527,
            0.0003642247398480735,
            0.0003642247398480735,
            0.00022887589220091912,
            0.00032003052100682526,
        ),
        (
            "subject_01_side_a",
            209.92918648830002,
            0.000779952740040677,
            135,
            0,
            0.0016730525137833938,
            0.001429780039238705,
            0.001429780039238705,
            0.000531627427675384,
            0.0008728849554949033,
        ),
        (
            "subject_01_side_b",
            180.577946817856,
            0.000906726691167968,
            167,
            0,
            0.0015320988042668267,
            0.001365981916788091,
            0.001365981916788091,
            0.00039609365349952617,
            0.0006089271266831761,
        ),
        (
            "subject_02_front",
            511.73689699750526,
            0.0003199590359357224,
            264,
            0,
            0.0012627172917912713,
            0.0012271687500435202,
            0.0012271687500435202,
            0.00014399500927188006,
            0.00031102139735496754,
        ),
        (
            "subject_02_side_a",
            203.15695527324993,
            0.0008059524420211624,
            227,
            1,
            0.0037517881717491265,
            0.0034050619741867834,
            0.0016373484421605986,
            0.0007712167732157531,
            0.0012369155287473446,
        ),
        (
            "subject_02_side_b",
            187.7749995011597,
            0.0008719736101772623,
            211,
            0,
            0.0034048486389311895,
            0.0015443833816254464,
            0.0015443833816254464,
            0.0006973219241729734,
            0.000836522725219002,
        ),
    ),
)
def test_preserves_exact_real_six_view_measurements(
    source_view_id,
    image_span,
    scale_factor,
    active_count,
    clipped_count,
    raw_max,
    weighted_max,
    bounded_max,
    p95,
    p99,
):
    measurement = (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .measurement_for_view(
            source_view_id
        )
    )

    assert measurement.image_reference_span_px == pytest.approx(
        image_span
    )
    assert measurement.canonical_reference_span == pytest.approx(
        0.16373484421605985
    )
    assert measurement.scale_factor == pytest.approx(
        scale_factor
    )

    assert measurement.mapped_vertex_count == 264
    assert measurement.active_vertex_count == active_count
    assert measurement.clipped_vertex_count == clipped_count

    assert measurement.maximum_absolute_amplitude == pytest.approx(
        0.0016373484421605986
    )

    assert measurement.raw_absolute_max == pytest.approx(
        raw_max
    )
    assert measurement.weighted_absolute_max == pytest.approx(
        weighted_max
    )
    assert measurement.bounded_absolute_max == pytest.approx(
        bounded_max
    )
    assert measurement.weighted_absolute_p95 == pytest.approx(
        p95
    )
    assert measurement.weighted_absolute_p99 == pytest.approx(
        p99
    )

    assert measurement.connectivity_signature == (
        "3fa911072b9c2cea8807b02bfea1d69c36c6208a169f9dd4733ed1d8bd4809be"
    )


def test_exposes_verified_aggregate_real_hybrid_detail_measurements():
    assert (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .view_count()
        == 6
    )

    assert (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .active_vertex_total()
        == 1268
    )

    assert (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .clipped_vertex_total()
        == 1
    )

    assert (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .clipped_vertex_fraction()
        == pytest.approx(
            0.0007886435331230284
        )
    )

    assert (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .connectivity_signature_count()
        == 1
    )


def test_unknown_view_is_rejected():
    with pytest.raises(
        KeyError,
        match="subject_03_front",
    ):
        (
            AtlasCanonicalHeadHybridDetailBenchmarkEvidence
            .measurement_for_view(
                "subject_03_front"
            )
        )


def test_raw_evidence_catalog_does_not_claim_support_or_decision():
    catalog = AtlasCanonicalHeadHybridDetailBenchmarkEvidence

    for forbidden_attribute in (
        "candidate_observation",
        "identity_preservation_support",
        "multi_view_consistency",
        "physical_suitability",
        "support_score",
        "decision",
        "phase_9_authorized",
    ):
        assert not hasattr(
            catalog,
            forbidden_attribute,
        )

import importlib.util
from pathlib import Path

import numpy as np

from CORE.atlas_canonical_head_correspondence_reference_span_resolver import (
    AtlasCanonicalHeadCorrespondenceReferenceSpanResolver,
)
from CORE.atlas_canonical_head_residual_detail_scale_normalizer import (
    AtlasCanonicalHeadResidualDetailScaleNormalizer,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)
from CORE.atlas_canonical_head_surface_view_residual_detail_bridge import (
    AtlasCanonicalHeadSurfaceViewResidualDetailBridge,
)


def test_catalog_matches_recomputed_real_six_view_hybrid_detail_chain():
    root = Path(__file__).resolve().parents[1]

    real_test_path = (
        root
        / "Test"
        / "test_phase8_10_real_flame_surface_correspondence.py"
    )

    spec = importlib.util.spec_from_file_location(
        "phase8_10_real_hybrid_detail_binding",
        real_test_path,
    )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    geometry = (
        module._load_real_flame_reference_geometry()
    )

    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id=(
            "phase8-10-item9-catalog-cross-check"
        ),
        topology=geometry.topology,
        observed_sample_to_canonical_surface=(
            module._load_real_flame_surface_mapping()
        ),
    )

    recomputed_active_total = 0
    recomputed_clipped_total = 0

    for case_id in module.CASES:
        source_observation = (
            module._load_real_residual_detail_observation(
                case_id
            )
        )

        spans = (
            AtlasCanonicalHeadCorrespondenceReferenceSpanResolver
            .resolve(
                observation=source_observation,
                correspondence=correspondence,
                geometry=geometry,
            )
        )

        normalized = (
            AtlasCanonicalHeadResidualDetailScaleNormalizer
            .normalize(
                observation=source_observation,
                image_reference_span_px=(
                    spans.image_reference_span_px
                ),
                canonical_reference_span=(
                    spans.canonical_reference_span
                ),
            )
        )

        maximum = (
            spans.canonical_reference_span
            * module.PHASE8_10_HYBRID_MAXIMUM_AMPLITUDE_FRACTION
        )

        bridge = (
            AtlasCanonicalHeadSurfaceViewResidualDetailBridge
            .resolve(
                observation=normalized.observation,
                correspondence=correspondence,
                maximum_absolute_amplitude=maximum,
            )
        )

        active_mask = (
            bridge.canonical_confidence > 0.0
        )

        raw_active = np.abs(
            bridge.canonical_scalar_detail[
                active_mask
            ]
        )

        weighted_active = np.abs(
            bridge.weighted_amplitude[
                active_mask
            ]
        )

        bounded_active = np.abs(
            bridge.bounded_amplitude[
                active_mask
            ]
        )

        active_count = int(
            np.count_nonzero(
                active_mask
            )
        )

        clipped_count = int(
            np.count_nonzero(
                weighted_active
                > maximum + 1e-15
            )
        )

        catalog = (
            AtlasCanonicalHeadHybridDetailBenchmarkEvidence
            .measurement_for_view(
                case_id
            )
        )

        assert catalog.image_reference_span_px == pytest.approx(
            spans.image_reference_span_px
        )
        assert catalog.canonical_reference_span == pytest.approx(
            spans.canonical_reference_span
        )
        assert catalog.scale_factor == pytest.approx(
            normalized.scale_factor
        )

        assert catalog.mapped_vertex_count == (
            bridge.mapped_vertex_count
        )
        assert catalog.active_vertex_count == active_count
        assert catalog.clipped_vertex_count == clipped_count

        assert catalog.maximum_absolute_amplitude == pytest.approx(
            bridge.maximum_absolute_amplitude
        )

        assert catalog.raw_absolute_max == pytest.approx(
            float(
                np.max(
                    raw_active
                )
            )
        )

        assert catalog.weighted_absolute_max == pytest.approx(
            float(
                np.max(
                    weighted_active
                )
            )
        )

        assert catalog.bounded_absolute_max == pytest.approx(
            float(
                np.max(
                    bounded_active
                )
            )
        )

        assert catalog.weighted_absolute_p95 == pytest.approx(
            float(
                np.percentile(
                    weighted_active,
                    95.0,
                )
            )
        )

        assert catalog.weighted_absolute_p99 == pytest.approx(
            float(
                np.percentile(
                    weighted_active,
                    99.0,
                )
            )
        )

        assert catalog.connectivity_signature == (
            bridge.connectivity_signature
        )

        recomputed_active_total += active_count
        recomputed_clipped_total += clipped_count

    assert recomputed_active_total == (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .active_vertex_total()
    )
    assert recomputed_active_total == 1268

    assert recomputed_clipped_total == (
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .clipped_vertex_total()
    )
    assert recomputed_clipped_total == 1

    assert (
        recomputed_clipped_total
        / recomputed_active_total
    ) == pytest.approx(
        AtlasCanonicalHeadHybridDetailBenchmarkEvidence
        .clipped_vertex_fraction()
    )
