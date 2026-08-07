import pytest

from CORE.atlas_urban_road_hierarchy_resolver import (
    AtlasUrbanRoadHierarchyResolver,
)


@pytest.mark.parametrize(
    "highway,expected",
    [
        ("primary", "major_road"),
        ("secondary", "major_road"),
        ("tertiary", "major_road"),
        ("residential", "local_road"),
        ("living_street", "local_road"),
        ("unclassified", "local_road"),
        ("road", "local_road"),
        ("service", "service_road"),
        ("footway", "pedestrian_path"),
        ("path", "pedestrian_path"),
        ("pedestrian", "pedestrian_path"),
        ("steps", "pedestrian_path"),
        ("cycleway", "cycleway"),
        ("bridleway", "bridleway"),
    ],
)
def test_urban_road_hierarchy_resolves_highway_semantics(
    highway,
    expected,
):
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_highway(
            highway
        )
        == expected
    )


def test_urban_road_hierarchy_returns_none_for_unknown_highway():
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_highway(
            "construction"
        )
        is None
    )


def test_urban_road_hierarchy_normalizes_highway_value():
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_highway(
            " PRIMARY "
        )
        == "major_road"
    )


@pytest.mark.parametrize(
    "highway",
    [
        "motorway",
        "trunk",
    ],
)
def test_urban_road_hierarchy_preserves_top_level_vehicle_roads(
    highway,
):
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_highway(
            highway
        )
        == "major_road"
    )


from CORE.atlas_urban_road_hierarchy_resolver import (
    AtlasUrbanRoadProfile,
)


def test_urban_road_profile_preserves_product_properties():
    profile = AtlasUrbanRoadProfile(
        semantic_class=" major road ",
        semantic_priority=0.90,
        physical_width_mm=1.80,
        minimum_printable_width_mm=0.80,
        vertical_treatment=" raised ",
        lod_eligible=True,
        simplification_priority=0.85,
    )

    assert profile.semantic_class == "major_road"
    assert profile.semantic_priority == pytest.approx(0.90)
    assert profile.physical_width_mm == pytest.approx(1.80)
    assert profile.minimum_printable_width_mm == pytest.approx(0.80)
    assert profile.vertical_treatment == "raised"
    assert profile.lod_eligible is True
    assert profile.simplification_priority == pytest.approx(0.85)


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("semantic_priority", -0.01),
        ("semantic_priority", 1.01),
        ("simplification_priority", -0.01),
        ("simplification_priority", 1.01),
        ("physical_width_mm", 0.0),
        ("minimum_printable_width_mm", 0.0),
    ],
)
def test_urban_road_profile_rejects_invalid_product_values(
    field_name,
    value,
):
    values = {
        "semantic_class": "major_road",
        "semantic_priority": 0.9,
        "physical_width_mm": 1.8,
        "minimum_printable_width_mm": 0.8,
        "vertical_treatment": "raised",
        "lod_eligible": True,
        "simplification_priority": 0.8,
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        AtlasUrbanRoadProfile(**values)


def test_urban_road_profile_requires_boolean_lod_eligibility():
    with pytest.raises(TypeError):
        AtlasUrbanRoadProfile(
            semantic_class="major_road",
            semantic_priority=0.9,
            physical_width_mm=1.8,
            minimum_printable_width_mm=0.8,
            vertical_treatment="raised",
            lod_eligible=1,
            simplification_priority=0.8,
        )


def test_urban_road_profile_rejects_print_minimum_above_physical_width():
    with pytest.raises(ValueError):
        AtlasUrbanRoadProfile(
            semantic_class="local_road",
            semantic_priority=0.6,
            physical_width_mm=0.8,
            minimum_printable_width_mm=1.0,
            vertical_treatment="raised",
            lod_eligible=True,
            simplification_priority=0.5,
        )


def test_urban_road_profiles_preserve_relative_visual_hierarchy():
    major = AtlasUrbanRoadProfile(
        semantic_class="major_road",
        semantic_priority=0.9,
        physical_width_mm=1.8,
        minimum_printable_width_mm=0.8,
        vertical_treatment="raised",
        lod_eligible=True,
        simplification_priority=0.9,
    )
    local = AtlasUrbanRoadProfile(
        semantic_class="local_road",
        semantic_priority=0.7,
        physical_width_mm=1.4,
        minimum_printable_width_mm=0.8,
        vertical_treatment="raised",
        lod_eligible=True,
        simplification_priority=0.7,
    )
    service = AtlasUrbanRoadProfile(
        semantic_class="service_road",
        semantic_priority=0.5,
        physical_width_mm=1.0,
        minimum_printable_width_mm=0.8,
        vertical_treatment="raised",
        lod_eligible=True,
        simplification_priority=0.5,
    )
    pedestrian = AtlasUrbanRoadProfile(
        semantic_class="pedestrian_path",
        semantic_priority=0.3,
        physical_width_mm=0.8,
        minimum_printable_width_mm=0.8,
        vertical_treatment="raised",
        lod_eligible=True,
        simplification_priority=0.3,
    )

    AtlasUrbanRoadHierarchyResolver.validate_relative_hierarchy(
        (
            major,
            local,
            service,
            pedestrian,
        )
    )


def test_urban_road_profiles_reject_inverted_relative_hierarchy():
    major = AtlasUrbanRoadProfile(
        semantic_class="major_road",
        semantic_priority=0.9,
        physical_width_mm=1.0,
        minimum_printable_width_mm=0.8,
        vertical_treatment="raised",
        lod_eligible=True,
        simplification_priority=0.9,
    )
    local = AtlasUrbanRoadProfile(
        semantic_class="local_road",
        semantic_priority=0.7,
        physical_width_mm=1.4,
        minimum_printable_width_mm=0.8,
        vertical_treatment="raised",
        lod_eligible=True,
        simplification_priority=0.7,
    )

    with pytest.raises(ValueError):
        AtlasUrbanRoadHierarchyResolver.validate_relative_hierarchy(
            (
                major,
                local,
            )
        )


def test_urban_road_hierarchy_resolves_scaled_physical_width():
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_physical_width_mm(
            real_width_m=8.0,
            scale_ratio=4000.0,
            minimum_printable_width_mm=0.8,
        )
        == pytest.approx(2.0)
    )


def test_urban_road_hierarchy_enforces_minimum_printable_width():
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_physical_width_mm(
            real_width_m=2.0,
            scale_ratio=5000.0,
            minimum_printable_width_mm=0.8,
        )
        == pytest.approx(0.8)
    )


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("real_width_m", 0.0),
        ("scale_ratio", 0.0),
        ("minimum_printable_width_mm", 0.0),
    ],
)
def test_urban_road_hierarchy_rejects_invalid_width_resolution_input(
    field_name,
    value,
):
    values = {
        "real_width_m": 5.0,
        "scale_ratio": 5000.0,
        "minimum_printable_width_mm": 0.8,
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        AtlasUrbanRoadHierarchyResolver.resolve_physical_width_mm(
            **values
        )


@pytest.mark.parametrize(
    "source_width,default_width,expected",
    [
        ("7.5", 5.0, 7.5),
        ("7.5 m", 5.0, 7.5),
        (7.5, 5.0, 7.5),
        (None, 5.0, 5.0),
        ("invalid", 5.0, 5.0),
        ("0", 5.0, 5.0),
        ("-2", 5.0, 5.0),
    ],
)
def test_urban_road_hierarchy_resolves_source_width_m(
    source_width,
    default_width,
    expected,
):
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_source_width_m(
            source_width=source_width,
            default_width_m=default_width,
        )
        == pytest.approx(expected)
    )


@pytest.mark.parametrize(
    "default_width",
    [
        0.0,
        -1.0,
    ],
)
def test_urban_road_hierarchy_rejects_invalid_default_width(
    default_width,
):
    with pytest.raises(ValueError):
        AtlasUrbanRoadHierarchyResolver.resolve_source_width_m(
            source_width=None,
            default_width_m=default_width,
        )


@pytest.mark.parametrize(
    "highway,expected_width_m",
    [
        ("motorway", 12.0),
        ("trunk", 10.0),
        ("primary", 8.0),
        ("secondary", 7.0),
        ("tertiary", 6.0),
        ("residential", 5.0),
        ("service", 4.0),
        ("living_street", 4.0),
        ("unclassified", 5.0),
        ("road", 5.0),
    ],
)
def test_urban_road_hierarchy_preserves_existing_vehicle_default_widths(
    highway,
    expected_width_m,
):
    assert (
        AtlasUrbanRoadHierarchyResolver.default_width_m(
            highway
        )
        == pytest.approx(expected_width_m)
    )


def test_urban_road_hierarchy_returns_none_without_default_width():
    assert (
        AtlasUrbanRoadHierarchyResolver.default_width_m(
            "footway"
        )
        is None
    )


def test_urban_road_hierarchy_resolves_major_road_product_profile():
    profile = AtlasUrbanRoadHierarchyResolver.resolve_profile(
        highway="primary",
        source_width="8 m",
        scale_ratio=4000.0,
        minimum_printable_width_mm=0.8,
    )

    assert isinstance(profile, AtlasUrbanRoadProfile)
    assert profile.semantic_class == "major_road"
    assert profile.physical_width_mm == pytest.approx(2.0)
    assert profile.minimum_printable_width_mm == pytest.approx(0.8)
    assert profile.vertical_treatment == "foundation_raised"
    assert profile.lod_eligible is True


def test_urban_road_hierarchy_returns_none_for_unsupported_profile():
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_profile(
            highway="construction",
            source_width=None,
            scale_ratio=4000.0,
            minimum_printable_width_mm=0.8,
        )
        is None
    )


@pytest.mark.parametrize(
    "highway,expected_class,source_width,expected_width_mm",
    [
        ("residential", "local_road", None, 1.25),
        ("service", "service_road", None, 1.00),
    ],
)
def test_urban_road_hierarchy_resolves_vehicle_product_profiles(
    highway,
    expected_class,
    source_width,
    expected_width_mm,
):
    profile = AtlasUrbanRoadHierarchyResolver.resolve_profile(
        highway=highway,
        source_width=source_width,
        scale_ratio=4000.0,
        minimum_printable_width_mm=0.8,
    )

    assert isinstance(profile, AtlasUrbanRoadProfile)
    assert profile.semantic_class == expected_class
    assert profile.physical_width_mm == pytest.approx(
        expected_width_mm
    )
    assert profile.vertical_treatment == "foundation_raised"
    assert profile.lod_eligible is True


@pytest.mark.parametrize(
    "highway",
    [
        "footway",
        "path",
        "pedestrian",
        "steps",
    ],
)
def test_urban_road_hierarchy_resolves_pedestrian_product_profile(
    highway,
):
    profile = AtlasUrbanRoadHierarchyResolver.resolve_profile(
        highway=highway,
        source_width=None,
        scale_ratio=4000.0,
        minimum_printable_width_mm=0.8,
    )

    assert isinstance(profile, AtlasUrbanRoadProfile)
    assert profile.semantic_class == "pedestrian_path"
    assert profile.physical_width_mm == pytest.approx(0.8)
    assert profile.minimum_printable_width_mm == pytest.approx(0.8)
    assert profile.vertical_treatment == "foundation_raised"
    assert profile.lod_eligible is True
    assert profile.semantic_priority == pytest.approx(0.30)
    assert profile.simplification_priority == pytest.approx(0.30)


def test_urban_road_hierarchy_uses_source_width_for_pedestrian_profile():
    profile = AtlasUrbanRoadHierarchyResolver.resolve_profile(
        highway="footway",
        source_width="4 m",
        scale_ratio=4000.0,
        minimum_printable_width_mm=0.8,
    )

    assert profile.physical_width_mm == pytest.approx(1.0)


def test_urban_road_hierarchy_does_not_invent_pedestrian_source_width():
    profile = AtlasUrbanRoadHierarchyResolver.resolve_profile(
        highway="footway",
        source_width="invalid",
        scale_ratio=500.0,
        minimum_printable_width_mm=0.8,
    )

    assert profile.physical_width_mm == pytest.approx(0.8)


@pytest.mark.parametrize(
    "highway,semantic_class",
    [
        ("cycleway", "cycleway"),
        ("bridleway", "bridleway"),
    ],
)
def test_urban_road_hierarchy_defers_linear_corridor_profiles_to_8_3(
    highway,
    semantic_class,
):
    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_highway(
            highway
        )
        == semantic_class
    )

    assert (
        AtlasUrbanRoadHierarchyResolver.resolve_profile(
            highway=highway,
            source_width=None,
            scale_ratio=4000.0,
            minimum_printable_width_mm=0.8,
        )
        is None
    )
