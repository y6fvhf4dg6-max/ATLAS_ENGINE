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
        "spire",
        "buttress_system",
        "window_bay_system",
        "roof_section",
        "roof_section",
        "roof_section",
        "roof_section",
    )


def test_cathedral_profile_creates_two_towers_and_two_spires():
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
    assert len(tower_components) == 2
    assert len(spire_components) == 2


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
