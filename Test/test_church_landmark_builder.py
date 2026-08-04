from __future__ import annotations

from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkBuilder,
)
from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


def _landmark(
    *,
    landmark_type=AtlasLandmarkType.CHURCH,
    tags=None,
):
    return AtlasLandmark(
        id=501,
        landmark_type=landmark_type,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 40.0),
            (0.0, 40.0),
        ),
        tags=tags or {},
        source="OSM",
    )


def test_builder_creates_default_church_component_plan():
    result = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    assert result.landmark_id == 501
    assert result.landmark_class == "church"
    assert result.footprint == (
        (0.0, 0.0),
        (20.0, 0.0),
        (20.0, 40.0),
        (0.0, 40.0),
    )

    assert tuple(
        component.component_type
        for component in result.components
    ) == (
        "nave",
        "transept",
        "apse",
        "tower",
        "tower",
        "tower",
        "buttress_system",
        "window_bay_system",
        "roof_section",
        "roof_section",
        "roof_section",
        "roof_section",
    )

    assert tuple(
        component.section_name
        for component in result.components
        if component.component_type == "tower"
    ) == (
        "crossing_tower",
        "front_polygon_tower",
        "west_tower_left",
    )


def test_cathedral_profile_creates_resolved_architectural_towers():
    result = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            tower_count=2,
        ),
    )

    tower_components = tuple(
        component
        for component in result.components
        if component.component_type == "tower"
    )
    spire_components = tuple(
        component
        for component in result.components
        if component.component_type == "spire"
    )

    assert result.landmark_class == "cathedral"
    assert len(tower_components) == 4
    assert spire_components == ()

    assert tuple(
        component.section_name
        for component in tower_components
    ) == (
        "crossing_tower",
        "outer_polygon_tower",
        "west_tower_left",
        "west_tower_right",
    )


def test_builder_uses_osm_height_when_available():
    result = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            tags={
                "height": "42.5",
            },
        ),
        profile=AtlasChurchLandmarkProfile(),
    )

    assert result.height_m == 42.5


def test_builder_uses_landmark_class_fallback_height():
    church = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="church",
        ),
    )

    cathedral = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            tower_count=2,
        ),
    )

    assert church.height_m == (
        AtlasChurchLandmarkBuilder.DEFAULT_CHURCH_HEIGHT_M
    )
    assert cathedral.height_m == (
        AtlasChurchLandmarkBuilder.DEFAULT_CATHEDRAL_HEIGHT_M
    )


def test_builder_rejects_non_church_landmark_type():
    landmark = _landmark(
        landmark_type=AtlasLandmarkType.TOWER,
    )

    try:
        AtlasChurchLandmarkBuilder.build(
            landmark=landmark,
            profile=AtlasChurchLandmarkProfile(),
        )
    except ValueError as exc:
        assert "church or cathedral" in str(exc)
    else:
        raise AssertionError(
            "Expected non-church landmark type to be rejected"
        )


def test_builder_resolves_window_and_buttress_physical_actions():
    result = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        ),
    )

    window_system = next(
        component
        for component in result.components
        if component.component_type == "window_bay_system"
    )
    buttress_system = next(
        component
        for component in result.components
        if component.component_type == "buttress_system"
    )

    assert window_system.physical_action in {
        "preserve",
        "enlarge",
        "omit",
    }
    assert buttress_system.physical_action in {
        "preserve",
        "enlarge",
        "omit",
    }

    assert window_system.resolved_size_mm > 0.0
    assert buttress_system.resolved_size_mm > 0.0


def test_builder_uses_finer_nozzle_to_preserve_more_detail():
    coarse = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        ),
    )

    fine = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.2,
        ),
    )

    coarse_window = next(
        component
        for component in coarse.components
        if component.component_type == "window_bay_system"
    )
    fine_window = next(
        component
        for component in fine.components
        if component.component_type == "window_bay_system"
    )

    assert (
        fine_window.resolved_size_mm
        <= coarse_window.resolved_size_mm
    )


def test_cathedral_geometry_carries_resolved_architectural_tower_profile():
    result = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            tower_count=2,
        ),
    )

    assert tuple(
        tower.tower_type
        for tower in result.tower_profile.towers
    ) == (
        "crossing_tower",
        "outer_polygon_tower",
        "west_tower_left",
        "west_tower_right",
    )

    tower_components = tuple(
        component
        for component in result.components
        if component.component_type == "tower"
    )

    assert len(tower_components) == 4
    assert tuple(
        component.section_name
        for component in tower_components
    ) == (
        "crossing_tower",
        "outer_polygon_tower",
        "west_tower_left",
        "west_tower_right",
    )
