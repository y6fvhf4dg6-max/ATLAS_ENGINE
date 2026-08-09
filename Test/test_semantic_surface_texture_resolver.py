import pytest

from CORE.atlas_semantic_surface_texture_resolver import (
    AtlasSemanticSurfaceTextureResolver,
)


@pytest.mark.parametrize(
    ("surface_role", "texture_language"),
    (
        ("park_ground", "lawn"),
        ("grass_ground", "grass"),
        ("plaza_ground", "paving"),
        ("pedestrian_square_ground", "paving"),
    ),
)
def test_resolver_maps_semantic_surface_to_texture_language(
    surface_role,
    texture_language,
):
    result = AtlasSemanticSurfaceTextureResolver.resolve(
        surface_role=surface_role,
    )

    assert result["surface_role"] == surface_role
    assert result["texture_language"] == texture_language
    assert result["geometry_mode"] == "shallow_relief"


def test_resolver_returns_none_for_unsupported_surface_role():
    assert (
        AtlasSemanticSurfaceTextureResolver.resolve(
            surface_role="unknown_ground",
        )
        is None
    )


@pytest.mark.parametrize(
    (
        "surface_role",
        "expected_max_depth_mm",
        "expected_min_pitch_mm",
    ),
    (
        ("park_ground", 0.20, 1.20),
        ("grass_ground", 0.20, 1.00),
        ("plaza_ground", 0.16, 1.50),
        ("pedestrian_square_ground", 0.16, 1.50),
    ),
)
def test_texture_profiles_expose_restrained_physical_contract(
    surface_role,
    expected_max_depth_mm,
    expected_min_pitch_mm,
):
    result = AtlasSemanticSurfaceTextureResolver.resolve(
        surface_role=surface_role,
    )

    assert 0.0 < result["relief_depth_mm"] <= expected_max_depth_mm
    assert result["feature_pitch_mm"] >= expected_min_pitch_mm
    assert result["lod_min_level"] >= 1


def test_texture_profiles_keep_relief_secondary_to_scene_geometry():
    for surface_role in (
        "park_ground",
        "grass_ground",
        "plaza_ground",
        "pedestrian_square_ground",
    ):
        result = AtlasSemanticSurfaceTextureResolver.resolve(
            surface_role=surface_role,
        )

        assert result["relief_depth_mm"] < 0.25


@pytest.mark.parametrize(
    ("surface_role", "texture_language"),
    (
        ("garden_ground", "lawn"),
        ("cemetery_ground", "ordered_ground"),
        ("sports_field_ground", "field"),
        ("courtyard_ground", "paving"),
    ),
)
def test_resolver_supports_existing_source_backed_ground_roles(
    surface_role,
    texture_language,
):
    result = AtlasSemanticSurfaceTextureResolver.resolve(
        surface_role=surface_role,
    )

    assert result is not None
    assert result["surface_role"] == surface_role
    assert result["texture_language"] == texture_language
    assert result["geometry_mode"] == "shallow_relief"


def test_resolver_does_not_invent_farmland_or_forest_ground_roles():
    assert (
        AtlasSemanticSurfaceTextureResolver.resolve(
            surface_role="farmland_ground",
        )
        is None
    )
    assert (
        AtlasSemanticSurfaceTextureResolver.resolve(
            surface_role="forest_ground",
        )
        is None
    )

@pytest.mark.parametrize(
    (
        "surface_role",
        "expected_relief_depth_mm",
        "expected_feature_pitch_mm",
    ),
    (
        ("park_ground", 0.08, 2.40),
        ("grass_ground", 0.10, 1.80),
    ),
)
def test_lawn_and_grass_profiles_use_calibrated_physical_values(
    surface_role,
    expected_relief_depth_mm,
    expected_feature_pitch_mm,
):
    result = AtlasSemanticSurfaceTextureResolver.resolve(
        surface_role=surface_role,
    )

    assert result["relief_depth_mm"] == pytest.approx(
        expected_relief_depth_mm
    )
    assert result["feature_pitch_mm"] == pytest.approx(
        expected_feature_pitch_mm
    )
