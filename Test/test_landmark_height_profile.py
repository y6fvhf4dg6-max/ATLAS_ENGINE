"""
ATLAS Landmark Height Profile Regression Tests

Normal çevre binaları ile kale landmark yapılarının aynı düşey
ölçeğe mahkûm edilmemesini doğrular.
"""

from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_foundation_mesh_extruder import (
    AtlasFoundationMeshExtruder,
)


class DummyBuilding:
    def __init__(
        self,
        estimated_height,
        is_castle_building=False,
        castle_profile=None,
    ):
        self.estimated_height = estimated_height
        self.is_castle_building = is_castle_building
        self.castle_profile = castle_profile


def test_regular_building_keeps_existing_height_policy():
    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=41.0,
        origin_lon=29.0,
        xy_scale=5500,
        z_scale=5500,
    )

    building = DummyBuilding(
        estimated_height=10.0,
        is_castle_building=False,
    )

    height_mm = AtlasFoundationMeshExtruder._calculate_height(
        building=building,
        coordinate_engine=coordinate_engine,
    )

    assert height_mm == 2.0


def test_main_castle_tower_receives_landmark_vertical_emphasis():
    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=41.0,
        origin_lon=29.0,
        xy_scale=5500,
        z_scale=5500,
    )

    building = DummyBuilding(
        estimated_height=28.0,
        is_castle_building=True,
        castle_profile="main_tower",
    )

    height_mm = AtlasFoundationMeshExtruder._calculate_height(
        building=building,
        coordinate_engine=coordinate_engine,
    )

    assert height_mm == 18.0


def test_defensive_tower_has_minimum_physical_height():
    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=41.0,
        origin_lon=29.0,
        xy_scale=5500,
        z_scale=5500,
    )

    building = DummyBuilding(
        estimated_height=8.0,
        is_castle_building=True,
        castle_profile="defensive_tower",
    )

    height_mm = AtlasFoundationMeshExtruder._calculate_height(
        building=building,
        coordinate_engine=coordinate_engine,
    )

    assert height_mm == 12.0


def test_castle_wing_has_minimum_physical_height():
    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=41.0,
        origin_lon=29.0,
        xy_scale=5500,
        z_scale=5500,
    )

    building = DummyBuilding(
        estimated_height=12.0,
        is_castle_building=True,
        castle_profile="castle_wing",
    )

    height_mm = AtlasFoundationMeshExtruder._calculate_height(
        building=building,
        coordinate_engine=coordinate_engine,
    )

    assert height_mm == 6.0
