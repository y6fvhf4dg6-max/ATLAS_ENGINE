from __future__ import annotations

import numpy as np

from CORE.atlas_portrait_flame_identity_geometry_evaluator import (
    AtlasPortraitFlameIdentityGeometryEvaluator,
)
from CORE.atlas_portrait_identity_recovery_v2_optimizer import (
    AtlasPortraitIdentityRecoveryV2ViewState,
)
from CORE.atlas_portrait_identity_recovery_v2_residual_evaluator import (
    AtlasPortraitIdentityRecoveryV2ResidualEvaluator,
)


def test_v2_residual_evaluator_owns_candidate_sensitive_photometric_channel():
    geometry_evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=np.array(
            [
                [-1.0, -1.0, 0.0],
                [1.0, -1.0, 0.0],
                [-1.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        faces=np.array(
            [[0, 1, 2]],
            dtype=np.int64,
        ),
        identity_directions=np.zeros(
            (3, 3, 1),
            dtype=np.float64,
        ),
    )

    source_front = np.zeros(
        (8, 8, 3),
        dtype=np.float64,
    )
    source_side = np.zeros(
        (8, 8, 3),
        dtype=np.float64,
    )

    for y in range(8):
        for x in range(8):
            source_front[y, x] = [
                x / 10.0,
                y / 10.0,
                0.1,
            ]
            source_side[y, x] = [
                y / 10.0,
                x / 10.0,
                0.2,
            ]

    evaluator = AtlasPortraitIdentityRecoveryV2ResidualEvaluator(
        geometry_evaluator=geometry_evaluator,
        base_fx_fy_by_view=(
            np.array([4.0, 4.0], dtype=np.float64),
            np.array([4.0, 4.0], dtype=np.float64),
        ),
        principal_xy_by_view=(
            np.array([3.5, 3.5], dtype=np.float64),
            np.array([3.5, 3.5], dtype=np.float64),
        ),
        source_rgb_by_view=(
            source_front,
            source_side,
        ),
        photometric_pairs=(
            (0, 1),
        ),
        photometric_vertex_indices_by_pair=(
            np.array([0, 1, 2], dtype=np.int64),
        ),
        photometric_baseline_confidence_by_pair=(
            np.array([1.0, 0.64, 0.25], dtype=np.float64),
        ),
        image_support_masks_by_view=(
            np.ones((8, 8), dtype=bool),
            np.ones((8, 8), dtype=bool),
        ),
    )

    states = (
        AtlasPortraitIdentityRecoveryV2ViewState(
            pose_radians=np.zeros(3),
            translation_xyz=np.array(
                [0.0, 0.0, 5.0],
                dtype=np.float64,
            ),
            log_focal_scale_xy=np.zeros(2),
        ),
        AtlasPortraitIdentityRecoveryV2ViewState(
            pose_radians=np.zeros(3),
            translation_xyz=np.array(
                [0.0, 0.0, 5.0],
                dtype=np.float64,
            ),
            log_focal_scale_xy=np.zeros(2),
        ),
    )

    residuals = evaluator(
        np.zeros(1, dtype=np.float64),
        states,
    )

    assert set(residuals) == {"photometric"}

    photometric = residuals["photometric"]

    # One accepted three-channel residual per frozen
    # canonical pair vertex.
    assert photometric.shape == (9,)
    assert np.all(np.isfinite(photometric))

    # Channel weighting is deliberately owned by the V2
    # objective, not by this residual evaluator.
    assert evaluator.applies_objective_channel_weighting is False


def test_v2_residual_evaluator_recomputes_photometric_residual_when_candidate_view_state_changes():
    geometry_evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=np.array(
            [
                [-1.0, -1.0, 0.0],
                [1.0, -1.0, 0.0],
                [-1.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        faces=np.array(
            [[0, 1, 2]],
            dtype=np.int64,
        ),
        identity_directions=np.zeros(
            (3, 3, 1),
            dtype=np.float64,
        ),
    )

    source_front = np.zeros(
        (10, 10, 3),
        dtype=np.float64,
    )
    source_side = np.zeros(
        (10, 10, 3),
        dtype=np.float64,
    )

    for y in range(10):
        for x in range(10):
            source_front[y, x] = [
                x / 12.0,
                y / 12.0,
                0.1,
            ]
            source_side[y, x] = [
                y / 12.0,
                x / 12.0,
                0.2,
            ]

    evaluator = AtlasPortraitIdentityRecoveryV2ResidualEvaluator(
        geometry_evaluator=geometry_evaluator,
        base_fx_fy_by_view=(
            np.array([4.0, 4.0], dtype=np.float64),
            np.array([4.0, 4.0], dtype=np.float64),
        ),
        principal_xy_by_view=(
            np.array([4.5, 4.5], dtype=np.float64),
            np.array([4.5, 4.5], dtype=np.float64),
        ),
        source_rgb_by_view=(
            source_front,
            source_side,
        ),
        photometric_pairs=((0, 1),),
        photometric_vertex_indices_by_pair=(
            np.array([0, 1, 2], dtype=np.int64),
        ),
        photometric_baseline_confidence_by_pair=(
            np.array([1.0, 0.64, 0.25], dtype=np.float64),
        ),
        image_support_masks_by_view=(
            np.ones((10, 10), dtype=bool),
            np.ones((10, 10), dtype=bool),
        ),
    )

    front_state = AtlasPortraitIdentityRecoveryV2ViewState(
        pose_radians=np.zeros(3),
        translation_xyz=np.array(
            [0.0, 0.0, 5.0],
            dtype=np.float64,
        ),
        log_focal_scale_xy=np.zeros(2),
    )

    side_first = AtlasPortraitIdentityRecoveryV2ViewState(
        pose_radians=np.zeros(3),
        translation_xyz=np.array(
            [0.0, 0.0, 5.0],
            dtype=np.float64,
        ),
        log_focal_scale_xy=np.zeros(2),
    )

    side_second = AtlasPortraitIdentityRecoveryV2ViewState(
        pose_radians=np.zeros(3),
        translation_xyz=np.array(
            [0.5, 0.0, 5.0],
            dtype=np.float64,
        ),
        log_focal_scale_xy=np.zeros(2),
    )

    identity = np.zeros(
        1,
        dtype=np.float64,
    )

    first = evaluator(
        identity,
        (front_state, side_first),
    )["photometric"]

    second = evaluator(
        identity,
        (front_state, side_second),
    )["photometric"]

    # Frozen D1 accepted support controls residual cardinality.
    assert first.shape == (9,)
    assert second.shape == (9,)

    assert np.all(np.isfinite(first))
    assert np.all(np.isfinite(second))

    # Changing a live candidate camera/view state must alter
    # reprojection and image sampling; persisted D1 RGB must
    # therefore not be reused as a static optimizer residual.
    assert not np.allclose(
        first,
        second,
        atol=1.0e-12,
        rtol=0.0,
    )


def _make_minimal_d2_owner_inputs():
    geometry_evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=np.array(
            [
                [-1.0, -1.0, 0.0],
                [1.0, -1.0, 0.0],
                [-1.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        faces=np.array(
            [[0, 1, 2]],
            dtype=np.int64,
        ),
        identity_directions=np.zeros(
            (3, 3, 1),
            dtype=np.float64,
        ),
    )

    return dict(
        geometry_evaluator=geometry_evaluator,
        base_fx_fy_by_view=(
            np.array([4.0, 4.0], dtype=np.float64),
            np.array([4.0, 4.0], dtype=np.float64),
        ),
        principal_xy_by_view=(
            np.array([3.5, 3.5], dtype=np.float64),
            np.array([3.5, 3.5], dtype=np.float64),
        ),
        source_rgb_by_view=(
            np.zeros((8, 8, 3), dtype=np.float64),
            np.zeros((8, 8, 3), dtype=np.float64),
        ),
        photometric_pairs=((0, 1),),
        photometric_vertex_indices_by_pair=(
            np.array([0, 1, 2], dtype=np.int64),
        ),
        photometric_baseline_confidence_by_pair=(
            np.array([1.0, 0.64, 0.25], dtype=np.float64),
        ),
        image_support_masks_by_view=(
            np.ones((8, 8), dtype=bool),
            np.ones((8, 8), dtype=bool),
        ),
    )


def test_v2_residual_evaluator_rejects_pair_support_contract_violations():
    kwargs = _make_minimal_d2_owner_inputs()

    duplicate_kwargs = dict(kwargs)
    duplicate_kwargs[
        "photometric_vertex_indices_by_pair"
    ] = (
        np.array([0, 0, 2], dtype=np.int64),
    )

    try:
        AtlasPortraitIdentityRecoveryV2ResidualEvaluator(
            **duplicate_kwargs
        )
    except ValueError as error:
        assert "unique" in str(error)
    else:
        raise AssertionError(
            "duplicate frozen pair support must be rejected"
        )

    mismatch_kwargs = dict(kwargs)
    mismatch_kwargs[
        "photometric_baseline_confidence_by_pair"
    ] = (
        np.array([1.0, 0.64], dtype=np.float64),
    )

    try:
        AtlasPortraitIdentityRecoveryV2ResidualEvaluator(
            **mismatch_kwargs
        )
    except ValueError as error:
        assert "confidence" in str(error)
    else:
        raise AssertionError(
            "confidence cardinality mismatch must be rejected"
        )


def test_v2_residual_evaluator_rejects_view_state_count_mismatch():
    evaluator = AtlasPortraitIdentityRecoveryV2ResidualEvaluator(
        **_make_minimal_d2_owner_inputs()
    )

    one_state = (
        AtlasPortraitIdentityRecoveryV2ViewState(
            pose_radians=np.zeros(3),
            translation_xyz=np.array(
                [0.0, 0.0, 5.0],
                dtype=np.float64,
            ),
            log_focal_scale_xy=np.zeros(2),
        ),
    )

    try:
        evaluator(
            np.zeros(1, dtype=np.float64),
            one_state,
        )
    except ValueError as error:
        assert "view state count" in str(error)
    else:
        raise AssertionError(
            "view-state count mismatch must be rejected"
        )


def test_v2_residual_evaluator_pair_support_fixes_residual_cardinality():
    kwargs = _make_minimal_d2_owner_inputs()

    kwargs["photometric_vertex_indices_by_pair"] = (
        np.array([0, 2], dtype=np.int64),
    )
    kwargs["photometric_baseline_confidence_by_pair"] = (
        np.array([1.0, 0.25], dtype=np.float64),
    )

    evaluator = AtlasPortraitIdentityRecoveryV2ResidualEvaluator(
        **kwargs
    )

    states = tuple(
        AtlasPortraitIdentityRecoveryV2ViewState(
            pose_radians=np.zeros(3),
            translation_xyz=np.array(
                [0.0, 0.0, 5.0],
                dtype=np.float64,
            ),
            log_focal_scale_xy=np.zeros(2),
        )
        for _ in range(2)
    )

    residual = evaluator(
        np.zeros(1, dtype=np.float64),
        states,
    )["photometric"]

    assert residual.shape == (2 * 3,)


def test_v2_optimizer_consumes_candidate_sensitive_photometric_owner_end_to_end():
    from CORE.atlas_portrait_identity_recovery_v2_optimizer import (
        AtlasPortraitIdentityRecoveryV2Optimizer,
    )
    from CORE.atlas_portrait_identity_recovery_v2_spec import (
        AtlasPortraitIdentityRecoveryV2Spec,
    )

    kwargs = _make_minimal_d2_owner_inputs()

    source_front = np.zeros(
        (8, 8, 3),
        dtype=np.float64,
    )
    source_side = np.zeros(
        (8, 8, 3),
        dtype=np.float64,
    )

    for y in range(8):
        for x in range(8):
            source_front[y, x] = [
                x / 10.0,
                y / 10.0,
                0.1,
            ]
            source_side[y, x] = [
                y / 10.0,
                x / 10.0,
                0.2,
            ]

    kwargs["source_rgb_by_view"] = (
        source_front,
        source_side,
    )

    evaluator = AtlasPortraitIdentityRecoveryV2ResidualEvaluator(
        **kwargs
    )

    spec = AtlasPortraitIdentityRecoveryV2Spec(
        use_static_landmarks=False,
        use_dense_landmarks=False,
        use_face_oval=False,
        use_silhouette=False,
        use_photometric=True,
        use_surface_normals=False,
        use_identity_prior=False,
        photometric_weight=1.0,
    )

    optimizer = AtlasPortraitIdentityRecoveryV2Optimizer(
        spec=spec,
        identity_dimension=1,
        max_nfev=1,
    )

    states = (
        AtlasPortraitIdentityRecoveryV2ViewState(
            pose_radians=np.zeros(3),
            translation_xyz=np.array(
                [0.0, 0.0, 5.0],
                dtype=np.float64,
            ),
            log_focal_scale_xy=np.zeros(2),
        ),
        AtlasPortraitIdentityRecoveryV2ViewState(
            pose_radians=np.zeros(3),
            translation_xyz=np.array(
                [0.0, 0.0, 5.0],
                dtype=np.float64,
            ),
            log_focal_scale_xy=np.zeros(2),
        ),
    )

    initial_identity = np.zeros(
        1,
        dtype=np.float64,
    )

    direct = evaluator(
        initial_identity,
        states,
    )["photometric"]

    result = optimizer.fit(
        initial_identity=initial_identity,
        initial_view_states=states,
        residual_evaluator=evaluator,
    )

    # Three frozen pair vertices x RGB.
    assert direct.shape == (9,)
    assert result.residual_vector.shape == (9,)

    assert np.all(np.isfinite(result.residual_vector))
    assert np.isfinite(result.cost)

    # With max_nfev=1, the final optimizer objective must be
    # the same unweighted photometric channel produced by the
    # integration owner because photometric_weight == 1.
    np.testing.assert_allclose(
        result.residual_vector,
        direct,
        atol=1.0e-12,
        rtol=0.0,
    )

    # D2 geometry/evidence ownership remains outside optimizer.
    assert evaluator.applies_objective_channel_weighting is False
