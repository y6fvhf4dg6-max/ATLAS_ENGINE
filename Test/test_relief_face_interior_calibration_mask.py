from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_face_interior_calibration_mask import (
    AtlasReliefFaceInteriorCalibrationMask,
)


def test_output_shape_and_dtype_are_preserved() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float32,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
    )

    assert result.shape == subject_mask.shape
    assert result.dtype == np.float64


def test_output_is_bounded_to_unit_interval() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
    )

    assert float(result.min()) >= 0.0
    assert float(result.max()) <= 1.0


def test_output_is_zero_outside_face_bounds() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    face_bounds = (
        20,
        120,
        25,
        95,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=face_bounds,
    )

    top, bottom, left, right = face_bounds

    outside = np.ones_like(
        subject_mask,
        dtype=bool,
    )
    outside[
        top:bottom + 1,
        left:right + 1,
    ] = False

    assert np.allclose(
        result[outside],
        0.0,
        atol=1e-12,
    )


def test_center_face_is_more_active_than_side_edges() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
    )

    center = float(
        result[65, 60]
    )

    left_edge = float(
        result[65, 27]
    )

    right_edge = float(
        result[65, 93]
    )

    assert center > left_edge
    assert center > right_edge


def test_forehead_and_cheeks_remain_active() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
    )

    forehead = float(
        result[45, 60]
    )

    left_cheek = float(
        result[72, 45]
    )

    right_cheek = float(
        result[72, 75]
    )

    assert forehead > 0.20
    assert left_cheek > 0.20
    assert right_cheek > 0.20


def test_eye_glasses_band_is_suppressed() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
        eye_suppression_strength=0.90,
    )

    forehead = float(
        result[42, 60]
    )

    eye_band = float(
        result[58, 60]
    )

    assert eye_band < forehead


def test_mouth_band_is_suppressed() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
        mouth_suppression_strength=0.90,
    )

    cheek = float(
        result[70, 48]
    )

    mouth = float(
        result[92, 60]
    )

    assert mouth < cheek


def test_lower_neck_region_is_excluded() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
    )

    chin = float(
        result[100, 60]
    )

    lower_neck = float(
        result[118, 60]
    )

    assert chin > lower_neck


def test_subject_mask_limits_calibration_region() -> None:
    subject_mask = np.zeros(
        (160, 120),
        dtype=np.float64,
    )
    subject_mask[20:121, 25:96] = 1.0
    subject_mask[50:80, 55:65] = 0.0

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
    )

    assert np.allclose(
        result[subject_mask <= 0.0],
        0.0,
        atol=1e-12,
    )


def test_binary_selection_contains_enough_pixels() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceInteriorCalibrationMask.build(
        subject_mask,
        face_bounds=(20, 120, 25, 95),
    )

    selected = result >= 0.25

    assert int(np.count_nonzero(selected)) > 500


def test_invalid_subject_mask_dimension_is_rejected() -> None:
    subject_mask = np.ones(
        (160, 120, 1),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="subject_mask",
    ):
        AtlasReliefFaceInteriorCalibrationMask.build(
            subject_mask,
            face_bounds=(20, 120, 25, 95),
        )


@pytest.mark.parametrize(
    "face_bounds",
    [
        (20, 20, 25, 95),
        (120, 20, 25, 95),
        (20, 120, 50, 50),
        (-1, 120, 25, 95),
        (20, 160, 25, 95),
        (20, 120, -1, 95),
        (20, 120, 25, 120),
        (20, 120, 25),
    ],
)
def test_invalid_face_bounds_are_rejected(
    face_bounds: tuple[int, ...],
) -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="face_bounds",
    ):
        AtlasReliefFaceInteriorCalibrationMask.build(
            subject_mask,
            face_bounds=face_bounds,
        )


@pytest.mark.parametrize(
    "parameter_name,parameter_value",
    [
        (
            "eye_suppression_strength",
            -0.1,
        ),
        (
            "eye_suppression_strength",
            1.1,
        ),
        (
            "mouth_suppression_strength",
            -0.1,
        ),
        (
            "mouth_suppression_strength",
            1.1,
        ),
    ],
)
def test_invalid_suppression_strength_is_rejected(
    parameter_name: str,
    parameter_value: float,
) -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    kwargs = {
        parameter_name: parameter_value,
    }

    with pytest.raises(
        ValueError,
        match=parameter_name,
    ):
        AtlasReliefFaceInteriorCalibrationMask.build(
            subject_mask,
            face_bounds=(20, 120, 25, 95),
            **kwargs,
        )
