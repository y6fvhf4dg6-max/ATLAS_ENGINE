from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_face_structure_confidence_map import (
    AtlasReliefFaceStructureConfidenceMap,
)


IMAGE_SHAPE = (160, 120)


def _regions() -> dict[str, np.ndarray]:
    rows, columns = IMAGE_SHAPE

    result = {
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

    result["face_interior"][20:121, 25:96] = 1.0

    result["face_boundary_falloff"][20:28, 25:96] = 1.0
    result["face_boundary_falloff"][113:121, 25:96] = 1.0
    result["face_boundary_falloff"][20:121, 25:33] = 1.0
    result["face_boundary_falloff"][20:121, 88:96] = 1.0

    result["eye_glasses"][42:58, 34:86] = 1.0
    result["nose_bridge"][48:76, 56:64] = 1.0
    result["nose_body"][62:84, 51:69] = 1.0
    result["nose_base"][80:90, 50:70] = 1.0

    result["philtrum"][89:99, 56:64] = 1.0
    result["upper_lip"][96:104, 47:73] = 1.0
    result["lower_lip"][103:112, 47:73] = 1.0

    result["right_cheek"][62:89, 31:51] = 1.0
    result["left_cheek"][62:89, 69:89] = 1.0
    result["chin"][108:120, 47:73] = 1.0

    return result


def _subject_mask() -> np.ndarray:
    mask = np.zeros(
        IMAGE_SHAPE,
        dtype=np.float64,
    )
    mask[10:150, 15:105] = 1.0
    return mask


def _build() -> np.ndarray:
    return AtlasReliefFaceStructureConfidenceMap.build(
        _subject_mask(),
        landmark_regions=_regions(),
    )


def test_output_contract() -> None:
    result = _build()

    assert result.shape == IMAGE_SHAPE
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))
    assert float(result.min()) >= 0.0
    assert float(result.max()) <= 1.0


def test_output_is_zero_outside_subject() -> None:
    subject = _subject_mask()

    result = AtlasReliefFaceStructureConfidenceMap.build(
        subject,
        landmark_regions=_regions(),
    )

    assert np.allclose(
        result[subject <= 0.0],
        0.0,
        atol=1.0e-12,
    )


def test_face_interior_does_not_create_a_structure_cutoff() -> None:
    result = _build()

    face = float(
        np.mean(result[64:84, 35:85])
    )
    subject_outside_face = float(
        np.mean(result[130:145, 35:85])
    )

    assert face > 0.50
    assert subject_outside_face > 0.90


def test_cheeks_retain_high_structure_confidence() -> None:
    result = _build()

    right_cheek = float(
        np.mean(result[66:84, 34:48])
    )
    left_cheek = float(
        np.mean(result[66:84, 72:86])
    )

    assert right_cheek > 0.70
    assert left_cheek > 0.70


def test_nose_body_retains_more_structure_than_nose_base() -> None:
    result = _build()

    nose_body = float(
        np.mean(result[64:78, 55:65])
    )
    nose_base = float(
        np.mean(result[82:89, 53:67])
    )

    assert nose_body > 0.70
    assert nose_body > nose_base
    assert nose_base < 0.55


def test_chin_retains_structure_confidence() -> None:
    result = _build()

    chin = float(
        np.mean(result[110:118, 51:69])
    )

    assert chin > 0.65


def test_glasses_core_uses_strong_but_nonzero_confidence() -> None:
    result = _build()

    glasses_core = float(
        np.mean(result[45:55, 39:81])
    )
    cheek = float(
        np.mean(result[66:84, 34:48])
    )

    assert 0.10 <= glasses_core < 0.20
    assert glasses_core > 0.0
    assert cheek > glasses_core


def test_philtrum_and_lips_are_more_suppressed_than_cheeks() -> None:
    result = _build()

    philtrum = float(
        np.mean(result[90:98, 57:63])
    )
    upper_lip = float(
        np.mean(result[97:103, 51:69])
    )
    lower_lip = float(
        np.mean(result[104:111, 51:69])
    )
    cheek = float(
        np.mean(result[66:84, 34:48])
    )

    assert philtrum < 0.45
    assert upper_lip < 0.50
    assert lower_lip < 0.55
    assert cheek > philtrum
    assert cheek > upper_lip
    assert cheek > lower_lip


def test_face_boundary_falloff_does_not_reduce_structure() -> None:
    result = _build()

    # Sample below the synthetic glasses band so both regions are free
    # from local anatomical suppression.
    boundary = float(
        np.mean(result[60:90, 26:32])
    )
    nearby_clear_interior = float(
        np.mean(result[60:90, 34:40])
    )

    assert boundary > 0.90
    assert abs(
        boundary - nearby_clear_interior
    ) < 0.10


def test_region_overlap_never_increases_above_one() -> None:
    regions = _regions()

    regions["eye_glasses"][62:76, 52:68] = 1.0
    regions["nose_body"][62:76, 52:68] = 1.0

    result = AtlasReliefFaceStructureConfidenceMap.build(
        _subject_mask(),
        landmark_regions=regions,
    )

    assert float(result.max()) <= 1.0


def test_missing_landmark_region_is_rejected() -> None:
    regions = _regions()
    del regions["nose_base"]

    with pytest.raises(
        ValueError,
        match="nose_base",
    ):
        AtlasReliefFaceStructureConfidenceMap.build(
            _subject_mask(),
            landmark_regions=regions,
        )


def test_wrong_region_shape_is_rejected() -> None:
    regions = _regions()
    regions["eye_glasses"] = np.zeros(
        (80, 60),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="eye_glasses",
    ):
        AtlasReliefFaceStructureConfidenceMap.build(
            _subject_mask(),
            landmark_regions=regions,
        )


def test_nonfinite_region_is_rejected() -> None:
    regions = _regions()
    regions["philtrum"][92, 60] = np.nan

    with pytest.raises(
        ValueError,
        match="philtrum",
    ):
        AtlasReliefFaceStructureConfidenceMap.build(
            _subject_mask(),
            landmark_regions=regions,
        )


def test_invalid_strength_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="glasses_confidence",
    ):
        AtlasReliefFaceStructureConfidenceMap.build(
            _subject_mask(),
            landmark_regions=_regions(),
            glasses_confidence=1.1,
        )


def test_face_support_masks_do_not_change_clear_structure_confidence() -> None:
    subject = _subject_mask()

    regions_with_support = _regions()
    regions_without_support = _regions()

    regions_without_support["face_interior"][:] = 0.0
    regions_without_support["face_boundary_falloff"][:] = 0.0

    with_support = AtlasReliefFaceStructureConfidenceMap.build(
        subject,
        landmark_regions=regions_with_support,
    )
    without_support = AtlasReliefFaceStructureConfidenceMap.build(
        subject,
        landmark_regions=regions_without_support,
    )

    clear_region = np.ones(
        IMAGE_SHAPE,
        dtype=bool,
    )

    for name in (
        "eye_glasses",
        "nose_base",
        "philtrum",
        "upper_lip",
        "lower_lip",
    ):
        clear_region &= (
            regions_with_support[name] <= 0.0
        )

    clear_region &= subject > 0.0

    assert np.allclose(
        with_support[clear_region],
        without_support[clear_region],
        atol=1.0e-12,
    )


def test_glasses_core_is_more_suppressed_than_soft_glasses_region() -> None:
    regions = _regions()

    regions["eye_glasses"][:] = 0.0
    regions["eye_glasses"][40:60, 32:88] = 0.50
    regions["eye_glasses"][45:55, 40:80] = 1.00

    result = AtlasReliefFaceStructureConfidenceMap.build(
        _subject_mask(),
        landmark_regions=regions,
        glasses_confidence=0.35,
        glasses_core_confidence=0.12,
    )

    core = float(
        np.mean(result[47:53, 44:76])
    )
    soft_surround = float(
        np.mean(result[41:44, 36:84])
    )

    assert core < 0.20
    assert 0.55 < soft_surround < 0.80
    assert core < soft_surround


def test_glasses_core_control_does_not_change_clear_face_regions() -> None:
    regions = _regions()

    regions["eye_glasses"][:] = 0.0
    regions["eye_glasses"][40:60, 32:88] = 0.50
    regions["eye_glasses"][45:55, 40:80] = 1.00

    default_core = AtlasReliefFaceStructureConfidenceMap.build(
        _subject_mask(),
        landmark_regions=regions,
        glasses_confidence=0.35,
        glasses_core_confidence=0.12,
    )

    weaker_core = AtlasReliefFaceStructureConfidenceMap.build(
        _subject_mask(),
        landmark_regions=regions,
        glasses_confidence=0.35,
        glasses_core_confidence=0.30,
    )

    clear_face = np.zeros(
        IMAGE_SHAPE,
        dtype=bool,
    )
    clear_face[64:84, 34:48] = True
    clear_face[64:78, 55:65] = True
    clear_face[24:38, 42:78] = True

    assert np.allclose(
        default_core[clear_face],
        weaker_core[clear_face],
        atol=1.0e-12,
    )


@pytest.mark.parametrize(
    "glasses_core_confidence",
    [
        -0.1,
        1.1,
        np.nan,
        np.inf,
    ],
)
def test_invalid_glasses_core_confidence_is_rejected(
    glasses_core_confidence: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="glasses_core_confidence",
    ):
        AtlasReliefFaceStructureConfidenceMap.build(
            _subject_mask(),
            landmark_regions=_regions(),
            glasses_core_confidence=glasses_core_confidence,
        )
