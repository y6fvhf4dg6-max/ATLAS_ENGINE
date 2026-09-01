import numpy as np
import pytest

from CORE.atlas_portrait_identity_recovery_v2_optimizer import (
    AtlasPortraitIdentityRecoveryV2Optimizer,
    AtlasPortraitIdentityRecoveryV2ViewState,
)
from CORE.atlas_portrait_identity_recovery_v2_spec import (
    AtlasPortraitIdentityRecoveryV2Spec,
)


def _spec():
    return AtlasPortraitIdentityRecoveryV2Spec(
        use_static_landmarks=True,
        use_dense_landmarks=False,
        use_face_oval=False,
        use_silhouette=False,
        use_photometric=False,
        use_surface_normals=False,
        use_identity_prior=True,
        identity_prior_weight=0.0,
    )


def _state(
    pose=(0.0, 0.0, 0.0),
    translation=(0.0, 0.0, 10.0),
    focal_scale=(1.0, 1.0),
):
    return AtlasPortraitIdentityRecoveryV2ViewState(
        pose_radians=np.asarray(pose, dtype=np.float64),
        translation_xyz=np.asarray(
            translation,
            dtype=np.float64,
        ),
        log_focal_scale_xy=np.log(
            np.asarray(focal_scale, dtype=np.float64)
        ),
    )


def test_view_state_exposes_positive_focal_scale():
    state = _state(focal_scale=(1.25, 0.8))

    np.testing.assert_allclose(
        state.focal_scale_xy,
        np.array([1.25, 0.8]),
    )


def test_pack_unpack_roundtrip_preserves_shared_identity_and_views():
    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=_spec(),
        identity_dimension=2,
    )

    identity = np.array([0.3, -0.4])
    views = (
        _state(
            pose=(0.1, 0.2, 0.3),
            translation=(1.0, 2.0, 10.0),
            focal_scale=(1.1, 0.9),
        ),
        _state(
            pose=(-0.1, -0.2, 0.15),
            translation=(-1.0, 3.0, 12.0),
            focal_scale=(0.8, 1.2),
        ),
    )

    packed = optimizer.pack(
        identity_vector=identity,
        view_states=views,
    )
    recovered_identity, recovered_views = optimizer.unpack(
        packed,
        view_count=2,
    )

    np.testing.assert_allclose(
        recovered_identity,
        identity,
    )

    for expected, recovered in zip(
        views,
        recovered_views,
    ):
        np.testing.assert_allclose(
            recovered.pose_radians,
            expected.pose_radians,
        )
        np.testing.assert_allclose(
            recovered.translation_xyz,
            expected.translation_xyz,
        )
        np.testing.assert_allclose(
            recovered.focal_scale_xy,
            expected.focal_scale_xy,
        )


def test_parameter_bounds_include_identity_pose_translation_and_focal():
    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=_spec(),
        identity_dimension=3,
        identity_bound=3.0,
        pose_bound_degrees=60.0,
        translation_bound=100.0,
        focal_scale_min=0.5,
        focal_scale_max=2.0,
    )

    lower, upper = optimizer.parameter_bounds(
        view_count=2,
    )

    assert lower.shape == upper.shape == (19,)
    np.testing.assert_array_equal(
        lower[:3],
        np.array([-3.0, -3.0, -3.0]),
    )
    np.testing.assert_array_equal(
        upper[:3],
        np.array([3.0, 3.0, 3.0]),
    )


def test_translation_z_lower_bound_is_positive_and_explicit():
    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=_spec(),
        identity_dimension=2,
        translation_bound=100.0,
        translation_z_min=0.25,
    )

    lower, upper = optimizer.parameter_bounds(
        view_count=1,
    )

    view_offset = 2

    assert lower[view_offset + 3] == pytest.approx(-100.0)
    assert lower[view_offset + 4] == pytest.approx(-100.0)
    assert lower[view_offset + 5] == pytest.approx(0.25)
    assert upper[view_offset + 5] == pytest.approx(100.0)


@pytest.mark.parametrize(
    "translation_z_min",
    [0.0, -1.0],
)
def test_nonpositive_translation_z_min_is_rejected(
    translation_z_min,
):
    with pytest.raises(
        ValueError,
        match="translation_z_min must be positive",
    ):
        AtlasPortraitIdentityRecoveryV2Optimizer(
            spec=_spec(),
            identity_dimension=2,
            translation_z_min=translation_z_min,
        )


def test_translation_z_min_must_be_below_translation_bound():
    with pytest.raises(
        ValueError,
        match="smaller than translation_bound",
    ):
        AtlasPortraitIdentityRecoveryV2Optimizer(
            spec=_spec(),
            identity_dimension=2,
            translation_bound=1.0,
            translation_z_min=1.0,
        )



def test_optimizer_recovers_shared_identity_and_per_view_state():
    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=_spec(),
        identity_dimension=2,
        identity_bound=3.0,
        translation_bound=100.0,
        focal_scale_min=0.5,
        focal_scale_max=2.0,
        max_nfev=300,
    )

    target_identity = np.array([0.7, -0.35])

    target_views = (
        _state(
            pose=(0.05, 0.10, -0.03),
            translation=(1.0, -2.0, 15.0),
            focal_scale=(1.10, 0.95),
        ),
        _state(
            pose=(-0.04, -0.12, 0.02),
            translation=(-1.5, 1.0, 18.0),
            focal_scale=(0.90, 1.05),
        ),
    )

    target_blocks = [target_identity]
    for view in target_views:
        target_blocks.extend(
            [
                view.pose_radians,
                view.translation_xyz,
                view.log_focal_scale_xy,
            ]
        )
    target = np.concatenate(target_blocks)

    def residual_evaluator(identity, views):
        blocks = [identity]
        for view in views:
            blocks.extend(
                [
                    view.pose_radians,
                    view.translation_xyz,
                    view.log_focal_scale_xy,
                ]
            )

        current = np.concatenate(blocks)

        return {
            "static_landmarks": current - target,
        }

    result = optimizer.fit(
        initial_identity=np.zeros(2),
        initial_view_states=(
            _state(),
            _state(),
        ),
        residual_evaluator=residual_evaluator,
    )

    assert result.success is True
    np.testing.assert_allclose(
        result.identity_vector,
        target_identity,
        atol=1.0e-7,
    )

    for recovered, expected in zip(
        result.view_states,
        target_views,
    ):
        np.testing.assert_allclose(
            recovered.pose_radians,
            expected.pose_radians,
            atol=1.0e-7,
        )
        np.testing.assert_allclose(
            recovered.translation_xyz,
            expected.translation_xyz,
            atol=1.0e-7,
        )
        np.testing.assert_allclose(
            recovered.focal_scale_xy,
            expected.focal_scale_xy,
            atol=1.0e-7,
        )

    assert np.linalg.norm(result.residual_vector) < 1.0e-6


def test_native_prior_is_injected_by_optimizer():
    spec = AtlasPortraitIdentityRecoveryV2Spec(
        use_static_landmarks=True,
        use_dense_landmarks=False,
        use_face_oval=False,
        use_silhouette=False,
        use_photometric=False,
        use_surface_normals=False,
        use_identity_prior=True,
        identity_prior_weight=1.0,
    )

    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=spec,
        identity_dimension=2,
    )

    def evaluator(identity, views):
        return {
            "static_landmarks": np.zeros(1),
        }

    result = optimizer.fit(
        initial_identity=np.array([1.0, -1.0]),
        initial_view_states=(_state(),),
        residual_evaluator=evaluator,
    )

    np.testing.assert_allclose(
        result.identity_vector,
        np.zeros(2),
        atol=1.0e-7,
    )


def test_external_identity_prior_residual_is_rejected():
    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=_spec(),
        identity_dimension=2,
    )

    def evaluator(identity, views):
        return {
            "static_landmarks": np.zeros(1),
            "identity_prior": np.zeros(2),
        }

    with pytest.raises(
        ValueError,
        match="identity_prior residual is owned by the optimizer",
    ):
        optimizer.fit(
            initial_identity=np.zeros(2),
            initial_view_states=(_state(),),
            residual_evaluator=evaluator,
        )


def test_initial_identity_outside_bounds_is_rejected():
    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=_spec(),
        identity_dimension=2,
        identity_bound=3.0,
    )

    def evaluator(identity, views):
        return {
            "static_landmarks": np.zeros(1),
        }

    with pytest.raises(
        ValueError,
        match="outside optimizer bounds",
    ):
        optimizer.fit(
            initial_identity=np.array([4.0, 0.0]),
            initial_view_states=(_state(),),
            residual_evaluator=evaluator,
        )


def test_identity_is_global_not_stored_per_view():
    state = _state()

    assert not hasattr(state, "identity_vector")
