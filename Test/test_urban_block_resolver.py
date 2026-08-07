from CORE.atlas_urban_block_resolver import (
    AtlasUrbanBlockResolver,
)


def test_urban_block_resolver_groups_generic_buildings_inside_same_block():
    resolver = AtlasUrbanBlockResolver()

    block_polygon = (
        (0.0, 0.0),
        (0.0, 10.0),
        (10.0, 10.0),
        (10.0, 0.0),
    )

    buildings = (
        {
            "element_id": "building_1",
            "centroid": (2.0, 2.0),
            "semantic_class": "generic_building",
        },
        {
            "element_id": "building_2",
            "centroid": (7.0, 7.0),
            "semantic_class": "generic_building",
        },
        {
            "element_id": "landmark_1",
            "centroid": (5.0, 5.0),
            "semantic_class": "landmark",
        },
    )

    result = resolver.resolve_block_members(
        block_id="block_1",
        block_polygon=block_polygon,
        buildings=buildings,
    )

    assert result == (
        "building_1",
        "building_2",
    )


import pytest


def test_urban_block_resolver_rejects_invalid_block_polygon():
    resolver = AtlasUrbanBlockResolver()

    with pytest.raises(ValueError):
        resolver.resolve_block_members(
            block_id="block_1",
            block_polygon=((0.0, 0.0), (1.0, 1.0)),
            buildings=(),
        )


def test_urban_block_resolver_excludes_non_generic_buildings():
    resolver = AtlasUrbanBlockResolver()

    result = resolver.resolve_block_members(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "landmark_1",
                "centroid": (5.0, 5.0),
                "semantic_class": "landmark",
            },
        ),
    )

    assert result == ()


def test_urban_block_resolver_accepts_generic_building_by_footprint_overlap():
    resolver = AtlasUrbanBlockResolver()

    result = resolver.resolve_block_members(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (11.0, 5.0),
                "footprint": (
                    (9.0, 4.0),
                    (9.0, 6.0),
                    (11.0, 6.0),
                    (11.0, 4.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert result == ("building_1",)


def test_urban_block_resolver_rejects_boundary_touch_without_area_overlap():
    resolver = AtlasUrbanBlockResolver()

    result = resolver.resolve_block_members(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (11.0, 5.0),
                "footprint": (
                    (10.0, 4.0),
                    (10.0, 6.0),
                    (12.0, 6.0),
                    (12.0, 4.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert result == ()


def test_urban_block_resolver_rejects_invalid_self_intersecting_block_polygon():
    resolver = AtlasUrbanBlockResolver()

    with pytest.raises(ValueError):
        resolver.resolve_block_members(
            block_id="block_1",
            block_polygon=(
                (0.0, 0.0),
                (10.0, 10.0),
                (0.0, 10.0),
                (10.0, 0.0),
            ),
            buildings=(),
        )


from CORE.atlas_urban_block_resolver import (
    AtlasUrbanBlockProfile,
)


def test_urban_block_profile_preserves_block_identity_and_members():
    profile = AtlasUrbanBlockProfile(
        block_id=" Block 1 ",
        member_element_ids=(
            " Building 1 ",
            "building_2",
        ),
    )

    assert profile.block_id == "block_1"
    assert profile.member_element_ids == (
        "building_1",
        "building_2",
    )


def test_urban_block_profile_rejects_duplicate_members():
    with pytest.raises(ValueError):
        AtlasUrbanBlockProfile(
            block_id="block_1",
            member_element_ids=(
                "building_1",
                " Building 1 ",
            ),
        )


def test_urban_block_resolver_builds_block_profile():
    resolver = AtlasUrbanBlockResolver()

    profile = resolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (2.0, 2.0),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile == AtlasUrbanBlockProfile(
        block_id="block_1",
        member_element_ids=("building_1",),
    )


def test_urban_block_profile_reports_footprint_density():
    resolver = AtlasUrbanBlockResolver()

    profile = resolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (2.0, 2.0),
                "footprint": (
                    (1.0, 1.0),
                    (1.0, 3.0),
                    (3.0, 3.0),
                    (3.0, 1.0),
                ),
                "semantic_class": "generic_building",
            },
            {
                "element_id": "building_2",
                "centroid": (7.0, 7.0),
                "footprint": (
                    (6.0, 6.0),
                    (6.0, 8.0),
                    (8.0, 8.0),
                    (8.0, 6.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile.density_ratio == pytest.approx(0.08)


def test_urban_block_profile_keeps_member_without_footprint_but_excludes_it_from_density():
    resolver = AtlasUrbanBlockResolver()

    profile = resolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (2.0, 2.0),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile.member_element_ids == ("building_1",)
    assert profile.density_ratio == pytest.approx(0.0)


def test_urban_block_profile_does_not_double_count_overlapping_footprints():
    resolver = AtlasUrbanBlockResolver()

    profile = resolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (3.0, 3.0),
                "footprint": (
                    (1.0, 1.0),
                    (1.0, 5.0),
                    (5.0, 5.0),
                    (5.0, 1.0),
                ),
                "semantic_class": "generic_building",
            },
            {
                "element_id": "building_2",
                "centroid": (5.0, 5.0),
                "footprint": (
                    (3.0, 3.0),
                    (3.0, 7.0),
                    (7.0, 7.0),
                    (7.0, 3.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile.density_ratio == pytest.approx(0.28)


def test_urban_block_profile_reports_median_member_height():
    resolver = AtlasUrbanBlockResolver()

    profile = resolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (2.0, 2.0),
                "semantic_class": "generic_building",
                "estimated_height_m": 10.0,
            },
            {
                "element_id": "building_2",
                "centroid": (5.0, 5.0),
                "semantic_class": "generic_building",
                "estimated_height_m": 14.0,
            },
            {
                "element_id": "building_3",
                "centroid": (8.0, 8.0),
                "semantic_class": "generic_building",
                "estimated_height_m": 30.0,
            },
        ),
    )

    assert profile.median_height_m == pytest.approx(14.0)


def test_urban_block_profile_rejects_negative_median_height():
    with pytest.raises(ValueError):
        AtlasUrbanBlockProfile(
            block_id="block_1",
            member_element_ids=("building_1",),
            median_height_m=-1.0,
        )


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_urban_block_profile_rejects_non_finite_median_height(value):
    with pytest.raises(ValueError):
        AtlasUrbanBlockProfile(
            block_id="block_1",
            member_element_ids=("building_1",),
            median_height_m=value,
        )


def test_urban_block_profile_ignores_non_finite_member_heights():
    resolver = AtlasUrbanBlockResolver()

    profile = resolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (2.0, 2.0),
                "semantic_class": "generic_building",
                "estimated_height_m": 10.0,
            },
            {
                "element_id": "building_2",
                "centroid": (5.0, 5.0),
                "semantic_class": "generic_building",
                "estimated_height_m": float("nan"),
            },
            {
                "element_id": "building_3",
                "centroid": (8.0, 8.0),
                "semantic_class": "generic_building",
                "estimated_height_m": float("inf"),
            },
        ),
    )

    assert profile.median_height_m == pytest.approx(10.0)


def test_urban_block_profile_reports_nearest_landmark_distance():
    resolver = AtlasUrbanBlockResolver()

    profile = resolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (2.0, 2.0),
                "semantic_class": "generic_building",
            },
        ),
        landmarks=(
            {
                "element_id": "landmark_1",
                "centroid": (15.0, 5.0),
            },
        ),
    )

    assert profile.nearest_landmark_distance == pytest.approx(10.0)


def test_urban_block_profile_rejects_negative_landmark_distance():
    with pytest.raises(ValueError):
        AtlasUrbanBlockProfile(
            block_id="block_1",
            member_element_ids=("building_1",),
            nearest_landmark_distance=-1.0,
        )


from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)


def test_urban_block_profile_preserves_composition_lod_level():
    lod_level = AtlasLoDLevelCatalog.resolve(2)

    profile = AtlasUrbanBlockProfile(
        block_id="block_1",
        member_element_ids=("building_1",),
        composition_lod_level=lod_level,
    )

    assert profile.composition_lod_level is lod_level


def test_urban_block_resolver_passes_composition_lod_into_profile():
    lod_level = AtlasLoDLevelCatalog.resolve(1)

    profile = AtlasUrbanBlockResolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(),
        composition_lod_level=lod_level,
    )

    assert profile.composition_lod_level is lod_level


def test_urban_block_profile_reports_shared_boundary_length():
    profile = AtlasUrbanBlockResolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (2.0, 2.0),
                "footprint": (
                    (1.0, 1.0),
                    (1.0, 3.0),
                    (3.0, 3.0),
                    (3.0, 1.0),
                ),
                "semantic_class": "generic_building",
            },
            {
                "element_id": "building_2",
                "centroid": (4.0, 2.0),
                "footprint": (
                    (3.0, 1.0),
                    (3.0, 3.0),
                    (5.0, 3.0),
                    (5.0, 1.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile.shared_boundary_length == pytest.approx(2.0)


def test_urban_block_density_preserves_inner_courtyard_void():
    profile = AtlasUrbanBlockResolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (3.0, 3.0),
                "footprint": (
                    (1.0, 1.0),
                    (1.0, 5.0),
                    (5.0, 5.0),
                    (5.0, 1.0),
                ),
                "inner_geometries": (
                    (
                        (2.0, 2.0),
                        (2.0, 4.0),
                        (4.0, 4.0),
                        (4.0, 2.0),
                    ),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile.density_ratio == pytest.approx(0.12)


def test_urban_block_shared_boundary_ignores_inner_courtyard_boundaries():
    profile = AtlasUrbanBlockResolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (3.0, 3.0),
                "footprint": (
                    (1.0, 1.0),
                    (1.0, 5.0),
                    (5.0, 5.0),
                    (5.0, 1.0),
                ),
                "inner_geometries": (
                    (
                        (2.0, 2.0),
                        (2.0, 4.0),
                        (4.0, 4.0),
                        (4.0, 2.0),
                    ),
                ),
                "semantic_class": "generic_building",
            },
            {
                "element_id": "building_2",
                "centroid": (6.0, 3.0),
                "footprint": (
                    (5.0, 2.0),
                    (5.0, 4.0),
                    (7.0, 4.0),
                    (7.0, 2.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile.shared_boundary_length == pytest.approx(2.0)


def test_urban_block_profile_reports_courtyard_count():
    profile = AtlasUrbanBlockResolver.resolve_block_profile(
        block_id="block_1",
        block_polygon=(
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (3.0, 3.0),
                "footprint": (
                    (1.0, 1.0),
                    (1.0, 5.0),
                    (5.0, 5.0),
                    (5.0, 1.0),
                ),
                "inner_geometries": (
                    (
                        (2.0, 2.0),
                        (2.0, 4.0),
                        (4.0, 4.0),
                        (4.0, 2.0),
                    ),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profile.courtyard_count == 1


def test_urban_block_resolver_resolves_multiple_source_blocks():
    profiles = AtlasUrbanBlockResolver.resolve_block_profiles(
        blocks=(
            {
                "block_id": "block_1",
                "polygon": (
                    (0.0, 0.0),
                    (0.0, 10.0),
                    (10.0, 10.0),
                    (10.0, 0.0),
                ),
            },
            {
                "block_id": "block_2",
                "polygon": (
                    (20.0, 0.0),
                    (20.0, 10.0),
                    (30.0, 10.0),
                    (30.0, 0.0),
                ),
            },
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (5.0, 5.0),
                "semantic_class": "generic_building",
            },
            {
                "element_id": "building_2",
                "centroid": (25.0, 5.0),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert tuple(
        profile.block_id
        for profile in profiles
    ) == (
        "block_1",
        "block_2",
    )

    assert profiles[0].member_element_ids == (
        "building_1",
    )
    assert profiles[1].member_element_ids == (
        "building_2",
    )


def test_urban_block_resolver_rejects_duplicate_block_ids():
    with pytest.raises(ValueError):
        AtlasUrbanBlockResolver.resolve_block_profiles(
            blocks=(
                {
                    "block_id": "block_1",
                    "polygon": (
                        (0.0, 0.0),
                        (0.0, 10.0),
                        (10.0, 10.0),
                        (10.0, 0.0),
                    ),
                },
                {
                    "block_id": " Block 1 ",
                    "polygon": (
                        (20.0, 0.0),
                        (20.0, 10.0),
                        (30.0, 10.0),
                        (30.0, 0.0),
                    ),
                },
            ),
            buildings=(),
        )


def test_urban_block_resolver_polygonizes_closed_road_centerlines():
    blocks = AtlasUrbanBlockResolver.resolve_road_defined_blocks(
        road_segments=(
            {"centerline": [(0.0, 0.0), (0.0, 10.0)]},
            {"centerline": [(0.0, 10.0), (10.0, 10.0)]},
            {"centerline": [(10.0, 10.0), (10.0, 0.0)]},
            {"centerline": [(10.0, 0.0), (0.0, 0.0)]},
        ),
    )

    assert len(blocks) == 1
    assert blocks[0]["block_id"] == "road_block_1"
    assert len(blocks[0]["polygon"]) == 4


def test_urban_block_resolver_ignores_open_road_centerlines():
    blocks = AtlasUrbanBlockResolver.resolve_road_defined_blocks(
        road_segments=(
            {"centerline": [(0.0, 0.0), (0.0, 10.0)]},
            {"centerline": [(0.0, 10.0), (10.0, 10.0)]},
            {"centerline": [(10.0, 10.0), (10.0, 0.0)]},
        ),
    )

    assert blocks == ()


def test_urban_block_resolver_assigns_deterministic_road_block_ids():
    segments = (
        {"centerline": [(0.0, 0.0), (0.0, 10.0)]},
        {"centerline": [(0.0, 10.0), (10.0, 10.0)]},
        {"centerline": [(10.0, 10.0), (10.0, 0.0)]},
        {"centerline": [(10.0, 0.0), (0.0, 0.0)]},
        {"centerline": [(20.0, 0.0), (20.0, 10.0)]},
        {"centerline": [(20.0, 10.0), (30.0, 10.0)]},
        {"centerline": [(30.0, 10.0), (30.0, 0.0)]},
        {"centerline": [(30.0, 0.0), (20.0, 0.0)]},
    )

    forward = AtlasUrbanBlockResolver.resolve_road_defined_blocks(
        road_segments=segments,
    )
    reversed_result = AtlasUrbanBlockResolver.resolve_road_defined_blocks(
        road_segments=tuple(reversed(segments)),
    )

    assert forward == reversed_result
    assert tuple(block["block_id"] for block in forward) == (
        "road_block_1",
        "road_block_2",
    )


def test_urban_block_resolver_keeps_building_membership_block_local():
    profiles = AtlasUrbanBlockResolver.resolve_block_profiles(
        blocks=(
            {
                "block_id": "block_1",
                "polygon": (
                    (0.0, 0.0),
                    (0.0, 10.0),
                    (10.0, 10.0),
                    (10.0, 0.0),
                ),
            },
            {
                "block_id": "block_2",
                "polygon": (
                    (20.0, 0.0),
                    (20.0, 10.0),
                    (30.0, 10.0),
                    (30.0, 0.0),
                ),
            },
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (5.0, 5.0),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profiles[0].member_element_ids == ("building_1",)
    assert profiles[1].member_element_ids == ()


def test_urban_block_resolver_exposes_ambiguous_multi_block_overlap():
    profiles = AtlasUrbanBlockResolver.resolve_block_profiles(
        blocks=(
            {
                "block_id": "block_1",
                "polygon": (
                    (0.0, 0.0),
                    (0.0, 10.0),
                    (10.0, 10.0),
                    (10.0, 0.0),
                ),
            },
            {
                "block_id": "block_2",
                "polygon": (
                    (8.0, 0.0),
                    (8.0, 10.0),
                    (18.0, 10.0),
                    (18.0, 0.0),
                ),
            },
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (9.0, 5.0),
                "footprint": (
                    (8.5, 4.0),
                    (8.5, 6.0),
                    (9.5, 6.0),
                    (9.5, 4.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    memberships = tuple(
        profile.block_id
        for profile in profiles
        if "building_1" in profile.member_element_ids
    )

    assert memberships == (
        "block_1",
        "block_2",
    )


def test_urban_block_resolver_assigns_building_to_largest_overlap_block():
    profiles = AtlasUrbanBlockResolver.resolve_exclusive_block_profiles(
        blocks=(
            {
                "block_id": "block_1",
                "polygon": (
                    (0.0, 0.0),
                    (0.0, 10.0),
                    (10.0, 10.0),
                    (10.0, 0.0),
                ),
            },
            {
                "block_id": "block_2",
                "polygon": (
                    (8.0, 0.0),
                    (8.0, 10.0),
                    (18.0, 10.0),
                    (18.0, 0.0),
                ),
            },
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (9.5, 5.0),
                "footprint": (
                    (8.0, 4.0),
                    (8.0, 6.0),
                    (12.0, 6.0),
                    (12.0, 4.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profiles[0].member_element_ids == ()
    assert profiles[1].member_element_ids == (
        "building_1",
    )


def test_urban_block_resolver_breaks_equal_overlap_by_block_id():
    profiles = AtlasUrbanBlockResolver.resolve_exclusive_block_profiles(
        blocks=(
            {
                "block_id": "block_b",
                "polygon": (
                    (0.0, 0.0),
                    (0.0, 10.0),
                    (10.0, 10.0),
                    (10.0, 0.0),
                ),
            },
            {
                "block_id": "block_a",
                "polygon": (
                    (10.0, 0.0),
                    (10.0, 10.0),
                    (20.0, 10.0),
                    (20.0, 0.0),
                ),
            },
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (10.0, 5.0),
                "footprint": (
                    (9.0, 4.0),
                    (9.0, 6.0),
                    (11.0, 6.0),
                    (11.0, 4.0),
                ),
                "semantic_class": "generic_building",
            },
        ),
    )

    memberships = {
        profile.block_id: profile.member_element_ids
        for profile in profiles
    }

    assert memberships["block_a"] == ("building_1",)
    assert memberships["block_b"] == ()


def test_urban_block_resolver_assigns_centroid_only_building_exclusively():
    profiles = AtlasUrbanBlockResolver.resolve_exclusive_block_profiles(
        blocks=(
            {
                "block_id": "block_1",
                "polygon": (
                    (0.0, 0.0),
                    (0.0, 10.0),
                    (10.0, 10.0),
                    (10.0, 0.0),
                ),
            },
            {
                "block_id": "block_2",
                "polygon": (
                    (20.0, 0.0),
                    (20.0, 10.0),
                    (30.0, 10.0),
                    (30.0, 0.0),
                ),
            },
        ),
        buildings=(
            {
                "element_id": "building_1",
                "centroid": (5.0, 5.0),
                "semantic_class": "generic_building",
            },
        ),
    )

    assert profiles[0].member_element_ids == (
        "building_1",
    )
    assert profiles[1].member_element_ids == ()


from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricElement,
    AtlasUrbanFabricScene,
)


def test_urban_block_resolver_integrates_block_membership_into_scene():
    profile = AtlasUrbanBlockProfile(
        block_id="block_1",
        member_element_ids=("building_1",),
        density_ratio=0.25,
    )

    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="building_1",
                semantic_class="generic_building",
            ),
        ),
    )

    result = AtlasUrbanBlockResolver.integrate_profile_into_scene(
        scene=scene,
        profile=profile,
    )

    block = result.get_element("block_1")

    assert block is not None
    assert block.semantic_class == "urban_block"

    assert len(result.relationships) == 1
    assert result.relationships[0].relation_type == "contains_building"
    assert result.relationships[0].source_element_id == "block_1"
    assert result.relationships[0].target_element_id == "building_1"


def test_urban_block_resolver_integrates_multiple_profiles_into_scene():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="building_1",
                semantic_class="generic_building",
            ),
            AtlasUrbanFabricElement(
                element_id="building_2",
                semantic_class="generic_building",
            ),
        ),
    )

    result = AtlasUrbanBlockResolver.integrate_profiles_into_scene(
        scene=scene,
        profiles=(
            AtlasUrbanBlockProfile(
                block_id="block_1",
                member_element_ids=("building_1",),
            ),
            AtlasUrbanBlockProfile(
                block_id="block_2",
                member_element_ids=("building_2",),
            ),
        ),
    )

    assert result.get_element("block_1") is not None
    assert result.get_element("block_2") is not None
    assert tuple(
        relationship.relationship_id
        for relationship in result.relationships
    ) == (
        "block_1_contains_building_1",
        "block_2_contains_building_2",
    )


def test_urban_block_resolver_requires_scene_members_to_exist():
    scene = AtlasUrbanFabricScene()

    profile = AtlasUrbanBlockProfile(
        block_id="block_1",
        member_element_ids=("building_1",),
    )

    with pytest.raises(ValueError):
        AtlasUrbanBlockResolver.integrate_profile_into_scene(
            scene=scene,
            profile=profile,
        )
