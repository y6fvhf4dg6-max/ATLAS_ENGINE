import numpy as np
import pytest

from CORE.atlas_canonical_head_local_facial_feature_xy_correction import (
    AtlasCanonicalHeadLocalFacialFeatureXYCorrection,
)


def _vertices():
    return np.asarray(
        [
            [-2.0,  2.0, 0.1],
            [-1.0,  1.0, 0.2],
            [ 0.0,  0.0, 0.3],
            [ 1.0, -1.0, 0.4],
            [ 2.0, -2.0, 0.5],
        ],
        dtype=np.float64,
    )


def _support(values):
    return np.asarray(values, dtype=np.float64)


def test_nose_bridge_channel_applies_supported_xy_affine_only():
    original = _vertices()

    result = AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=original,
        channels={
            "nose_bridge": {
                "support": _support([0.0, 1.0, 1.0, 0.0, 0.0]),
                "pivot_xy": (0.0, 0.0),
                "scale_xy": (0.8, 1.2),
                "translation_xy": (-0.1, 0.2),
            },
        },
    )

    assert np.array_equal(result.vertices[0], original[0])
    assert np.array_equal(result.vertices[3], original[3])
    assert np.array_equal(result.vertices[4], original[4])

    assert result.vertices[1, 0] == pytest.approx(-0.9)
    assert result.vertices[1, 1] == pytest.approx(1.4)
    assert result.vertices[2, 0] == pytest.approx(-0.1)
    assert result.vertices[2, 1] == pytest.approx(0.2)


def test_nose_body_base_channel_is_independent_from_bridge():
    original = _vertices()

    result = AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=original,
        channels={
            "nose_bridge": {
                "support": _support([0.0, 0.0, 0.0, 0.0, 0.0]),
                "pivot_xy": (0.0, 0.0),
                "scale_xy": (0.5, 0.5),
                "translation_xy": (9.0, 9.0),
            },
            "nose_body_base": {
                "support": _support([0.0, 0.0, 1.0, 1.0, 0.0]),
                "pivot_xy": (0.0, 0.0),
                "scale_xy": (1.1, 0.9),
                "translation_xy": (0.0, -0.2),
            },
        },
    )

    assert result.vertices[2, 0] == pytest.approx(0.0)
    assert result.vertices[2, 1] == pytest.approx(-0.2)
    assert result.vertices[3, 0] == pytest.approx(1.1)
    assert result.vertices[3, 1] == pytest.approx(-1.1)


def test_mouth_lips_channel_can_contract_width_without_changing_z():
    original = _vertices()

    result = AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=original,
        channels={
            "mouth_lips": {
                "support": _support([0.0, 1.0, 1.0, 1.0, 0.0]),
                "pivot_xy": (0.0, 0.0),
                "scale_xy": (0.92, 1.0),
                "translation_xy": (0.0, 0.0),
            },
        },
    )

    assert abs(result.vertices[1, 0]) < abs(original[1, 0])
    assert abs(result.vertices[3, 0]) < abs(original[3, 0])
    assert np.array_equal(result.vertices[:, 2], original[:, 2])


def test_fractional_support_blends_identity_to_full_transform():
    original = _vertices()

    result = AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=original,
        channels={
            "mouth_lips": {
                "support": _support([0.0, 0.5, 0.0, 0.0, 0.0]),
                "pivot_xy": (0.0, 0.0),
                "scale_xy": (0.8, 1.0),
                "translation_xy": (0.0, 0.0),
            },
        },
    )

    full_x = -0.8
    expected_x = 0.5 * original[1, 0] + 0.5 * full_x

    assert result.vertices[1, 0] == pytest.approx(expected_x)
    assert result.vertices[1, 1] == pytest.approx(original[1, 1])


def test_rejects_unknown_channel_name():
    with pytest.raises(
        ValueError,
        match="unsupported channel",
    ):
        AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
            vertices=_vertices(),
            channels={
                "eyes": {
                    "support": _support([1.0] * 5),
                    "pivot_xy": (0.0, 0.0),
                    "scale_xy": (1.0, 1.0),
                    "translation_xy": (0.0, 0.0),
                },
            },
        )


def test_rejects_support_length_mismatch():
    with pytest.raises(
        ValueError,
        match="support",
    ):
        AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
            vertices=_vertices(),
            channels={
                "nose_bridge": {
                    "support": _support([1.0, 1.0]),
                    "pivot_xy": (0.0, 0.0),
                    "scale_xy": (1.0, 1.0),
                    "translation_xy": (0.0, 0.0),
                },
            },
        )


def test_rejects_support_outside_unit_interval():
    with pytest.raises(
        ValueError,
        match="support",
    ):
        AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
            vertices=_vertices(),
            channels={
                "nose_bridge": {
                    "support": _support([0.0, 1.2, 0.0, 0.0, 0.0]),
                    "pivot_xy": (0.0, 0.0),
                    "scale_xy": (1.0, 1.0),
                    "translation_xy": (0.0, 0.0),
                },
            },
        )


def test_channel_application_is_deterministic_and_ordered():
    original = _vertices()

    channels = {
        "nose_bridge": {
            "support": _support([0.0, 1.0, 0.0, 0.0, 0.0]),
            "pivot_xy": (0.0, 0.0),
            "scale_xy": (0.9, 1.1),
            "translation_xy": (0.1, 0.0),
        },
        "mouth_lips": {
            "support": _support([0.0, 1.0, 0.0, 0.0, 0.0]),
            "pivot_xy": (0.0, 0.0),
            "scale_xy": (0.8, 1.0),
            "translation_xy": (0.0, 0.2),
        },
    }

    a = AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=original,
        channels=channels,
    )

    b = AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=original,
        channels=dict(reversed(list(channels.items()))),
    )

    assert np.array_equal(a.vertices, b.vertices)


def test_reports_explicit_bounded_semantic_contract():
    result = AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=_vertices(),
        channels={
            "nose_bridge": {
                "support": _support([0.0] * 5),
                "pivot_xy": (0.0, 0.0),
                "scale_xy": (1.0, 1.0),
                "translation_xy": (0.0, 0.0),
            },
        },
    )

    assert (
        result.provenance
        == "atlas_canonical_head_local_facial_feature_xy_correction:v1"
    )
    assert result.support_source == "explicit_external_feature_support"
    assert result.dense_semantics_invented is False
    assert result.hair_semantics_used is False
    assert result.ear_semantics_used is False


def test_input_vertices_are_not_mutated():
    original = _vertices()
    before = original.copy()

    AtlasCanonicalHeadLocalFacialFeatureXYCorrection.apply(
        vertices=original,
        channels={
            "nose_bridge": {
                "support": _support([0.0, 1.0, 1.0, 0.0, 0.0]),
                "pivot_xy": (0.0, 0.0),
                "scale_xy": (0.9, 1.1),
                "translation_xy": (0.0, 0.0),
            },
        },
    )

    assert np.array_equal(original, before)
