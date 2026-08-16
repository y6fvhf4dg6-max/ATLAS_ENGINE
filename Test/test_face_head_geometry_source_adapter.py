from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.atlas_face_head_geometry_source_adapter import (
    AtlasFaceHeadGeometrySourceAdapter,
)


def test_face_head_adapter_normalizes_portrait_landmark_result():
    portrait = AtlasPortraitLandmarkResult(
        image_width=1000,
        image_height=800,
        landmarks={
            "Left Eye Outer": (0.30, 0.35),
            "Right Eye Outer": (0.70, 0.35),
            "Nose Tip": (0.50, 0.55),
            "Mouth Left": (0.42, 0.70),
            "Mouth Right": (0.58, 0.70),
            "Chin Tip": (0.50, 0.90),
        },
        confidence=0.95,
        provider_id="fixture-provider",
        metadata={
            "source": "synthetic fixture",
        },
    )

    result = (
        AtlasFaceHeadGeometrySourceAdapter()
        .adapt(portrait)
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )

    assert result.normalized_geometry == {
        "geometry_kind": "face_head_landmarks",
        "coordinate_space": "normalized_image_2d",
        "image_width": 1000,
        "image_height": 800,
        "landmarks": {
            "left_eye_outer": (0.30, 0.35),
            "right_eye_outer": (0.70, 0.35),
            "nose_tip": (0.50, 0.55),
            "mouth_left": (0.42, 0.70),
            "mouth_right": (0.58, 0.70),
            "chin_tip": (0.50, 0.90),
        },
        "provider_id": "fixture-provider",
    }

    assert result.local_bounds == (
        (0.30, 0.35, 0.0),
        (0.70, 0.90, 0.0),
    )

    assert dict(result.anchors) == {
        "left_eye_outer": (0.30, 0.35, 0.0),
        "right_eye_outer": (0.70, 0.35, 0.0),
        "nose_tip": (0.50, 0.55, 0.0),
        "mouth_left": (0.42, 0.70, 0.0),
        "mouth_right": (0.58, 0.70, 0.0),
        "chin_tip": (0.50, 0.90, 0.0),
    }

    assert result.confidence == 0.95
    assert result.provenance == (
        "portrait_landmark_provider:"
        "fixture-provider"
    )

    assert result.supported_projection_modes == (
        "flat_plane",
    )

    assert "mesh" not in result.normalized_geometry
    assert "triangles" not in result.normalized_geometry
    assert "head_mesh" not in result.normalized_geometry

import pytest


def _portrait_result(
    *,
    landmarks=None,
    confidence=0.90,
    provider_id="fixture-provider",
):
    return AtlasPortraitLandmarkResult(
        image_width=640,
        image_height=480,
        landmarks=(
            landmarks
            if landmarks is not None
            else {
                "left eye": (0.25, 0.30),
                "right eye": (0.75, 0.30),
                "nose tip": (0.50, 0.55),
                "chin tip": (0.50, 0.90),
            }
        ),
        confidence=confidence,
        provider_id=provider_id,
        metadata={
            "source": "fixture",
        },
    )


def test_face_head_adapter_rejects_non_portrait_landmark_result():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitLandmarkResult",
    ):
        AtlasFaceHeadGeometrySourceAdapter().adapt(
            {
                "landmarks": {},
            }
        )


def test_face_head_adapter_bounds_are_deterministic_from_normalized_landmarks():
    result = AtlasFaceHeadGeometrySourceAdapter().adapt(
        _portrait_result()
    )

    assert result.local_bounds == (
        (0.25, 0.30, 0.0),
        (0.75, 0.90, 0.0),
    )


def test_face_head_adapter_anchors_use_canonical_landmark_identity():
    result = AtlasFaceHeadGeometrySourceAdapter().adapt(
        _portrait_result()
    )

    assert dict(result.anchors) == {
        "left_eye": (0.25, 0.30, 0.0),
        "right_eye": (0.75, 0.30, 0.0),
        "nose_tip": (0.50, 0.55, 0.0),
        "chin_tip": (0.50, 0.90, 0.0),
    }


def test_face_head_adapter_preserves_provider_confidence_and_provenance():
    result = AtlasFaceHeadGeometrySourceAdapter().adapt(
        _portrait_result(
            confidence=0.81,
            provider_id="custom-provider",
        )
    )

    assert result.confidence == 0.81
    assert result.provenance == (
        "portrait_landmark_provider:"
        "custom-provider"
    )


def test_face_head_adapter_supports_only_flat_plane_projection():
    result = AtlasFaceHeadGeometrySourceAdapter().adapt(
        _portrait_result()
    )

    assert (
        result.require_projection_mode(
            " Flat Plane "
        )
        == "flat_plane"
    )

    with pytest.raises(
        ValueError,
        match="projection mode",
    ):
        result.require_projection_mode(
            "curved_surface"
        )


def test_face_head_adapter_does_not_claim_canonical_3d_head_geometry():
    result = AtlasFaceHeadGeometrySourceAdapter().adapt(
        _portrait_result()
    )

    geometry = result.normalized_geometry

    assert geometry[
        "geometry_kind"
    ] == "face_head_landmarks"

    assert geometry[
        "coordinate_space"
    ] == "normalized_image_2d"

    assert "vertices" not in geometry
    assert "faces" not in geometry
    assert "triangles" not in geometry
    assert "head_mesh" not in geometry


def test_face_head_adapter_normalized_geometry_is_isolated_snapshot():
    portrait = _portrait_result()

    result = AtlasFaceHeadGeometrySourceAdapter().adapt(
        portrait
    )

    geometry_landmarks = result.normalized_geometry[
        "landmarks"
    ]

    assert geometry_landmarks == {
        "left_eye": (0.25, 0.30),
        "right_eye": (0.75, 0.30),
        "nose_tip": (0.50, 0.55),
        "chin_tip": (0.50, 0.90),
    }

    assert geometry_landmarks is not portrait.landmarks
