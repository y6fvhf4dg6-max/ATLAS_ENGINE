import pytest

from CORE.atlas_linear_infrastructure_resolver import (
    AtlasLinearInfrastructureResolver,
)


@pytest.mark.parametrize(
    "tags,expected",
    [
        ({"railway": "rail"}, "railway"),
        ({"railway": "light_rail"}, "light_rail"),
        ({"railway": "tram"}, "tram"),
        ({"highway": "cycleway"}, "cycle_corridor"),
        ({"highway": "bridleway"}, "bridleway_corridor"),
    ],
)
def test_linear_infrastructure_resolves_semantic_class(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_semantic_class(
            tags
        )
        == expected
    )


@pytest.mark.parametrize(
    "tags,expected",
    [
        ({"railway": "rail"}, "active"),
        ({"railway": "proposed"}, "proposed"),
        ({"railway": "disused"}, "disused"),
        ({"railway": "rail", "proposed": "yes"}, "proposed"),
        ({"railway": "rail", "disused": "yes"}, "disused"),
    ],
)
def test_linear_infrastructure_resolves_operational_state(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_operational_state(
            tags
        )
        == expected
    )


@pytest.mark.parametrize(
    "tags,expected",
    [
        ({"railway": "rail"}, True),
        ({"railway": "tram"}, True),
        ({"railway": "light_rail", "tunnel": "yes"}, False),
        ({"highway": "cycleway", "tunnel": "yes"}, False),
    ],
)
def test_linear_infrastructure_resolves_surface_visibility(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.is_surface_visible(
            tags
        )
        is expected
    )


from CORE.atlas_linear_infrastructure_resolver import (
    AtlasLinearInfrastructureProfile,
)


def test_linear_infrastructure_profile_preserves_product_properties():
    profile = AtlasLinearInfrastructureProfile(
        semantic_class=" railway ",
        visual_priority=0.85,
        physical_width_mm=1.6,
        minimum_printable_width_mm=0.8,
        parallel_line_representation=True,
        lod_eligible=True,
    )

    assert profile.semantic_class == "railway"
    assert profile.visual_priority == pytest.approx(0.85)
    assert profile.physical_width_mm == pytest.approx(1.6)
    assert profile.minimum_printable_width_mm == pytest.approx(0.8)
    assert profile.parallel_line_representation is True
    assert profile.lod_eligible is True


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("visual_priority", -0.01),
        ("visual_priority", 1.01),
        ("physical_width_mm", 0.0),
        ("minimum_printable_width_mm", 0.0),
    ],
)
def test_linear_infrastructure_profile_rejects_invalid_values(
    field_name,
    value,
):
    values = {
        "semantic_class": "railway",
        "visual_priority": 0.85,
        "physical_width_mm": 1.6,
        "minimum_printable_width_mm": 0.8,
        "parallel_line_representation": True,
        "lod_eligible": True,
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        AtlasLinearInfrastructureProfile(**values)


def test_linear_infrastructure_profile_rejects_print_minimum_above_width():
    with pytest.raises(ValueError):
        AtlasLinearInfrastructureProfile(
            semantic_class="railway",
            visual_priority=0.85,
            physical_width_mm=0.8,
            minimum_printable_width_mm=1.0,
            parallel_line_representation=True,
            lod_eligible=True,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "parallel_line_representation",
        "lod_eligible",
    ],
)
def test_linear_infrastructure_profile_requires_boolean_flags(
    field_name,
):
    values = {
        "semantic_class": "railway",
        "visual_priority": 0.85,
        "physical_width_mm": 1.6,
        "minimum_printable_width_mm": 0.8,
        "parallel_line_representation": True,
        "lod_eligible": True,
    }
    values[field_name] = 1

    with pytest.raises(TypeError):
        AtlasLinearInfrastructureProfile(**values)


@pytest.mark.parametrize(
    "real_width_m,scale_ratio,minimum_printable_width_mm,expected",
    [
        (8.0, 4000.0, 0.8, 2.0),
        (2.0, 5000.0, 0.8, 0.8),
        (3.0, 3000.0, 0.6, 1.0),
    ],
)
def test_linear_infrastructure_physical_width_uses_scale_and_print_minimum(
    real_width_m,
    scale_ratio,
    minimum_printable_width_mm,
    expected,
):
    result = AtlasLinearInfrastructureResolver.resolve_physical_width_mm(
        real_width_m=real_width_m,
        scale_ratio=scale_ratio,
        minimum_printable_width_mm=minimum_printable_width_mm,
    )

    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("real_width_m", 0.0),
        ("scale_ratio", 0.0),
        ("minimum_printable_width_mm", 0.0),
        ("real_width_m", float("inf")),
    ],
)
def test_linear_infrastructure_physical_width_rejects_invalid_inputs(
    field_name,
    value,
):
    values = {
        "real_width_m": 4.0,
        "scale_ratio": 4000.0,
        "minimum_printable_width_mm": 0.8,
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        AtlasLinearInfrastructureResolver.resolve_physical_width_mm(
            **values
        )


@pytest.mark.parametrize(
    "gauge_mm,scale_ratio,line_width_mm,minimum_gap_mm,expected",
    [
        (1435.0, 1000.0, 0.4, 0.2, True),
        (1435.0, 4738.0, 0.4, 0.2, False),
        (1000.0, 5000.0, 0.3, 0.1, False),
    ],
)
def test_parallel_line_representation_requires_printable_source_spacing(
    gauge_mm,
    scale_ratio,
    line_width_mm,
    minimum_gap_mm,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver
        .resolve_parallel_line_representation(
            gauge_mm=gauge_mm,
            scale_ratio=scale_ratio,
            line_width_mm=line_width_mm,
            minimum_gap_mm=minimum_gap_mm,
        )
        is expected
    )


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("gauge_mm", 0.0),
        ("scale_ratio", 0.0),
        ("line_width_mm", 0.0),
        ("minimum_gap_mm", -0.1),
    ],
)
def test_parallel_line_representation_rejects_invalid_dimensions(
    field_name,
    value,
):
    values = {
        "gauge_mm": 1435.0,
        "scale_ratio": 4738.0,
        "line_width_mm": 0.4,
        "minimum_gap_mm": 0.2,
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        AtlasLinearInfrastructureResolver.resolve_parallel_line_representation(
            **values
        )


def test_tram_profile_without_source_width_uses_printable_minimum():
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags={
            "railway": "tram",
            "gauge": "1435",
        },
        scale_ratio=4738.0,
        minimum_printable_width_mm=0.8,
        line_width_mm=0.4,
        minimum_gap_mm=0.2,
    )

    assert profile is not None
    assert profile.semantic_class == "tram"
    assert profile.physical_width_mm == pytest.approx(0.8)
    assert profile.minimum_printable_width_mm == pytest.approx(0.8)
    assert profile.parallel_line_representation is False
    assert profile.lod_eligible is True


def test_tram_profile_uses_valid_source_width_when_available():
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags={
            "railway": "tram",
            "gauge": "1435",
            "width": "6.0",
        },
        scale_ratio=3000.0,
        minimum_printable_width_mm=0.8,
        line_width_mm=0.4,
        minimum_gap_mm=0.2,
    )

    assert profile is not None
    assert profile.physical_width_mm == pytest.approx(2.0)


def test_parallel_rail_profile_is_enabled_only_when_gauge_is_print_readable():
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags={
            "railway": "rail",
            "gauge": "1435",
        },
        scale_ratio=1000.0,
        minimum_printable_width_mm=0.8,
        line_width_mm=0.4,
        minimum_gap_mm=0.2,
    )

    assert profile is not None
    assert profile.parallel_line_representation is True


def test_cycle_corridor_profile_never_requires_rail_parallel_lines():
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags={
            "highway": "cycleway",
            "width": "3.0",
        },
        scale_ratio=3000.0,
        minimum_printable_width_mm=0.6,
        line_width_mm=0.4,
        minimum_gap_mm=0.2,
    )

    assert profile is not None
    assert profile.semantic_class == "cycle_corridor"
    assert profile.physical_width_mm == pytest.approx(1.0)
    assert profile.parallel_line_representation is False


def test_unsupported_linear_infrastructure_returns_no_profile():
    assert (
        AtlasLinearInfrastructureResolver.resolve_profile(
            tags={"railway": "monorail"},
            scale_ratio=3000.0,
            minimum_printable_width_mm=0.8,
            line_width_mm=0.4,
            minimum_gap_mm=0.2,
        )
        is None
    )












@pytest.mark.parametrize(
    "tags,expected",
    [
        (
            {
                "railway": "proposed",
                "proposed": "light_rail",
            },
            "light_rail",
        ),
        (
            {
                "railway": "disused",
                "disused:railway": "tram",
            },
            "tram",
        ),
        (
            {
                "railway": "platform",
                "tram": "yes",
            },
            None,
        ),
    ],
)
def test_linear_infrastructure_preserves_underlying_rail_semantics(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_semantic_class(
            tags
        )
        == expected
    )


@pytest.mark.parametrize(
    "highway",
    [
        "footway",
        "path",
        "pedestrian",
        "steps",
    ],
)
def test_linear_infrastructure_resolves_pedestrian_path_semantics(
    highway,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_semantic_class(
            {"highway": highway}
        )
        == "pedestrian_path"
    )


@pytest.mark.parametrize(
    "tags,expected",
    [
        (
            {"man_made": "embankment"},
            "embankment",
        ),
        (
            {
                "railway": "rail",
                "embankment": "yes",
            },
            "railway",
        ),
    ],
)
def test_linear_infrastructure_resolves_embankment_semantics(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_semantic_class(
            tags
        )
        == expected
    )


@pytest.mark.parametrize(
    "tags,expected",
    [
        (
            {"landuse": "railway"},
            "infrastructure_corridor",
        ),
        (
            {
                "railway": "light_rail",
                "service": "yard",
            },
            "light_rail",
        ),
        (
            {
                "public_transport": "platform",
            },
            None,
        ),
        (
            {
                "railway": "platform",
                "public_transport": "platform",
            },
            None,
        ),
    ],
)
def test_linear_infrastructure_resolves_major_strip_semantics(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_semantic_class(
            tags
        )
        == expected
    )




@pytest.mark.parametrize(
    "tags,expected_semantic",
    [
        (
            {"highway": "footway"},
            "pedestrian_path",
        ),
        (
            {"man_made": "embankment"},
            "embankment",
        ),
        (
            {"landuse": "railway"},
            "infrastructure_corridor",
        ),
    ],
)
def test_linear_infrastructure_profile_covers_required_8_3_classes(
    tags,
    expected_semantic,
):
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags=tags,
        scale_ratio=4738.0,
        minimum_printable_width_mm=0.8,
        line_width_mm=0.4,
        minimum_gap_mm=0.2,
    )

    assert profile is not None
    assert profile.semantic_class == expected_semantic
    assert profile.physical_width_mm == pytest.approx(0.8)
    assert profile.parallel_line_representation is False
    assert profile.lod_eligible is True


@pytest.mark.parametrize(
    "tags,expected",
    [
        (
            {"railway": "tram"},
            "surface",
        ),
        (
            {
                "railway": "tram",
                "bridge": "yes",
                "layer": "1",
            },
            "bridge_elevated",
        ),
        (
            {
                "railway": "light_rail",
                "tunnel": "yes",
                "layer": "-2",
            },
            "subsurface",
        ),
        (
            {
                "highway": "footway",
                "tunnel": "building_passage",
            },
            "subsurface",
        ),
        (
            {
                "railway": "tram",
                "layer": "1",
            },
            "surface",
        ),
    ],
)
def test_linear_infrastructure_resolves_vertical_interaction_context(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_vertical_treatment(
            tags
        )
        == expected
    )


@pytest.mark.parametrize(
    "tags,expected",
    [
        (
            {"railway": "tram"},
            "surface",
        ),
        (
            {
                "railway": "tram",
                "bridge": "yes",
            },
            "bridge_elevated",
        ),
        (
            {
                "railway": "light_rail",
                "tunnel": "yes",
            },
            "subsurface",
        ),
    ],
)
def test_linear_infrastructure_profile_preserves_vertical_treatment(
    tags,
    expected,
):
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags=tags,
        scale_ratio=4738.0,
        minimum_printable_width_mm=0.8,
        line_width_mm=0.4,
        minimum_gap_mm=0.2,
    )

    assert profile is not None
    assert profile.vertical_treatment == expected


@pytest.mark.parametrize(
    "tags,expected",
    [
        (
            {"railway": "tram"},
            True,
        ),
        (
            {
                "railway": "tram",
                "bridge": "yes",
            },
            True,
        ),
        (
            {
                "railway": "light_rail",
                "tunnel": "yes",
            },
            False,
        ),
        (
            {
                "railway": "proposed",
                "proposed": "light_rail",
                "tunnel": "yes",
            },
            False,
        ),
        (
            {
                "railway": "disused",
                "disused:railway": "tram",
            },
            False,
        ),
    ],
)
def test_linear_infrastructure_resolves_product_surface_eligibility(
    tags,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver
        .is_product_surface_eligible(tags)
        is expected
    )


@pytest.mark.parametrize(
    "tags,is_closed,expected",
    [
        (
            {"railway": "tram"},
            False,
            "linear_strip",
        ),
        (
            {"highway": "cycleway"},
            False,
            "linear_strip",
        ),
        (
            {"man_made": "embankment"},
            False,
            "linear_strip",
        ),
        (
            {"landuse": "railway"},
            True,
            "area_strip",
        ),
    ],
)
def test_linear_infrastructure_resolves_geometry_kind(
    tags,
    is_closed,
    expected,
):
    assert (
        AtlasLinearInfrastructureResolver.resolve_geometry_kind(
            tags=tags,
            is_closed=is_closed,
        )
        == expected
    )


def test_linear_infrastructure_rejects_closed_area_corridor_as_linear_strip():
    assert (
        AtlasLinearInfrastructureResolver.resolve_geometry_kind(
            tags={"landuse": "railway"},
            is_closed=False,
        )
        is None
    )


def test_building_passage_is_not_surface_visible():
    tags = {
        "highway": "footway",
        "tunnel": "building_passage",
    }

    assert (
        AtlasLinearInfrastructureResolver
        .is_surface_visible(tags)
        is False
    )


def test_building_passage_is_not_product_surface_eligible():
    tags = {
        "highway": "footway",
        "tunnel": "building_passage",
    }

    assert (
        AtlasLinearInfrastructureResolver
        .is_product_surface_eligible(tags)
        is False
    )
