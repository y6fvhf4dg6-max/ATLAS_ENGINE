import pytest

from CORE.atlas_semantic_surface_texture_pattern import (
    AtlasSemanticSurfaceTexturePattern,
)


def test_paving_pattern_produces_restrained_periodic_offset():
    pattern = AtlasSemanticSurfaceTexturePattern(
        texture_language="paving",
        relief_depth_mm=0.14,
        feature_pitch_mm=1.80,
    )

    values = [
        pattern.offset_at(x, 0.75)
        for x in (
            0.0,
            0.45,
            0.90,
            1.35,
            1.80,
            2.25,
        )
    ]

    assert any(abs(value) > 0.0 for value in values)

    assert (
        max(abs(value) for value in values)
        <= 0.14 + 1e-9
    )


def test_paving_pattern_is_deterministic():
    first = AtlasSemanticSurfaceTexturePattern(
        texture_language="paving",
        relief_depth_mm=0.14,
        feature_pitch_mm=1.80,
    )

    second = AtlasSemanticSurfaceTexturePattern(
        texture_language="paving",
        relief_depth_mm=0.14,
        feature_pitch_mm=1.80,
    )

    assert first.offset_at(3.25, 4.75) == second.offset_at(
        3.25,
        4.75,
    )


def test_pattern_rejects_unsupported_language():
    with pytest.raises(
        ValueError,
        match="unsupported texture_language",
    ):
        AtlasSemanticSurfaceTexturePattern(
            texture_language="unknown",
            relief_depth_mm=0.14,
            feature_pitch_mm=1.80,
        )


from CORE.atlas_semantic_surface_texture_resolver import (
    AtlasSemanticSurfaceTextureResolver,
)


def test_paving_pattern_can_be_built_from_semantic_profile():
    profile = AtlasSemanticSurfaceTextureResolver.resolve(
        surface_role="plaza_ground",
    )

    pattern = AtlasSemanticSurfaceTexturePattern(
        texture_language=profile["texture_language"],
        relief_depth_mm=profile["relief_depth_mm"],
        feature_pitch_mm=profile["feature_pitch_mm"],
    )

    assert pattern.texture_language == "paving"
    assert pattern.relief_depth_mm == 0.14
    assert pattern.feature_pitch_mm == 1.80


def test_courtyard_uses_same_restrained_paving_language():
    profile = AtlasSemanticSurfaceTextureResolver.resolve(
        surface_role="courtyard_ground",
    )

    pattern = AtlasSemanticSurfaceTexturePattern(
        texture_language=profile["texture_language"],
        relief_depth_mm=profile["relief_depth_mm"],
        feature_pitch_mm=profile["feature_pitch_mm"],
    )

    assert pattern.offset_at(0.45, 0.45) == pytest.approx(
        AtlasSemanticSurfaceTexturePattern(
            texture_language="paving",
            relief_depth_mm=0.14,
            feature_pitch_mm=1.80,
        ).offset_at(0.45, 0.45)
    )

def test_paving_pattern_is_non_negative_emboss():
    pattern = AtlasSemanticSurfaceTexturePattern(
        texture_language="paving",
        relief_depth_mm=0.14,
        feature_pitch_mm=1.80,
    )

    values = [
        pattern.offset_at(x, y)
        for x, y in (
            (0.45, 0.45),
            (0.45, 1.35),
            (1.35, 0.45),
            (1.35, 1.35),
        )
    ]

    assert min(values) >= 0.0
    assert max(values) <= 0.14 + 1e-9



@pytest.mark.parametrize(
    (
        "texture_language",
        "relief_depth_mm",
        "feature_pitch_mm",
    ),
    (
        ("lawn", 0.18, 1.40),
        ("grass", 0.18, 1.20),
    ),
)
def test_lawn_and_grass_patterns_are_restrained_non_negative_emboss(
    texture_language,
    relief_depth_mm,
    feature_pitch_mm,
):
    pattern = AtlasSemanticSurfaceTexturePattern(
        texture_language=texture_language,
        relief_depth_mm=relief_depth_mm,
        feature_pitch_mm=feature_pitch_mm,
    )

    values = [
        pattern.offset_at(x, y)
        for x, y in (
            (0.0, 0.0),
            (0.30, 0.45),
            (0.60, 0.75),
            (0.90, 1.05),
            (1.20, 1.35),
        )
    ]

    assert min(values) >= 0.0
    assert max(values) <= relief_depth_mm + 1e-9
    assert any(value > 0.0 for value in values)


def test_lawn_and_grass_use_distinct_surface_languages():
    lawn = AtlasSemanticSurfaceTexturePattern(
        texture_language="lawn",
        relief_depth_mm=0.18,
        feature_pitch_mm=1.40,
    )

    grass = AtlasSemanticSurfaceTexturePattern(
        texture_language="grass",
        relief_depth_mm=0.18,
        feature_pitch_mm=1.20,
    )

    sample_points = (
        (0.25, 0.35),
        (0.55, 0.85),
        (1.05, 1.25),
    )

    lawn_values = tuple(
        lawn.offset_at(x, y)
        for x, y in sample_points
    )

    grass_values = tuple(
        grass.offset_at(x, y)
        for x, y in sample_points
    )

    assert lawn_values != grass_values


@pytest.mark.parametrize(
    (
        "texture_language",
        "relief_depth_mm",
        "feature_pitch_mm",
    ),
    (
        ("ordered_ground", 0.14, 1.80),
        ("field", 0.12, 2.00),
    ),
)
def test_ordered_ground_and_field_are_restrained_non_negative_emboss(
    texture_language,
    relief_depth_mm,
    feature_pitch_mm,
):
    pattern = AtlasSemanticSurfaceTexturePattern(
        texture_language=texture_language,
        relief_depth_mm=relief_depth_mm,
        feature_pitch_mm=feature_pitch_mm,
    )

    values = [
        pattern.offset_at(x, y)
        for x, y in (
            (0.0, 0.0),
            (0.50, 0.25),
            (1.00, 0.75),
            (1.50, 1.25),
            (2.00, 1.75),
        )
    ]

    assert min(values) >= 0.0
    assert max(values) <= relief_depth_mm + 1e-9
    assert any(value > 0.0 for value in values)


def test_ordered_ground_and_field_use_distinct_patterns():
    ordered = AtlasSemanticSurfaceTexturePattern(
        texture_language="ordered_ground",
        relief_depth_mm=0.14,
        feature_pitch_mm=1.80,
    )

    field = AtlasSemanticSurfaceTexturePattern(
        texture_language="field",
        relief_depth_mm=0.12,
        feature_pitch_mm=2.00,
    )

    sample_points = (
        (0.35, 0.20),
        (0.95, 0.65),
        (1.55, 1.10),
    )

    ordered_values = tuple(
        ordered.offset_at(x, y)
        for x, y in sample_points
    )

    field_values = tuple(
        field.offset_at(x, y)
        for x, y in sample_points
    )

    assert ordered_values != field_values
