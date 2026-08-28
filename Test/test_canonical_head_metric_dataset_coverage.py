import pytest


# === PHASE 8 ITEM 10.14 DATASET COVERAGE RED ===


def test_dataset_coverage_records_locked_dataset_level_fields():
    from CORE.atlas_canonical_head_metric_dataset_coverage import (
        AtlasCanonicalHeadMetricDatasetCoverage,
    )

    coverage = AtlasCanonicalHeadMetricDatasetCoverage(
        dataset_id="metric-gt-dataset-a",
        subject_ids=("subject-01", "subject-02"),
        view_ids=("front", "left", "right"),
        expressions=("NEUTRAL",),
        capture_conditions=("CONTROLLED_INDOOR",),
        same_subject_state="VERIFIED",
        session_relation_state="CROSS_SESSION_VERIFIED",
        scan_expression_state="NEUTRAL",
        image_expression_state="NEUTRAL",
        expression_compatibility="COMPATIBLE",
        scan_posture_state="UPRIGHT",
        image_head_pose_state="MULTIVIEW",
        posture_gravity_compatibility="COMPATIBLE",
        camera_calibration_availability="AVAILABLE",
        raw_scan_availability="AVAILABLE",
        source_image_multiview_availability="AVAILABLE",
        valid_facial_surface_coverage_state="PARTIAL",
        missing_surface_regions=("ears",),
        missing_ground_truth_states=("forehead_cranial",),
        failure_count=1,
        exclusion_count=0,
        provenance_reference="dataset coverage manifest",
    )

    assert coverage.dataset_id == "metric-gt-dataset-a"
    assert coverage.subject_count == 2
    assert coverage.view_count == 3
    assert coverage.failure_count == 1
    assert coverage.exclusion_count == 0


def test_subject_count_is_derived_from_unique_subject_ids():
    from CORE.atlas_canonical_head_metric_dataset_coverage import (
        AtlasCanonicalHeadMetricDatasetCoverage,
    )

    coverage = _coverage(
        subject_ids=("subject-01", "subject-02", "subject-03"),
    )

    assert coverage.subject_count == 3


def test_view_count_is_derived_from_unique_view_ids():
    from CORE.atlas_canonical_head_metric_dataset_coverage import (
        AtlasCanonicalHeadMetricDatasetCoverage,
    )

    coverage = _coverage(
        view_ids=("front", "left", "right", "three_quarter"),
    )

    assert coverage.view_count == 4


def test_rejects_duplicate_subject_ids():
    with pytest.raises(ValueError, match="subject_ids|unique|duplicate"):
        _coverage(
            subject_ids=("subject-01", "subject-01"),
        )


def test_rejects_duplicate_view_ids():
    with pytest.raises(ValueError, match="view_ids|unique|duplicate"):
        _coverage(
            view_ids=("front", "front"),
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "subject_ids",
        "view_ids",
        "expressions",
        "capture_conditions",
    ),
)
def test_rejects_empty_required_dataset_collections(field_name):
    with pytest.raises(ValueError, match=field_name):
        _coverage(**{field_name: ()})


def test_allows_missing_regions_and_missing_gt_states_to_be_empty():
    coverage = _coverage(
        missing_surface_regions=(),
        missing_ground_truth_states=(),
    )

    assert coverage.missing_surface_regions == ()
    assert coverage.missing_ground_truth_states == ()


@pytest.mark.parametrize(
    ("field_name", "state"),
    (
        ("same_subject_state", "MAYBE"),
        ("session_relation_state", "MAYBE"),
        ("expression_compatibility", "MAYBE"),
        ("posture_gravity_compatibility", "MAYBE"),
        ("camera_calibration_availability", "MAYBE"),
        ("raw_scan_availability", "MAYBE"),
        ("source_image_multiview_availability", "MAYBE"),
        ("valid_facial_surface_coverage_state", "MAYBE"),
    ),
)
def test_rejects_unknown_dataset_coverage_states(field_name, state):
    with pytest.raises(ValueError, match=field_name):
        _coverage(**{field_name: state})


def test_failure_and_exclusion_counts_must_be_nonnegative_integers():
    for field_name in ("failure_count", "exclusion_count"):
        with pytest.raises((TypeError, ValueError), match=field_name):
            _coverage(**{field_name: -1})

        with pytest.raises((TypeError, ValueError), match=field_name):
            _coverage(**{field_name: 1.5})


def test_dataset_coverage_requires_provenance():
    with pytest.raises(ValueError, match="provenance_reference"):
        _coverage(provenance_reference="   ")


def test_demographic_or_phenotypic_attributes_are_not_part_of_contract():
    coverage = _coverage()

    assert not hasattr(coverage, "race")
    assert not hasattr(coverage, "ethnicity")
    assert not hasattr(coverage, "phenotype")
    assert not hasattr(coverage, "demographic_profile")


def test_dataset_coverage_does_not_fabricate_metric_admissibility_or_phase_decision():
    coverage = _coverage()

    assert not hasattr(coverage, "metric_admissibility")
    assert not hasattr(coverage, "decision")
    assert not hasattr(coverage, "phase_9_authorized")
    assert not hasattr(coverage, "support_score")


def _coverage(**overrides):
    from CORE.atlas_canonical_head_metric_dataset_coverage import (
        AtlasCanonicalHeadMetricDatasetCoverage,
    )

    values = {
        "dataset_id": "metric-gt-dataset-a",
        "subject_ids": ("subject-01",),
        "view_ids": ("front",),
        "expressions": ("NEUTRAL",),
        "capture_conditions": ("CONTROLLED_INDOOR",),
        "same_subject_state": "VERIFIED",
        "session_relation_state": "UNRESOLVED",
        "scan_expression_state": "NEUTRAL",
        "image_expression_state": "NEUTRAL",
        "expression_compatibility": "UNRESOLVED",
        "scan_posture_state": "UNRESOLVED",
        "image_head_pose_state": "UNRESOLVED",
        "posture_gravity_compatibility": "UNRESOLVED",
        "camera_calibration_availability": "UNRESOLVED",
        "raw_scan_availability": "UNRESOLVED",
        "source_image_multiview_availability": "AVAILABLE",
        "valid_facial_surface_coverage_state": "UNRESOLVED",
        "missing_surface_regions": (),
        "missing_ground_truth_states": (),
        "failure_count": 0,
        "exclusion_count": 0,
        "provenance_reference": "dataset coverage manifest",
    }
    values.update(overrides)

    return AtlasCanonicalHeadMetricDatasetCoverage(**values)
