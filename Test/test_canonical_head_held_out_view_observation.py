import pytest

from CORE.atlas_canonical_head_held_out_view_observation import (
    AtlasCanonicalHeadHeldOutViewObservation,
)


def _observation(**overrides):
    values = {
        "observation_id": "flame-subject-01-front-side-a-to-side-b",
        "candidate_id": "flame-2023-open",
        "subject_id": "subject_01",
        "training_view_ids": (
            "front",
            "side_a",
        ),
        "held_out_view_id": "side_b",
        "shared_identity_component_count": 90,
        "identity_locked": True,
        "held_out_pose_camera_only": True,
        "held_out_reprojection_iod_nme": 0.034,
        "held_out_reprojection_bbox_nme": 0.009,
        "optimizer_success": True,
        "processing_time_seconds": 0.8,
        "expression_fixed_neutral": True,
        "projection_model": "weak_perspective",
    }
    values.update(overrides)

    return AtlasCanonicalHeadHeldOutViewObservation(
        **values
    )


def test_preserves_held_out_raw_evidence():
    observation = _observation()

    assert observation.candidate_id == "flame-2023-open"
    assert observation.subject_id == "subject_01"
    assert observation.training_view_count == 2
    assert observation.held_out_view_id == "side_b"
    assert observation.shared_identity_component_count == 90
    assert observation.identity_locked is True
    assert observation.held_out_pose_camera_only is True
    assert observation.optimizer_success is True
    assert observation.expression_fixed_neutral is True
    assert observation.projection_model == "weak_perspective"


def test_rejects_empty_training_views():
    with pytest.raises(ValueError):
        _observation(
            training_view_ids=(),
        )


def test_rejects_duplicate_training_views():
    with pytest.raises(ValueError):
        _observation(
            training_view_ids=(
                "front",
                "front",
            ),
        )


def test_held_out_view_must_not_be_in_training_views():
    with pytest.raises(ValueError):
        _observation(
            held_out_view_id="front",
        )


def test_rejects_nonpositive_identity_component_count():
    with pytest.raises(ValueError):
        _observation(
            shared_identity_component_count=0,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "held_out_reprojection_iod_nme",
        "held_out_reprojection_bbox_nme",
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


@pytest.mark.parametrize(
    "field_name",
    (
        "identity_locked",
        "held_out_pose_camera_only",
        "optimizer_success",
        "expression_fixed_neutral",
    ),
)
def test_state_flags_must_be_boolean(field_name):
    with pytest.raises(TypeError):
        _observation(
            **{
                field_name: 1,
            }
        )


def test_identity_must_be_locked_for_held_out_validation():
    with pytest.raises(ValueError):
        _observation(
            identity_locked=False,
        )


def test_held_out_fit_must_be_pose_camera_only():
    with pytest.raises(ValueError):
        _observation(
            held_out_pose_camera_only=False,
        )


def test_rejects_unsupported_projection_model():
    with pytest.raises(ValueError):
        _observation(
            projection_model="perspective",
        )


def test_held_out_observation_does_not_expose_support_or_decision():
    observation = _observation()

    assert not hasattr(
        observation,
        "identity_preservation_support",
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
