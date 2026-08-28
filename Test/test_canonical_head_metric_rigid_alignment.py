import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_rigid_alignment import (
    AtlasCanonicalHeadMetricRigidAlignment,
)


def test_recovers_exact_rigid_alignment_without_scaling():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [0.0, 20.0, 0.0],
            [0.0, 0.0, 30.0],
        ],
        dtype=np.float64,
    )

    rotation = np.asarray(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    translation = np.asarray(
        [100.0, -50.0, 25.0],
        dtype=np.float64,
    )

    target = source @ rotation.T + translation

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=target,
    )

    np.testing.assert_allclose(
        result.aligned_source_points,
        target,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        result.rotation,
        rotation,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        result.translation,
        translation,
        atol=1e-9,
    )
    assert result.scale_factor == pytest.approx(1.0)


def test_does_not_mutate_source_or_target_points():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )
    target = source + np.asarray(
        [4.0, 5.0, 6.0]
    )

    source_before = source.copy()
    target_before = target.copy()

    AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=target,
    )

    np.testing.assert_array_equal(
        source,
        source_before,
    )
    np.testing.assert_array_equal(
        target,
        target_before,
    )


def test_rejects_mismatched_point_counts():
    with pytest.raises(
        ValueError,
        match="same shape",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=np.zeros((3, 3)),
            target_points=np.zeros((4, 3)),
        )


def test_rejects_nonfinite_points():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, np.nan, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=source,
            target_points=np.zeros((3, 3)),
        )

# === PHASE 8 ITEM 10.5 RIGID ALIGNMENT CONTRACT ===


def _well_conditioned_points():
    return np.asarray(
        [
            [0.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [0.0, 20.0, 0.0],
            [0.0, 0.0, 30.0],
        ],
        dtype=np.float64,
    )


def test_result_explicitly_identifies_scale_fixed_rigid_alignment():
    source = _well_conditioned_points()
    target = source + np.asarray([2.0, -3.0, 4.0])

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=target,
    )

    assert result.alignment_mode == "RIGID_SCALE_FIXED"
    assert result.scale_factor == pytest.approx(1.0)


def test_mathematically_computable_transform_is_not_automatically_admissible():
    source = _well_conditioned_points()
    target = source + np.asarray([2.0, -3.0, 4.0])

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=target,
    )

    assert result.alignment_admissibility == "UNRESOLVED"


def test_records_solver_derived_alignment_audit_states():
    source = _well_conditioned_points()

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=source,
    )

    assert result.anchor_sufficiency == "SUFFICIENT"
    assert result.initialization == "DETERMINISTIC_CLOSED_FORM"
    assert result.reflection_state == "NOT_APPLIED"
    assert result.icp_refinement_state == "NOT_APPLIED"
    assert (
        result.multiple_initialization_sensitivity
        == "NOT_APPLICABLE_CLOSED_FORM"
    )


def test_records_unresolved_sensitivity_and_stability_until_independently_audited():
    source = _well_conditioned_points()

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=source,
    )

    assert result.anchor_subset_sensitivity == "UNRESOLVED"
    assert result.solver_stability == "UNRESOLVED"
    assert result.transform_stability == "UNRESOLVED"
    assert result.icp_free_agreement == "NOT_APPLICABLE_NO_ICP"


def test_rejects_collinear_anchor_geometry_as_insufficient_for_3d_rigid_alignment():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [3.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="anchor|rank|collinear|sufficient",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=source,
            target_points=source,
        )


def test_rigid_solver_never_returns_an_improper_rotation():
    source = _well_conditioned_points()
    reflected = source.copy()
    reflected[:, 0] *= -1.0

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=reflected,
    )

    assert np.linalg.det(result.rotation) == pytest.approx(
        1.0,
        abs=1e-12,
    )
    assert result.reflection_state == "NOT_APPLIED"


def test_alignment_audit_states_can_be_supplied_without_changing_rigid_scale():
    source = _well_conditioned_points()

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=source,
        alignment_admissibility="ADMISSIBLE",
        coordinate_system_state="VERIFIED",
        anchor_subset_sensitivity="VERIFIED_STABLE",
        solver_stability="VERIFIED_STABLE",
        transform_stability="VERIFIED_STABLE",
    )

    assert result.alignment_admissibility == "ADMISSIBLE"
    assert result.anchor_subset_sensitivity == "VERIFIED_STABLE"
    assert result.solver_stability == "VERIFIED_STABLE"
    assert result.transform_stability == "VERIFIED_STABLE"
    assert result.scale_factor == pytest.approx(1.0)


def test_rejects_unknown_alignment_admissibility_state():
    source = _well_conditioned_points()

    with pytest.raises(
        ValueError,
        match="alignment_admissibility",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=source,
            target_points=source,
            alignment_admissibility="MAYBE",
        )

# === PHASE 8 ITEM 10.5 ADMISSIBILITY CROSS-FIELD RED ===


def test_admissible_alignment_rejects_unresolved_stability_states():
    source = _well_conditioned_points()

    with pytest.raises(
        ValueError,
        match="ADMISSIBLE|stability|VERIFIED_STABLE",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=source,
            target_points=source,
            alignment_admissibility="ADMISSIBLE",
            anchor_subset_sensitivity="UNRESOLVED",
            solver_stability="UNRESOLVED",
            transform_stability="UNRESOLVED",
        )


def test_admissible_alignment_rejects_unstable_stability_states():
    source = _well_conditioned_points()

    with pytest.raises(
        ValueError,
        match="ADMISSIBLE|stability|VERIFIED_STABLE",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=source,
            target_points=source,
            alignment_admissibility="ADMISSIBLE",
            anchor_subset_sensitivity="UNSTABLE",
            solver_stability="UNSTABLE",
            transform_stability="UNSTABLE",
        )

# === PHASE 8 ITEM 10.5 COORDINATE ADMISSIBILITY RED ===


def test_admissible_alignment_rejects_unresolved_coordinate_system():
    source = _well_conditioned_points()

    with pytest.raises(
        ValueError,
        match="ADMISSIBLE|coordinate|VERIFIED",
    ):
        AtlasCanonicalHeadMetricRigidAlignment.solve(
            source_points=source,
            target_points=source,
            alignment_admissibility="ADMISSIBLE",
            coordinate_system_state="UNRESOLVED",
            anchor_subset_sensitivity="VERIFIED_STABLE",
            solver_stability="VERIFIED_STABLE",
            transform_stability="VERIFIED_STABLE",
        )


def test_admissible_alignment_accepts_verified_coordinate_system():
    source = _well_conditioned_points()

    result = AtlasCanonicalHeadMetricRigidAlignment.solve(
        source_points=source,
        target_points=source,
        alignment_admissibility="ADMISSIBLE",
        coordinate_system_state="VERIFIED",
        anchor_subset_sensitivity="VERIFIED_STABLE",
        solver_stability="VERIFIED_STABLE",
        transform_stability="VERIFIED_STABLE",
    )

    assert result.coordinate_system_state == "VERIFIED"
    assert result.alignment_admissibility == "ADMISSIBLE"

# === PHASE 8 ITEM 10.6 ALIGNMENT LANDMARK INDEPENDENCE RED ===


def test_alignment_landmark_independence_audit_records_exact_feature_and_region_sets():
    from CORE.atlas_canonical_head_metric_rigid_alignment import (
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit,
    )

    result = AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit.evaluate(
        alignment_features=("nose_tip", "left_eye_outer", "right_eye_outer"),
        evaluation_features=("nose_tip", "chin"),
        alignment_regions=("nose", "orbital"),
        evaluation_regions=("nose", "jaw_chin"),
    )

    assert result.alignment_features == (
        "nose_tip",
        "left_eye_outer",
        "right_eye_outer",
    )
    assert result.evaluation_features == (
        "nose_tip",
        "chin",
    )
    assert result.alignment_regions == (
        "nose",
        "orbital",
    )
    assert result.evaluation_regions == (
        "nose",
        "jaw_chin",
    )


def test_alignment_landmark_independence_audit_computes_feature_and_region_overlap():
    from CORE.atlas_canonical_head_metric_rigid_alignment import (
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit,
    )

    result = AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit.evaluate(
        alignment_features=("nose_tip", "left_eye_outer", "right_eye_outer"),
        evaluation_features=("chin", "nose_tip"),
        alignment_regions=("orbital", "nose"),
        evaluation_regions=("jaw_chin", "nose"),
    )

    assert result.feature_overlap == ("nose_tip",)
    assert result.region_overlap == ("nose",)


def test_feature_overlap_is_reported_as_alignment_bias_leakage_risk():
    from CORE.atlas_canonical_head_metric_rigid_alignment import (
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit,
    )

    result = AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit.evaluate(
        alignment_features=("nose_tip", "left_eye_outer"),
        evaluation_features=("nose_tip", "chin"),
        alignment_regions=("orbital",),
        evaluation_regions=("jaw_chin",),
    )

    assert result.feature_overlap == ("nose_tip",)
    assert result.region_overlap == ()
    assert result.alignment_bias_leakage_risk == "OVERLAP_PRESENT"


def test_region_overlap_is_reported_as_alignment_bias_leakage_risk():
    from CORE.atlas_canonical_head_metric_rigid_alignment import (
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit,
    )

    result = AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit.evaluate(
        alignment_features=("left_eye_outer",),
        evaluation_features=("chin",),
        alignment_regions=("orbital", "nose"),
        evaluation_regions=("nose", "jaw_chin"),
    )

    assert result.feature_overlap == ()
    assert result.region_overlap == ("nose",)
    assert result.alignment_bias_leakage_risk == "OVERLAP_PRESENT"


def test_disjoint_alignment_and_evaluation_support_has_no_identified_overlap_risk():
    from CORE.atlas_canonical_head_metric_rigid_alignment import (
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit,
    )

    result = AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit.evaluate(
        alignment_features=("left_eye_outer", "right_eye_outer"),
        evaluation_features=("chin", "mouth_center"),
        alignment_regions=("orbital",),
        evaluation_regions=("jaw_chin", "perioral"),
    )

    assert result.feature_overlap == ()
    assert result.region_overlap == ()
    assert (
        result.alignment_bias_leakage_risk
        == "NO_OVERLAP_IDENTIFIED"
    )


def test_overlap_risk_is_derived_and_not_caller_supplied():
    from CORE.atlas_canonical_head_metric_rigid_alignment import (
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit,
    )

    with pytest.raises(TypeError):
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit.evaluate(
            alignment_features=("nose_tip",),
            evaluation_features=("nose_tip",),
            alignment_regions=("nose",),
            evaluation_regions=("nose",),
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
        )

# === PHASE 8 ITEM 10.6 EMPTY-EVIDENCE CORRECTIVE RED ===


@pytest.mark.parametrize(
    (
        "alignment_features",
        "evaluation_features",
        "alignment_regions",
        "evaluation_regions",
    ),
    (
        (
            (),
            ("chin",),
            ("orbital",),
            ("jaw_chin",),
        ),
        (
            ("left_eye_outer",),
            (),
            ("orbital",),
            ("jaw_chin",),
        ),
        (
            ("left_eye_outer",),
            ("chin",),
            (),
            ("jaw_chin",),
        ),
        (
            ("left_eye_outer",),
            ("chin",),
            ("orbital",),
            (),
        ),
    ),
)
def test_alignment_landmark_independence_rejects_missing_support_evidence(
    alignment_features,
    evaluation_features,
    alignment_regions,
    evaluation_regions,
):
    from CORE.atlas_canonical_head_metric_rigid_alignment import (
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit,
    )

    with pytest.raises(
        ValueError,
        match="must not be empty|evidence|support",
    ):
        AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit.evaluate(
            alignment_features=alignment_features,
            evaluation_features=evaluation_features,
            alignment_regions=alignment_regions,
            evaluation_regions=evaluation_regions,
        )
