import numpy as np
import pytest

from CORE.atlas_portrait_identity_recovery_v2_objective import (
    AtlasPortraitIdentityRecoveryV2Objective,
)
from CORE.atlas_portrait_identity_recovery_v2_spec import (
    AtlasPortraitIdentityRecoveryV2Spec,
)


def _full_residuals():
    return {
        "static_landmarks": np.array([[1.0, -2.0]]),
        "dense_landmarks": np.array([3.0]),
        "face_oval": np.array([4.0, -5.0]),
        "silhouette": np.array([6.0]),
        "photometric": np.array([7.0, -8.0]),
        "surface_normals": np.array([[9.0, 10.0, -11.0]]),
        "identity_prior": np.array([12.0, -13.0]),
    }


def test_compose_uses_stable_channel_order():
    spec = AtlasPortraitIdentityRecoveryV2Spec()
    result = AtlasPortraitIdentityRecoveryV2Objective.compose(
        spec=spec,
        residuals_by_channel=_full_residuals(),
    )

    np.testing.assert_array_equal(
        result.residual_vector,
        np.array([
            1.0, -2.0,
            3.0,
            4.0, -5.0,
            6.0,
            7.0, -8.0,
            9.0, 10.0, -11.0,
            12.0, -13.0,
        ]),
    )


def test_compose_applies_square_root_weighting():
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        static_landmark_weight=4.0,
        dense_landmark_weight=9.0,
        face_oval_weight=16.0,
        silhouette_weight=25.0,
        photometric_weight=36.0,
        surface_normal_weight=49.0,
        identity_prior_weight=64.0,
    )

    residuals = {
        name: np.ones(1)
        for name in spec.enabled_channels
    }

    result = AtlasPortraitIdentityRecoveryV2Objective.compose(
        spec=spec,
        residuals_by_channel=residuals,
    )

    np.testing.assert_array_equal(
        result.residual_vector,
        np.array([2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]),
    )


def test_reports_channel_sizes_and_weighted_sse():
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        static_landmark_weight=4.0,
        use_dense_landmarks=False,
        use_face_oval=False,
        use_silhouette=False,
        use_photometric=False,
        use_surface_normals=False,
        use_identity_prior=False,
    )

    result = AtlasPortraitIdentityRecoveryV2Objective.compose(
        spec=spec,
        residuals_by_channel={
            "static_landmarks": np.array([1.0, 2.0, 3.0]),
        },
    )

    assert result.channel_sizes == {"static_landmarks": 3}
    assert result.weighted_channel_sse == {
        "static_landmarks": pytest.approx(56.0),
    }
    assert result.total_sse == pytest.approx(56.0)
    assert result.residual_count == 3


def test_disabled_channels_are_excluded_cleanly():
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        use_photometric=False,
        use_surface_normals=False,
    )

    residuals = _full_residuals()
    residuals.pop("photometric")
    residuals.pop("surface_normals")

    result = AtlasPortraitIdentityRecoveryV2Objective.compose(
        spec=spec,
        residuals_by_channel=residuals,
    )

    assert "photometric" not in result.channel_sizes
    assert "surface_normals" not in result.channel_sizes


def test_missing_enabled_channel_is_rejected():
    spec = AtlasPortraitIdentityRecoveryV2Spec()
    residuals = _full_residuals()
    residuals.pop("surface_normals")

    with pytest.raises(
        ValueError,
        match="missing enabled residual channels: surface_normals",
    ):
        AtlasPortraitIdentityRecoveryV2Objective.compose(
            spec=spec,
            residuals_by_channel=residuals,
        )


def test_unknown_channel_is_rejected():
    spec = AtlasPortraitIdentityRecoveryV2Spec()
    residuals = _full_residuals()
    residuals["mystery"] = np.array([1.0])

    with pytest.raises(
        ValueError,
        match="unknown residual channels: mystery",
    ):
        AtlasPortraitIdentityRecoveryV2Objective.compose(
            spec=spec,
            residuals_by_channel=residuals,
        )


def test_residual_for_disabled_channel_is_rejected():
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        use_photometric=False,
    )
    residuals = _full_residuals()

    with pytest.raises(
        ValueError,
        match="residuals supplied for disabled channels: photometric",
    ):
        AtlasPortraitIdentityRecoveryV2Objective.compose(
            spec=spec,
            residuals_by_channel=residuals,
        )


@pytest.mark.parametrize(
    "bad",
    [
        np.array([]),
        np.array([np.nan]),
        np.array([np.inf]),
        np.array([-np.inf]),
    ],
)
def test_invalid_enabled_residual_is_rejected(bad):
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        use_dense_landmarks=False,
        use_face_oval=False,
        use_silhouette=False,
        use_photometric=False,
        use_surface_normals=False,
        use_identity_prior=False,
    )

    expected = (
        "must not be empty"
        if bad.size == 0
        else "must contain only finite values"
    )

    with pytest.raises(ValueError, match=expected):
        AtlasPortraitIdentityRecoveryV2Objective.compose(
            spec=spec,
            residuals_by_channel={
                "static_landmarks": bad,
            },
        )


def test_result_residual_vector_is_read_only():
    spec = AtlasPortraitIdentityRecoveryV2Spec()
    result = AtlasPortraitIdentityRecoveryV2Objective.compose(
        spec=spec,
        residuals_by_channel=_full_residuals(),
    )

    assert result.residual_vector.flags.writeable is False


def test_zero_weight_channel_remains_present_but_contributes_zero_sse():
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        photometric_weight=0.0,
    )

    result = AtlasPortraitIdentityRecoveryV2Objective.compose(
        spec=spec,
        residuals_by_channel=_full_residuals(),
    )

    assert result.channel_sizes["photometric"] == 2
    assert result.weighted_channel_sse["photometric"] == 0.0
