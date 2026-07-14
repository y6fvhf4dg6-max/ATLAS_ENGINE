from CORE.atlas_ancient_theatre_profiler import (
    AtlasAncientTheatreProfiler,
)


class DummyBuilding:
    def __init__(self):
        self.tags = {}


def test_historic_theatre_is_classified():
    profile = AtlasAncientTheatreProfiler.profile(
        {
            "tags": {
                "historic": "theatre",
            }
        }
    )

    assert profile["is_ancient_theatre"] is True
    assert profile["replace_standard_building_mesh"] is True
    assert profile["matched_by"] == ("historic",)


def test_archaeological_site_theatre_is_classified():
    profile = AtlasAncientTheatreProfiler.profile(
        {
            "tags": {
                "archaeological_site": "theatre",
            }
        }
    )

    assert profile["is_ancient_theatre"] is True
    assert profile["matched_by"] == (
        "archaeological_site",
    )


def test_amphitheatre_value_is_supported():
    profile = AtlasAncientTheatreProfiler.profile(
        {
            "tags": {
                "historic": "amphitheatre",
            }
        }
    )

    assert profile["is_ancient_theatre"] is True


def test_normal_building_is_not_classified():
    profile = AtlasAncientTheatreProfiler.profile(
        {
            "tags": {
                "building": "yes",
            }
        }
    )

    assert profile["is_ancient_theatre"] is False
    assert profile["replace_standard_building_mesh"] is False


def test_ruins_does_not_disable_component_heights():
    profile = AtlasAncientTheatreProfiler.profile(
        {
            "tags": {
                "historic": "theatre",
                "ruins": "yes",
            }
        }
    )

    assert profile["is_ruin"] is True
    assert profile["preserve_component_heights"] is True


def test_apply_to_building_sets_atlas_metadata():
    atlas_building = DummyBuilding()

    result = AtlasAncientTheatreProfiler.apply_to_building(
        atlas_building=atlas_building,
        raw_building={
            "tags": {
                "historic": "theatre",
                "historic:civilization": "ancient_roman",
            }
        },
    )

    assert result is atlas_building
    assert result.is_ancient_theatre is True
    assert result.ancient_theatre_profile[
        "is_ancient_civilization"
    ] is True
    assert result.tags["atlas:ancient_theatre"] == "yes"
    assert (
        result.tags[
            "atlas:replace_standard_building_mesh"
        ]
        == "yes"
    )
