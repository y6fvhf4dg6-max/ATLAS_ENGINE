from CORE.atlas_building import AtlasBuilding


def test_zero_building_levels_fall_back_to_building_type_height():
    building = AtlasBuilding(
        building_id=693575043,
        source="osm",
        geometry=[
            (41.0250, 28.9740),
            (41.0250, 28.9741),
            (41.0251, 28.9741),
            (41.0251, 28.9740),
        ],
        tags={
            "building": "school",
            "building:levels": "0",
        },
    )

    assert building.levels == 0
    assert building.estimated_height == 12.0
