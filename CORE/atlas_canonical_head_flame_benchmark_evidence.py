from __future__ import annotations

from CORE.atlas_canonical_head_benchmark_evidence_coverage import (
    AtlasCanonicalHeadBenchmarkEvidenceCoverage,
)
from CORE.atlas_canonical_head_benchmark_measurement_observation import (
    AtlasCanonicalHeadBenchmarkMeasurementObservation,
)
from CORE.atlas_canonical_head_held_out_view_observation import (
    AtlasCanonicalHeadHeldOutViewObservation,
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

    _HELD_OUT_OBSERVATIONS = (
        AtlasCanonicalHeadHeldOutViewObservation(
            observation_id=(
                "flame-2023-open-subject-01-"
                "side-a-side-b-to-front"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_01",
            training_view_ids=(
                "side_a",
                "side_b",
            ),
            held_out_view_id="front",
            shared_identity_component_count=(
                ACTIVE_IDENTITY_COMPONENT_COUNT
            ),
            identity_locked=True,
            held_out_pose_camera_only=True,
            held_out_reprojection_iod_nme=0.025737053,
            held_out_reprojection_bbox_nme=0.009386448,
            optimizer_success=True,
            processing_time_seconds=10.257207,
            expression_fixed_neutral=True,
            projection_model="weak_perspective",
        ),
        AtlasCanonicalHeadHeldOutViewObservation(
            observation_id=(
                "flame-2023-open-subject-01-"
                "front-side-b-to-side-a"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_01",
            training_view_ids=(
                "front",
                "side_b",
            ),
            held_out_view_id="side_a",
            shared_identity_component_count=(
                ACTIVE_IDENTITY_COMPONENT_COUNT
            ),
            identity_locked=True,
            held_out_pose_camera_only=True,
            held_out_reprojection_iod_nme=0.042736096,
            held_out_reprojection_bbox_nme=0.010860442,
            optimizer_success=True,
            processing_time_seconds=10.775558,
            expression_fixed_neutral=True,
            projection_model="weak_perspective",
        ),
        AtlasCanonicalHeadHeldOutViewObservation(
            observation_id=(
                "flame-2023-open-subject-01-"
                "front-side-a-to-side-b"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_01",
            training_view_ids=(
                "front",
                "side_a",
            ),
            held_out_view_id="side_b",
            shared_identity_component_count=(
                ACTIVE_IDENTITY_COMPONENT_COUNT
            ),
            identity_locked=True,
            held_out_pose_camera_only=True,
            held_out_reprojection_iod_nme=0.038976068,
            held_out_reprojection_bbox_nme=0.010278185,
            optimizer_success=True,
            processing_time_seconds=10.701019,
            expression_fixed_neutral=True,
            projection_model="weak_perspective",
        ),
        AtlasCanonicalHeadHeldOutViewObservation(
            observation_id=(
                "flame-2023-open-subject-02-"
                "side-a-side-b-to-front"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_02",
            training_view_ids=(
                "side_a",
                "side_b",
            ),
            held_out_view_id="front",
            shared_identity_component_count=(
                ACTIVE_IDENTITY_COMPONENT_COUNT
            ),
            identity_locked=True,
            held_out_pose_camera_only=True,
            held_out_reprojection_iod_nme=0.038987713,
            held_out_reprojection_bbox_nme=0.014025643,
            optimizer_success=True,
            processing_time_seconds=16.549599,
            expression_fixed_neutral=True,
            projection_model="weak_perspective",
        ),
        AtlasCanonicalHeadHeldOutViewObservation(
            observation_id=(
                "flame-2023-open-subject-02-"
                "front-side-b-to-side-a"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_02",
            training_view_ids=(
                "front",
                "side_b",
            ),
            held_out_view_id="side_a",
            shared_identity_component_count=(
                ACTIVE_IDENTITY_COMPONENT_COUNT
            ),
            identity_locked=True,
            held_out_pose_camera_only=True,
            held_out_reprojection_iod_nme=0.037416831,
            held_out_reprojection_bbox_nme=0.011151774,
            optimizer_success=True,
            processing_time_seconds=13.301181,
            expression_fixed_neutral=True,
            projection_model="weak_perspective",
        ),
        AtlasCanonicalHeadHeldOutViewObservation(
            observation_id=(
                "flame-2023-open-subject-02-"
                "front-side-a-to-side-b"
            ),
            candidate_id=CANDIDATE_ID,
            subject_id="subject_02",
            training_view_ids=(
                "front",
                "side_a",
            ),
            held_out_view_id="side_b",
            shared_identity_component_count=(
                ACTIVE_IDENTITY_COMPONENT_COUNT
            ),
            identity_locked=True,
            held_out_pose_camera_only=True,
            held_out_reprojection_iod_nme=0.031452767,
            held_out_reprojection_bbox_nme=0.008749089,
            optimizer_success=True,
            processing_time_seconds=11.974395,
            expression_fixed_neutral=True,
            projection_model="weak_perspective",
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
    def held_out_observations(
        cls,
    ) -> tuple[
        AtlasCanonicalHeadHeldOutViewObservation,
        ...,
    ]:
        return cls._HELD_OUT_OBSERVATIONS

    @classmethod
    def held_out_observations_for_subject(
        cls,
        subject_id: str,
    ) -> tuple[
        AtlasCanonicalHeadHeldOutViewObservation,
        ...,
    ]:
        normalized = str(
            subject_id
        ).strip()

        observations = tuple(
            observation
            for observation in cls._HELD_OUT_OBSERVATIONS
            if observation.subject_id == normalized
        )

        if not observations:
            raise KeyError(
                normalized
            )

        return observations

    @classmethod
    def held_out_observation(
        cls,
        *,
        subject_id: str,
        held_out_view_id: str,
    ) -> AtlasCanonicalHeadHeldOutViewObservation:
        normalized_subject = str(
            subject_id
        ).strip()
        normalized_view = str(
            held_out_view_id
        ).strip()

        for observation in cls._HELD_OUT_OBSERVATIONS:
            if (
                observation.subject_id
                == normalized_subject
                and observation.held_out_view_id
                == normalized_view
            ):
                return observation

        raise KeyError(
            (
                normalized_subject,
                normalized_view,
            )
        )

    @classmethod
    def mean_held_out_reprojection_iod_nme(
        cls,
    ) -> float:
        return sum(
            observation.held_out_reprojection_iod_nme
            for observation in cls._HELD_OUT_OBSERVATIONS
        ) / len(
            cls._HELD_OUT_OBSERVATIONS
        )

    @classmethod
    def mean_held_out_reprojection_bbox_nme(
        cls,
    ) -> float:
        return sum(
            observation.held_out_reprojection_bbox_nme
            for observation in cls._HELD_OUT_OBSERVATIONS
        ) / len(
            cls._HELD_OUT_OBSERVATIONS
        )

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
