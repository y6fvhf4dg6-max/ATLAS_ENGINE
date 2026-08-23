from __future__ import annotations

from CORE.atlas_canonical_head_benchmark_evidence_coverage import (
    AtlasCanonicalHeadBenchmarkEvidenceCoverage,
)


class AtlasCanonicalHeadPrnetBenchmarkEvidence:
    """
    Deterministic raw Phase 8.10 evidence for the
    PRNet direct-neural-dense candidate.

    This catalog preserves verified benchmark evidence only.

    It performs no support normalization, candidate gating,
    architecture selection, or Phase 9 authorization.
    """

    CANDIDATE_ID = "prnet"
    ARCHITECTURE_FAMILY = "direct_neural_dense"

    VERTEX_COUNT = 43867
    TRIANGLE_COUNT = 86906

    FRONT_CASE_COUNT = 2
    LATERAL_CASE_COUNT = 4

    FRONT_MEAN_IOU = 0.8580595773782285
    LATERAL_MEAN_IOU = 0.7694332569672948
    LATERAL_MIN_IOU = 0.7140243158622372
    LATERAL_MEAN_ABSOLUTE_OFFSET = 0.5696098447867725

    SILHOUETTE_REFERENCE_KIND = (
        "mediapipe_face_oval_projection"
    )
    SILHOUETTE_REFERENCE_IS_3D_GROUND_TRUTH = False
    SILHOUETTE_REFERENCE_IS_MANUAL_SEGMENTATION = False
    SIDE_CASES_CANONICALLY_CLASSIFIED_AS_PROFILE = False

    MULTIVIEW_SUBJECT_COUNT = 2
    MULTIVIEW_PAIR_COUNT = 6

    MULTIVIEW_MEAN_PAIRWISE_NORMALIZED_RESIDUAL = (
        0.03667331198932592
    )
    MULTIVIEW_MAX_PAIRWISE_NORMALIZED_RESIDUAL = (
        0.04595704484272138
    )

    MULTIVIEW_MEASUREMENT_KIND = (
        "topology_corresponded_3d_similarity_aligned_residual"
    )
    MULTIVIEW_IS_IDENTITY_PRESERVATION_PROOF = False
    MULTIVIEW_IS_FLAME_CROSS_VIEW_IDENTITY_SHAPE_NME = False

    @classmethod
    def coverage(
        cls,
    ) -> AtlasCanonicalHeadBenchmarkEvidenceCoverage:
        return AtlasCanonicalHeadBenchmarkEvidenceCoverage(
            candidate_id=cls.CANDIDATE_ID,
            identity_preservation_support="MISSING",
            multi_view_consistency="MEASURED",
            silhouette_profile_support="PARTIAL",
            head_ratio_support="MISSING",
            jaw_chin_support="MISSING",
            nose_projection_support="MISSING",
            orbital_cheek_volume_support="MISSING",
            expression_separation_support="MISSING",
            pose_separation_support="MISSING",
            topology_suitability="DIRECT",
            physical_suitability="MISSING",
            apple_silicon_runtime_support="DIRECT",
            reproducibility_support="DIRECT",
        )
