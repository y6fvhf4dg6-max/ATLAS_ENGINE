import pytest

from CORE.atlas_canonical_head_shared_identity_fit_observation import (
    AtlasCanonicalHeadSharedIdentityFitObservation,
)


def _observation(**overrides):
    values = {
        "observation_id": "flame-subject-01-shared-90d",
        "candidate_id": "flame-2023-open",
        "subject_id": "subject_01",
        "view_ids": (
            "front",
            "side_a",
            "side_b",
        ),
        "shared_identity_component_count": 90,
        "mean_reprojection_iod_nme": 0.03,
        "mean_reprojection_bbox_nme": 0.008,
        "per_view_reprojection_iod_nme": (
            0.028,
            0.031,
            0.032,
        ),
        "identity_coefficient_l2_norm": 6.2,
        "identity_bound_hit_count": 1,
        "optimizer_success": True,
        "processing_time_seconds": 3.5,
        "expression_fixed_neutral": True,
        "projection_model": "weak_perspective",
    }
    values.update(overrides)
    return AtlasCanonicalHeadSharedIdentityFitObservation(
        **values
    )


def test_preserves_shared_identity_fit_raw_evidence():
    observation = _observation()

    assert observation.candidate_id == "flame-2023-open"
    assert observation.subject_id == "subject_01"
    assert observation.view_count == 3
    assert observation.shared_identity_component_count == 90
    assert observation.optimizer_success is True
    assert observation.expression_fixed_neutral is True
    assert observation.projection_model == "weak_perspective"


def test_view_count_is_derived_from_view_ids():
    observation = _observation(
        view_ids=("front", "side_a"),
        per_view_reprojection_iod_nme=(
            0.028,
            0.031,
        ),
    )

    assert observation.view_count == 2


def test_rejects_duplicate_view_ids():
    with pytest.raises(ValueError):
        _observation(
            view_ids=(
                "front",
                "front",
                "side_b",
            )
        )


def test_rejects_per_view_metric_count_mismatch():
    with pytest.raises(ValueError):
        _observation(
            per_view_reprojection_iod_nme=(
                0.028,
                0.031,
            )
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "mean_reprojection_iod_nme",
        "mean_reprojection_bbox_nme",
        "identity_coefficient_l2_norm",
        "processing_time_seconds",
    ),
)
def test_rejects_negative_raw_metrics(field_name):
    with pytest.raises(ValueError):
        _observation(
            **{
                field_name: -0.001,
            }
        )


def test_rejects_nonpositive_identity_component_count():
    with pytest.raises(ValueError):
        _observation(
            shared_identity_component_count=0,
        )


def test_rejects_negative_bound_hit_count():
    with pytest.raises(ValueError):
        _observation(
            identity_bound_hit_count=-1,
        )


def test_rejects_bound_hits_above_identity_component_count():
    with pytest.raises(ValueError):
        _observation(
            identity_bound_hit_count=91,
        )


def test_rejects_non_boolean_state_flags():
    with pytest.raises(TypeError):
        _observation(
            optimizer_success=1,
        )

    with pytest.raises(TypeError):
        _observation(
            expression_fixed_neutral=1,
        )


def test_rejects_unsupported_projection_model():
    with pytest.raises(ValueError):
        _observation(
            projection_model="perspective",
        )


def test_shared_fit_observation_does_not_expose_by_construction_consistency_score():
    observation = _observation()

    assert not hasattr(
        observation,
        "cross_view_identity_shape_nme",
    )
    assert not hasattr(
        observation,
        "multi_view_consistency",
    )
    assert not hasattr(
        observation,
        "support_score",
    )
    assert not hasattr(
        observation,
        "decision",
    )
    assert not hasattr(
        observation,
        "phase_9_authorized",
    )


def test_observation_is_immutable():
    observation = _observation()

    with pytest.raises(
        (
            AttributeError,
            TypeError,
        )
    ):
        observation.optimizer_success = False
