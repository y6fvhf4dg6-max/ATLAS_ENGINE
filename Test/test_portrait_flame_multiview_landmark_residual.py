import json
from pathlib import Path
import pickle

import numpy as np
import pytest

from CORE.atlas_portrait_flame_barycentric_landmark_evaluator import (
    AtlasPortraitFlameBarycentricEmbedding,
)
from CORE.atlas_portrait_flame_identity_geometry_evaluator import (
    AtlasPortraitFlameIdentityGeometryEvaluator,
)
from CORE.atlas_portrait_flame_multiview_landmark_residual import (
    AtlasPortraitFlameMultiviewLandmarkResidual,
    AtlasPortraitMediaPipeLandmarkObservation,
    _axis_angle_rotation_matrix,
    _flame_to_camera_axes,
)
from CORE.atlas_portrait_identity_recovery_v2_optimizer import (
    AtlasPortraitIdentityRecoveryV2ViewState,
)


def _state(
    pose=(0.0, 0.0, 0.0),
    translation=(0.0, 0.0, 10.0),
    focal_scale=(1.0, 1.0),
):
    return AtlasPortraitIdentityRecoveryV2ViewState(
        pose_radians=np.asarray(
            pose,
            dtype=np.float64,
        ),
        translation_xyz=np.asarray(
            translation,
            dtype=np.float64,
        ),
        log_focal_scale_xy=np.log(
            np.asarray(
                focal_scale,
                dtype=np.float64,
            )
        ),
    )


def test_json_loader_uses_w_minus_one_h_minus_one_pixel_contract(tmp_path):
    path = tmp_path / "landmarks.json"
    path.write_text(
        json.dumps(
            {
                "image_width": 101,
                "image_height": 51,
                "provider_id": "test",
                "landmarks": [
                    {
                        "id": 7,
                        "x": 0.5,
                        "y": 0.25,
                        "z": 0.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    observation = (
        AtlasPortraitMediaPipeLandmarkObservation.from_json_file(
            path
        )
    )

    np.testing.assert_allclose(
        observation.pixel_xy,
        np.array([[50.0, 12.5]]),
    )



def test_flame_to_camera_axes_flips_y_and_z_only():
    points = np.array(
        [
            [1.0, 2.0, 3.0],
            [-4.0, -5.0, 6.0],
        ],
        dtype=np.float64,
    )

    converted = _flame_to_camera_axes(points)

    np.testing.assert_array_equal(
        converted,
        np.array(
            [
                [1.0, -2.0, -3.0],
                [-4.0, 5.0, -6.0],
            ]
        ),
    )

    # Source geometry must remain untouched.
    np.testing.assert_array_equal(
        points,
        np.array(
            [
                [1.0, 2.0, 3.0],
                [-4.0, -5.0, 6.0],
            ]
        ),
    )


def test_flame_to_camera_axes_result_is_read_only():
    converted = _flame_to_camera_axes(
        np.array([[1.0, 2.0, 3.0]])
    )

    assert converted.flags.writeable is False


def test_axis_angle_zero_is_identity():
    np.testing.assert_allclose(
        _axis_angle_rotation_matrix(
            np.zeros(3)
        ),
        np.eye(3),
    )


def test_axis_angle_quarter_turn_about_z():
    rotation = _axis_angle_rotation_matrix(
        np.array([0.0, 0.0, np.pi / 2.0])
    )

    point = np.array([1.0, 0.0, 0.0])

    np.testing.assert_allclose(
        rotation @ point,
        np.array([0.0, 1.0, 0.0]),
        atol=1.0e-12,
    )


def test_residual_is_zero_when_projection_matches_observation():
    template = np.array(
        [
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=template,
        faces=np.array([[0, 1, 2]]),
        identity_directions=np.zeros((3, 3, 1)),
    )

    embedding = AtlasPortraitFlameBarycentricEmbedding(
        landmark_indices=np.array([10]),
        face_indices=np.array([0]),
        barycentric_coordinates=np.array(
            [[1.0, 0.0, 0.0]]
        ),
    )

    # Point [-1,0,0] translated to Z=10 and focal=100
    # projects to u=40, v=50 with principal point 50,50.
    observation = AtlasPortraitMediaPipeLandmarkObservation(
        image_width=101,
        image_height=101,
        landmark_ids=np.array([10]),
        pixel_xy=np.array([[40.0, 50.0]]),
        provider_id="test",
    )

    residual = AtlasPortraitFlameMultiviewLandmarkResidual(
        geometry_evaluator=evaluator,
        embedding=embedding,
        observations=(observation,),
        base_focal_pixels=(100.0,),
    )

    result = residual.evaluate(
        np.zeros(1),
        (_state(),),
    )

    np.testing.assert_allclose(
        result["static_landmarks"],
        np.zeros(2),
        atol=1.0e-12,
    )


def test_identity_changes_real_image_space_residual():
    template = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    dirs = np.zeros((3, 3, 1))
    dirs[0, 0, 0] = 1.0

    evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=template,
        faces=np.array([[0, 1, 2]]),
        identity_directions=dirs,
    )

    embedding = AtlasPortraitFlameBarycentricEmbedding(
        landmark_indices=np.array([10]),
        face_indices=np.array([0]),
        barycentric_coordinates=np.array(
            [[1.0, 0.0, 0.0]]
        ),
    )

    observation = AtlasPortraitMediaPipeLandmarkObservation(
        image_width=101,
        image_height=101,
        landmark_ids=np.array([10]),
        pixel_xy=np.array([[50.0, 50.0]]),
        provider_id="test",
    )

    residual = AtlasPortraitFlameMultiviewLandmarkResidual(
        geometry_evaluator=evaluator,
        embedding=embedding,
        observations=(observation,),
        base_focal_pixels=(100.0,),
    )

    zero = residual.evaluate(
        np.zeros(1),
        (_state(),),
    )["static_landmarks"]

    shifted = residual.evaluate(
        np.ones(1),
        (_state(),),
    )["static_landmarks"]

    assert np.linalg.norm(zero) == pytest.approx(0.0)
    assert np.linalg.norm(shifted) > 0.0


def test_real_recovered_json_contains_all_verified_105_ids():
    json_path = Path(
        "/Users/Kubi/ATLAS_PERSONAL_MULTIVIEW_SPIKE/EVIDENCE/"
        "phase8_10_personal_multiview_2026-08-26/"
        "recovered_landmarks/"
        "0B54D8DA-6E72-4E5F-9850-DC6250CAE81F.json"
    )

    observation = (
        AtlasPortraitMediaPipeLandmarkObservation.from_json_file(
            json_path
        )
    )

    with np.load(
        "Data/MODELS/FLAME/"
        "mediapipe_landmark_embedding.npz"
    ) as mapping:
        embedding = (
            AtlasPortraitFlameBarycentricEmbedding.from_npz_mapping(
                mapping
            )
        )

    selected = observation.select(
        embedding.landmark_indices
    )

    assert observation.landmark_ids.size == 478
    assert selected.shape == (105, 2)
    assert np.all(np.isfinite(selected))


def test_real_flame_and_real_json_generate_finite_210d_residual():
    with open(
        "Data/MODELS/FLAME/flame2023_Open.pkl",
        "rb",
    ) as stream:
        flame = pickle.load(
            stream,
            encoding="latin1",
        )

    evaluator = (
        AtlasPortraitFlameIdentityGeometryEvaluator.from_flame_mapping(
            flame=flame,
            identity_parameter_count=90,
        )
    )

    with np.load(
        "Data/MODELS/FLAME/"
        "mediapipe_landmark_embedding.npz"
    ) as mapping:
        embedding = (
            AtlasPortraitFlameBarycentricEmbedding.from_npz_mapping(
                mapping
            )
        )

    json_path = Path(
        "/Users/Kubi/ATLAS_PERSONAL_MULTIVIEW_SPIKE/EVIDENCE/"
        "phase8_10_personal_multiview_2026-08-26/"
        "recovered_landmarks/"
        "0B54D8DA-6E72-4E5F-9850-DC6250CAE81F.json"
    )

    observation = (
        AtlasPortraitMediaPipeLandmarkObservation.from_json_file(
            json_path
        )
    )

    residual = AtlasPortraitFlameMultiviewLandmarkResidual(
        geometry_evaluator=evaluator,
        embedding=embedding,
        observations=(observation,),
        base_focal_pixels=(1500.0,),
    )

    result = residual.evaluate(
        np.zeros(90),
        (
            _state(
                translation=(0.0, 0.0, 10.0),
            ),
        ),
    )

    assert result["static_landmarks"].shape == (210,)
    assert np.all(
        np.isfinite(
            result["static_landmarks"]
        )
    )
