from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_face_semantic_detail_weight_map import (
    AtlasReliefFaceSemanticDetailWeightMap,
)


FACE_BOUNDS = (
    20,
    120,
    25,
    95,
)


def test_output_shape_and_dtype_are_preserved() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float32,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
    )

    assert result.shape == subject_mask.shape
    assert result.dtype == np.float64


def test_output_is_bounded_to_unit_interval() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
    )

    assert float(result.min()) >= 0.0
    assert float(result.max()) <= 1.0


def test_output_is_zero_outside_subject() -> None:
    subject_mask = np.zeros(
        (160, 120),
        dtype=np.float64,
    )
    subject_mask[10:150, 15:105] = 1.0

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
    )

    assert np.allclose(
        result[subject_mask <= 0.0],
        0.0,
        atol=1e-12,
    )


def test_torso_region_has_near_zero_detail_weight() -> None:
    subject_mask = np.ones(
        (180, 130),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=(20, 120, 25, 105),
    )

    face_weight = float(
        np.mean(
            result[45:100, 40:90]
        )
    )
    torso_weight = float(
        np.mean(
            result[145:175, 30:100]
        )
    )

    assert face_weight > 0.20
    assert torso_weight < 0.05


def test_cheeks_retain_more_detail_than_glasses_band() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        glasses_suppression_strength=0.95,
    )

    glasses_band = float(
        np.mean(
            result[52:66, 38:82]
        )
    )
    cheeks = float(
        np.mean(
            result[68:82, 36:84]
        )
    )

    assert cheeks > glasses_band


def test_nose_body_retains_more_detail_than_nostril_region() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        nostril_suppression_strength=0.95,
    )

    nose_body = float(
        np.mean(
            result[58:78, 54:66]
        )
    )
    nostril_region = float(
        np.mean(
            result[78:86, 52:68]
        )
    )

    assert nose_body > nostril_region


def test_philtrum_and_upper_lip_are_suppressed() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        philtrum_suppression_strength=0.95,
    )

    cheek = float(
        np.mean(
            result[70:84, 38:48]
        )
    )
    philtrum = float(
        np.mean(
            result[84:96, 55:65]
        )
    )

    assert cheek > philtrum


def test_chin_retains_more_detail_than_lower_neck() -> None:
    subject_mask = np.ones(
        (170, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
    )

    chin = float(
        np.mean(
            result[98:110, 48:72]
        )
    )
    lower_neck = float(
        np.mean(
            result[125:145, 48:72]
        )
    )

    assert chin > lower_neck


def test_lateral_face_edges_are_lower_than_face_interior() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        boundary_suppression_strength=0.95,
    )

    interior = float(
        np.mean(
            result[65:90, 48:72]
        )
    )
    lateral_edges = float(
        np.mean(
            np.concatenate(
                [
                    result[55:95, 25:32].ravel(),
                    result[55:95, 88:96].ravel(),
                ]
            )
        )
    )

    assert interior > lateral_edges


def test_soft_subject_boundary_is_suppressed() -> None:
    rows = 160
    columns = 120

    subject_mask = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )
    subject_mask[15:145, 20:100] = 1.0

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        boundary_suppression_strength=1.0,
        boundary_width=6,
    )

    boundary = float(
        np.mean(
            result[40:110, 20:24]
        )
    )
    interior = float(
        np.mean(
            result[60:90, 45:75]
        )
    )

    assert interior > boundary


def test_face_interior_contains_enough_active_pixels() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
    )

    selected = result >= 0.20

    assert int(
        np.count_nonzero(selected)
    ) > 1000


def test_invalid_subject_mask_dimension_is_rejected() -> None:
    subject_mask = np.ones(
        (160, 120, 1),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="subject_mask",
    ):
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=FACE_BOUNDS,
        )


def test_nonfinite_subject_mask_is_rejected() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )
    subject_mask[20, 30] = np.nan

    with pytest.raises(
        ValueError,
        match="subject_mask",
    ):
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=FACE_BOUNDS,
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
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=face_bounds,
        )


@pytest.mark.parametrize(
    "parameter_name,parameter_value",
    [
        (
            "glasses_suppression_strength",
            -0.1,
        ),
        (
            "glasses_suppression_strength",
            1.1,
        ),
        (
            "nostril_suppression_strength",
            -0.1,
        ),
        (
            "nostril_suppression_strength",
            1.1,
        ),
        (
            "philtrum_suppression_strength",
            -0.1,
        ),
        (
            "philtrum_suppression_strength",
            1.1,
        ),
        (
            "boundary_suppression_strength",
            -0.1,
        ),
        (
            "boundary_suppression_strength",
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
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=FACE_BOUNDS,
            **kwargs,
        )


@pytest.mark.parametrize(
    "boundary_width",
    [
        0,
        -1,
        1.5,
        np.nan,
        np.inf,
    ],
)
def test_invalid_boundary_width_is_rejected(
    boundary_width: float,
) -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="boundary_width",
    ):
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=FACE_BOUNDS,
            boundary_width=boundary_width,
        )


def _synthetic_landmark_regions(
    shape: tuple[int, int] = (160, 120),
) -> dict[str, np.ndarray]:
    rows, columns = shape

    regions = {
        name: np.zeros(
            (rows, columns),
            dtype=np.float64,
        )
        for name in (
            "eye_glasses",
            "nose_bridge",
            "nose_body",
            "nose_base",
            "philtrum",
            "upper_lip",
            "lower_lip",
            "left_cheek",
            "right_cheek",
            "chin",
            "face_interior",
            "face_boundary_falloff",
        )
    }

    regions["face_interior"][20:121, 25:96] = 1.0

    regions["face_boundary_falloff"][20:26, 25:96] = 1.0
    regions["face_boundary_falloff"][115:121, 25:96] = 1.0
    regions["face_boundary_falloff"][20:121, 25:31] = 1.0
    regions["face_boundary_falloff"][20:121, 90:96] = 1.0

    # Deliberately placed away from the legacy proportional Gaussian
    # center so the test proves that landmark coordinates are used.
    regions["eye_glasses"][35:47, 72:96] = 1.0

    regions["nose_bridge"][50:75, 56:64] = 1.0
    regions["nose_body"][62:82, 52:68] = 1.0
    regions["nose_base"][80:88, 51:69] = 1.0

    regions["philtrum"][88:98, 56:64] = 1.0
    regions["upper_lip"][96:103, 48:72] = 1.0
    regions["lower_lip"][103:111, 48:72] = 1.0

    regions["right_cheek"][62:88, 30:50] = 1.0
    regions["left_cheek"][62:88, 70:90] = 1.0
    regions["chin"][108:119, 48:72] = 1.0

    return regions


def test_landmark_regions_preserve_output_contract() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        landmark_regions=_synthetic_landmark_regions(),
    )

    assert result.shape == subject_mask.shape
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))
    assert float(result.min()) >= 0.0
    assert float(result.max()) <= 1.0


def test_landmark_face_interior_replaces_rectangular_face_support() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )
    regions = _synthetic_landmark_regions()

    # Inside legacy face_bounds but outside landmark face interior.
    regions["face_interior"][30:50, 25:45] = 0.0

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        landmark_regions=regions,
    )

    assert np.allclose(
        result[32:48, 27:43],
        0.0,
        atol=1.0e-12,
    )

    assert float(
        np.mean(result[62:78, 52:68])
    ) > 0.0


def test_landmark_eye_glasses_region_controls_real_location() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )
    regions = _synthetic_landmark_regions()

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        landmark_regions=regions,
        glasses_suppression_strength=1.0,
        nostril_suppression_strength=0.0,
        philtrum_suppression_strength=0.0,
    )

    custom_glasses = float(
        np.mean(result[37:45, 76:92])
    )
    mirrored_clear_area = float(
        np.mean(result[37:45, 30:46])
    )

    assert custom_glasses < 0.05
    assert mirrored_clear_area > custom_glasses


def test_landmark_nose_body_retains_more_than_nose_base() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        landmark_regions=_synthetic_landmark_regions(),
        glasses_suppression_strength=0.0,
        nostril_suppression_strength=0.95,
        philtrum_suppression_strength=0.0,
    )

    nose_body = float(
        np.mean(result[64:76, 55:65])
    )
    nose_base = float(
        np.mean(result[81:87, 54:66])
    )

    assert nose_body > nose_base


def test_landmark_cheeks_retain_more_than_philtrum() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        landmark_regions=_synthetic_landmark_regions(),
        glasses_suppression_strength=0.0,
        nostril_suppression_strength=0.0,
        philtrum_suppression_strength=0.95,
    )

    cheeks = float(
        np.mean(
            np.concatenate(
                [
                    result[66:82, 34:48].ravel(),
                    result[66:82, 72:86].ravel(),
                ]
            )
        )
    )
    philtrum = float(
        np.mean(result[89:97, 57:63])
    )

    assert cheeks > philtrum


def test_landmark_chin_remains_above_lower_neck_weight() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        landmark_regions=_synthetic_landmark_regions(),
    )

    chin = float(
        np.mean(result[109:117, 51:69])
    )
    lower_neck = float(
        np.mean(result[130:150, 48:72])
    )

    assert chin > lower_neck


def test_landmark_face_boundary_falloff_suppresses_real_boundary() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    result = AtlasReliefFaceSemanticDetailWeightMap.build(
        subject_mask,
        face_bounds=FACE_BOUNDS,
        landmark_regions=_synthetic_landmark_regions(),
        boundary_suppression_strength=1.0,
    )

    landmark_boundary = float(
        np.mean(result[50:90, 26:30])
    )
    face_center = float(
        np.mean(result[60:78, 52:68])
    )

    assert face_center > landmark_boundary


def test_landmark_regions_reject_missing_required_region() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )
    regions = _synthetic_landmark_regions()
    del regions["eye_glasses"]

    with pytest.raises(
        ValueError,
        match="eye_glasses",
    ):
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=FACE_BOUNDS,
            landmark_regions=regions,
        )


def test_landmark_regions_reject_wrong_mask_shape() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )
    regions = _synthetic_landmark_regions()
    regions["nose_base"] = np.zeros(
        (80, 60),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="nose_base",
    ):
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=FACE_BOUNDS,
            landmark_regions=regions,
        )


def test_landmark_regions_reject_values_outside_unit_interval() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )
    regions = _synthetic_landmark_regions()
    regions["philtrum"][90, 60] = 1.1

    with pytest.raises(
        ValueError,
        match="philtrum",
    ):
        AtlasReliefFaceSemanticDetailWeightMap.build(
            subject_mask,
            face_bounds=FACE_BOUNDS,
            landmark_regions=regions,
        )
