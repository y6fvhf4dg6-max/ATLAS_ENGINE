import pytest

from CORE.atlas_portrait_identity_recovery_v2_spec import (
    AtlasPortraitIdentityRecoveryV2Spec,
)


def test_default_contract_enables_full_v2_evidence_stack():
    spec = AtlasPortraitIdentityRecoveryV2Spec()

    assert spec.shared_identity_across_views is True
    assert spec.separate_pose_per_view is True
    assert spec.separate_camera_per_view is True
    assert spec.neutral_expression_for_identity_fit is True
    assert spec.camera_model == "perspective"

    assert spec.enabled_channels == (
        "static_landmarks",
        "dense_landmarks",
        "face_oval",
        "silhouette",
        "photometric",
        "surface_normals",
        "identity_prior",
    )


def test_weights_are_exposed_by_channel():
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        static_landmark_weight=0.5,
        dense_landmark_weight=2.0,
        face_oval_weight=3.0,
        silhouette_weight=4.0,
        photometric_weight=5.0,
        surface_normal_weight=6.0,
        identity_prior_weight=7.0,
    )

    assert spec.weights == {
        "static_landmarks": 0.5,
        "dense_landmarks": 2.0,
        "face_oval": 3.0,
        "silhouette": 4.0,
        "photometric": 5.0,
        "surface_normals": 6.0,
        "identity_prior": 7.0,
    }


@pytest.mark.parametrize(
    "field",
    [
        "static_landmark_weight",
        "dense_landmark_weight",
        "face_oval_weight",
        "silhouette_weight",
        "photometric_weight",
        "surface_normal_weight",
        "identity_prior_weight",
    ],
)
def test_negative_weight_is_rejected(field):
    kwargs = {field: -1.0}

    with pytest.raises(ValueError, match="must be non-negative"):
        AtlasPortraitIdentityRecoveryV2Spec(**kwargs)


def test_invalid_camera_model_is_rejected():
    with pytest.raises(ValueError, match="camera_model"):
        AtlasPortraitIdentityRecoveryV2Spec(camera_model="orthographic")


def test_shared_identity_cannot_be_disabled():
    with pytest.raises(ValueError, match="shared identity"):
        AtlasPortraitIdentityRecoveryV2Spec(
            shared_identity_across_views=False
        )


def test_identity_fit_must_remain_neutral():
    with pytest.raises(ValueError, match="neutral expression"):
        AtlasPortraitIdentityRecoveryV2Spec(
            neutral_expression_for_identity_fit=False
        )
