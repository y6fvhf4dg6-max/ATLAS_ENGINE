from __future__ import annotations

from CORE.atlas_canonical_head_benchmark_evidence_coverage import (
    AtlasCanonicalHeadBenchmarkEvidenceCoverage,
)
from CORE.atlas_canonical_head_benchmark_measurement_observation import (
    AtlasCanonicalHeadBenchmarkMeasurementObservation,
)


class AtlasCanonicalHeadFlameBenchmarkEvidence:
    """
    Deterministic raw Phase 8.10 evidence for the
    FLAME 2023 Open parametric fixed-topology candidate.

    This catalog preserves verified raw benchmark
    measurements only.

    It performs no support normalization, candidate gating,
    architecture selection, or Phase 9 authorization.
    """

    CANDIDATE_ID = "flame-2023-open"
    IDENTITY_MODEL_CAPACITY = 300
    ACTIVE_IDENTITY_COMPONENT_COUNT = 90

    _MEASUREMENTS = (
        AtlasCanonicalHeadBenchmarkMeasurementObservation(
            measurement_id=(
                "flame-2023-open-subject-01-90d"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_01",
            view_count=3,
            landmarks_per_view=105,
            mean_reprojection_iod_nme=0.027984,
            mean_reprojection_bbox_nme=0.007818,
            cross_view_identity_shape_nme=0.059630,
            focal_identifiable=False,
            ground_truth_3d_available=False,
            volumetric_identity_proven=False,
            processing_time_seconds=1.407287,
        ),
        AtlasCanonicalHeadBenchmarkMeasurementObservation(
            measurement_id=(
                "flame-2023-open-subject-02-90d"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_02",
            view_count=3,
            landmarks_per_view=105,
            mean_reprojection_iod_nme=0.023456,
            mean_reprojection_bbox_nme=0.007082,
            cross_view_identity_shape_nme=0.064978,
            focal_identifiable=False,
            ground_truth_3d_available=False,
            volumetric_identity_proven=False,
            processing_time_seconds=1.457528,
        ),
    )

    @classmethod
    def measurements(
        cls,
    ) -> tuple[
        AtlasCanonicalHeadBenchmarkMeasurementObservation,
        ...,
    ]:
        return cls._MEASUREMENTS

    @classmethod
    def measurement_for_subject(
        cls,
        subject_id: str,
    ) -> AtlasCanonicalHeadBenchmarkMeasurementObservation:
        normalized = str(
            subject_id
        ).strip()

        for measurement in cls._MEASUREMENTS:
            if measurement.subject_id == normalized:
                return measurement

        raise KeyError(
            normalized
        )

    @classmethod
    def mean_reprojection_iod_nme(
        cls,
    ) -> float:
        return sum(
            measurement.mean_reprojection_iod_nme
            for measurement in cls._MEASUREMENTS
        ) / len(
            cls._MEASUREMENTS
        )

    @classmethod
    def mean_cross_view_identity_shape_nme(
        cls,
    ) -> float:
        return sum(
            measurement.cross_view_identity_shape_nme
            for measurement in cls._MEASUREMENTS
        ) / len(
            cls._MEASUREMENTS
        )

    @classmethod
    def all_focal_identifiable(
        cls,
    ) -> bool:
        return all(
            measurement.focal_identifiable
            for measurement in cls._MEASUREMENTS
        )

    @classmethod
    def any_volumetric_identity_proven(
        cls,
    ) -> bool:
        return any(
            measurement.volumetric_identity_proven
            for measurement in cls._MEASUREMENTS
        )


    @classmethod
    def coverage(
        cls,
    ) -> AtlasCanonicalHeadBenchmarkEvidenceCoverage:
        return AtlasCanonicalHeadBenchmarkEvidenceCoverage(
            candidate_id=cls.CANDIDATE_ID,
            identity_preservation_support="PARTIAL",
            multi_view_consistency="MEASURED",
            silhouette_profile_support="MISSING",
            head_ratio_support="MISSING",
            jaw_chin_support="MISSING",
            nose_projection_support="MISSING",
            orbital_cheek_volume_support="MISSING",
            expression_separation_support="MISSING",
            pose_separation_support="PARTIAL",
            topology_suitability="DIRECT",
            physical_suitability="MISSING",
            apple_silicon_runtime_support="DIRECT",
            reproducibility_support="DIRECT",
        )
