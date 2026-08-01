from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)
from CORE.atlas_church_tower_profile_system import (
    AtlasChurchTowerProfileSystem,
)
from CORE.atlas_church_tower_mesher import (
    AtlasChurchTowerMesher,
)
from CORE.atlas_church_tower_window_mesher import (
    AtlasChurchTowerWindowMesher,
)


def _tower_system():
    frame = AtlasChurchFootprintResolver.resolve(
        (
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 60.0),
            (0.0, 60.0),
        )
    )

    profile = AtlasChurchTowerProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        building_height=42.0,
        landmark_class="cathedral",
    )

    return AtlasChurchTowerMesher.build(
        frame=frame,
        profile=profile,
        building_height=42.0,
    )


def test_window_mesher_adds_bell_stage_to_crossing_tower():
    system = _tower_system()

    result = AtlasChurchTowerWindowMesher.apply(
        system
    )

    crossing = next(
        tower
        for tower in result["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    assert crossing["window_stage"]["type"] == "bell_stage"
    assert crossing["window_stage"]["window_count"] == 8
    assert len(crossing["window_meshes"]) == 8


def test_outer_polygon_tower_gets_one_window_per_face():
    system = _tower_system()

    result = AtlasChurchTowerWindowMesher.apply(
        system
    )

    outer = next(
        tower
        for tower in result["towers"]
        if tower["tower_type"] == "outer_polygon_tower"
    )

    assert outer["window_stage"]["window_count"] == 8
    assert len(outer["window_meshes"]) == 8


def test_west_towers_get_four_bell_openings_each():
    system = _tower_system()

    result = AtlasChurchTowerWindowMesher.apply(
        system
    )

    west_towers = [
        tower
        for tower in result["towers"]
        if tower["tower_type"] in {
            "west_tower_left",
            "west_tower_right",
        }
    ]

    assert len(west_towers) == 2

    for tower in west_towers:
        assert tower["window_stage"]["window_count"] == 4
        assert len(tower["window_meshes"]) == 4


def test_window_geometry_is_added_to_tower_triangles():
    system = _tower_system()

    before = {
        tower["tower_type"]: len(tower["triangles"])
        for tower in system["towers"]
    }

    result = AtlasChurchTowerWindowMesher.apply(
        system
    )

    for tower in result["towers"]:
        assert (
            len(tower["triangles"])
            > before[tower["tower_type"]]
        )
