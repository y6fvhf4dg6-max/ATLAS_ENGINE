import numpy as np
import pytest

from CORE.atlas_canonical_head_lateral_contour_correction import (
    AtlasCanonicalHeadLateralContourCorrection,
)


def _vertices():
    return np.asarray(
        [
            [-2.0,  1.0, 0.0],
            [-1.0,  1.0, 0.0],
            [-0.5,  0.0, 0.0],
            [ 0.0,  0.0, 0.0],
            [ 0.5,  0.0, 0.0],
            [ 1.0,  1.0, 0.0],
            [ 2.0,  1.0, 0.0],
        ],
        dtype=np.float64,
    )


def test_preserves_vertices_inside_central_face_protection_zone():
    result = AtlasCanonicalHeadLateralContourCorrection.apply(
        vertices=_vertices(),
        pivot_x=0.0,
        eye_half_span=1.0,
        protect_radius_eye_half=1.0,
        full_radius_eye_half=2.0,
        vertical_factors=np.asarray(
            [0.75] * 7,
            dtype=np.float64,
        ),
        strength=1.0,
    )

    assert np.allclose(
        result.vertices[2:5],
        _vertices()[2:5],
    )


def test_contracts_outer_lateral_vertices_toward_pivot():
    result = AtlasCanonicalHeadLateralContourCorrection.apply(
        vertices=_vertices(),
        pivot_x=0.0,
        eye_half_span=1.0,
        protect_radius_eye_half=1.0,
        full_radius_eye_half=2.0,
        vertical_factors=np.asarray(
            [0.75] * 7,
            dtype=np.float64,
        ),
        strength=1.0,
    )

    assert abs(result.vertices[0, 0]) < 2.0
    assert abs(result.vertices[-1, 0]) < 2.0


def test_y_and_z_are_unchanged():
    original = _vertices()

    result = AtlasCanonicalHeadLateralContourCorrection.apply(
        vertices=original,
        pivot_x=0.0,
        eye_half_span=1.0,
        protect_radius_eye_half=1.0,
        full_radius_eye_half=2.0,
        vertical_factors=np.asarray(
            [0.8] * len(original),
            dtype=np.float64,
        ),
        strength=1.0,
    )

    assert np.array_equal(
        result.vertices[:, 1],
        original[:, 1],
    )
    assert np.array_equal(
        result.vertices[:, 2],
        original[:, 2],
    )


def test_zero_strength_is_identity():
    original = _vertices()

    result = AtlasCanonicalHeadLateralContourCorrection.apply(
        vertices=original,
        pivot_x=0.0,
        eye_half_span=1.0,
        protect_radius_eye_half=1.0,
        full_radius_eye_half=2.0,
        vertical_factors=np.asarray(
            [0.7] * len(original),
            dtype=np.float64,
        ),
        strength=0.0,
    )

    assert np.array_equal(
        result.vertices,
        original,
    )


def test_requires_vertical_factor_for_every_vertex():
    with pytest.raises(
        ValueError,
        match="vertical_factors",
    ):
        AtlasCanonicalHeadLateralContourCorrection.apply(
            vertices=_vertices(),
            pivot_x=0.0,
            eye_half_span=1.0,
            protect_radius_eye_half=1.0,
            full_radius_eye_half=2.0,
            vertical_factors=np.asarray(
                [0.8, 0.8],
                dtype=np.float64,
            ),
            strength=1.0,
        )


def test_rejects_nonpositive_eye_half_span():
    with pytest.raises(
        ValueError,
        match="eye_half_span",
    ):
        AtlasCanonicalHeadLateralContourCorrection.apply(
            vertices=_vertices(),
            pivot_x=0.0,
            eye_half_span=0.0,
            protect_radius_eye_half=1.0,
            full_radius_eye_half=2.0,
            vertical_factors=np.asarray(
                [0.8] * 7,
                dtype=np.float64,
            ),
            strength=1.0,
        )


def test_rejects_invalid_radius_order():
    with pytest.raises(
        ValueError,
        match="full_radius_eye_half",
    ):
        AtlasCanonicalHeadLateralContourCorrection.apply(
            vertices=_vertices(),
            pivot_x=0.0,
            eye_half_span=1.0,
            protect_radius_eye_half=2.0,
            full_radius_eye_half=1.0,
            vertical_factors=np.asarray(
                [0.8] * 7,
                dtype=np.float64,
            ),
            strength=1.0,
        )


def test_reports_explicit_nonsemantic_provenance():
    result = AtlasCanonicalHeadLateralContourCorrection.apply(
        vertices=_vertices(),
        pivot_x=0.0,
        eye_half_span=1.0,
        protect_radius_eye_half=1.0,
        full_radius_eye_half=2.0,
        vertical_factors=np.asarray(
            [0.8] * 7,
            dtype=np.float64,
        ),
        strength=1.0,
    )

    assert (
        result.provenance
        == "atlas_canonical_head_lateral_contour_correction:v1"
    )
    assert result.semantic_support == "none"
    assert result.hair_semantics_used is False
    assert result.ear_semantics_used is False
