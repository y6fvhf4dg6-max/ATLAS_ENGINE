"""
ATLAS Foundation Mesh Extruder Regression Tests

Genel bina gövdesi motorunun basit ve konkav footprint'lerden
kapalı, manifold ve doğru yükseklikte mesh üretmesini doğrular.
"""

from CORE.atlas_foundation_mesh_extruder import (
    AtlasFoundationMeshExtruder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


class DummyCoordinateEngine:
    """
    Test geometrisini doğrudan milimetre uzayında tutar.
    """

    @staticmethod
    def geometry_to_stl_mm(points):
        return [
            (float(lon), float(lat))
            for lat, lon in points
        ]

    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m)


class DummyBuilding:
    def __init__(
        self,
        geometry,
        area_m2=100.0,
        estimated_height=8.0,
    ):
        self.geometry = geometry
        self.area_m2 = area_m2
        self.estimated_height = estimated_height

        self.is_castle_building = False
        self.castle_profile = None

        self.osm_id = "test-building"
        self.name = "Test Building"


def test_rectangular_building_produces_closed_manifold_mesh():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        estimated_height=8.0,
    )

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=1.25,
    )

    assert mesh is not None
    assert len(mesh["bottom"]) == 4
    assert len(mesh["top"]) == 4

    assert mesh["bottom_z"] == 1.25
    assert mesh["top_z"] == 9.25

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_l_shaped_building_produces_closed_manifold_mesh():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (3.0, 8.0),
            (3.0, 4.0),
            (7.0, 4.0),
            (7.0, 0.0),
        ],
        estimated_height=6.0,
    )

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.75,
    )

    assert mesh is not None
    assert len(mesh["bottom"]) == 6
    assert len(mesh["top"]) == 6

    assert mesh["bottom_z"] == 0.75
    assert mesh["top_z"] == 6.75

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
