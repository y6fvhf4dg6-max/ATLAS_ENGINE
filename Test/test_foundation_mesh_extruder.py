"""
ATLAS Foundation Mesh Extruder Regression Tests

Genel bina gövdesi motorunun basit ve konkav footprint'lerden
kapalı, manifold ve doğru yükseklikte mesh üretmesini doğrular.
"""

import pytest

from CORE.atlas_foundation_mesh_extruder import (
    AtlasFoundationMeshExtruder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_mesh_builder import AtlasMeshBuilder


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
        min_height=None,
        min_level=None,
        is_building_part=False,
        tags=None,
    ):
        self.geometry = geometry
        self.area_m2 = area_m2
        self.estimated_height = estimated_height
        self.min_height = min_height
        self.min_level = min_level
        self.is_building_part = is_building_part
        self.tags = dict(tags or {})

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



def test_small_building_reports_area_rejection_reason():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        area_m2=12.0,
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics["accepted"] is False
    assert diagnostics["reason"] == "building_area_below_minimum"
    assert diagnostics["area_m2"] == 12.0
    assert diagnostics["minimum_area_m2"] == 20.0


def test_narrow_building_reports_width_rejection_reason():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.80),
            (6.0, 0.80),
            (6.0, 0.0),
        ],
        area_m2=100.0,
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics["accepted"] is False
    assert diagnostics["reason"] == "model_width_below_minimum"
    assert diagnostics["model_width_mm"] == 0.80
    assert diagnostics["minimum_width_mm"] == 1.20



def test_building_part_starts_at_explicit_min_height():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        estimated_height=25.0,
        min_height=22.0,
    )

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=1.0,
    )

    assert mesh is not None
    assert mesh["base_offset_mm"] == 22.0
    assert mesh["bottom_z"] == 23.0
    assert mesh["top_z"] == 26.0

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_building_part_uses_min_level_when_min_height_is_missing():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        estimated_height=12.0,
        min_level=2,
    )

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.5,
    )

    assert mesh is not None
    assert mesh["base_offset_mm"] == 6.0
    assert mesh["bottom_z"] == 6.5
    assert mesh["top_z"] == 12.5


def test_explicit_min_height_has_priority_over_min_level():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        estimated_height=25.0,
        min_height=22.0,
        min_level=6,
    )

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
    )

    assert mesh is not None
    assert mesh["base_offset_mm"] == 22.0
    assert mesh["bottom_z"] == 22.0
    assert mesh["top_z"] == 25.0


def test_invalid_vertical_range_is_rejected():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        estimated_height=10.0,
        min_height=12.0,
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics["accepted"] is False
    assert diagnostics["reason"] == "invalid_vertical_range"



def test_thin_elevated_part_is_thickened_downward():
    class ScaledCoordinateEngine(DummyCoordinateEngine):
        @staticmethod
        def height_to_stl_mm(height_m):
            return float(height_m) * 1000.0 / 5500.0

    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        estimated_height=25.0,
        min_height=22.0,
    )

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=ScaledCoordinateEngine(),
        foundation_z=0.0,
    )

    assert mesh is not None
    assert mesh["top_z"] == 25.0 * 1000.0 / 5500.0
    assert mesh["vertical_part_thickness_mm"] == pytest.approx(0.80)
    assert mesh["vertical_part_thickness_adjusted"] is True
    assert mesh["bottom_z"] == pytest.approx(
        mesh["top_z"] - 0.80
    )


def test_thick_elevated_part_keeps_original_vertical_range():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 8.0),
            (6.0, 8.0),
            (6.0, 0.0),
        ],
        estimated_height=25.0,
        min_height=22.0,
    )

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
    )

    assert mesh is not None
    assert mesh["bottom_z"] == 22.0
    assert mesh["top_z"] == 25.0
    assert mesh["vertical_part_thickness_mm"] == 3.0
    assert mesh["vertical_part_thickness_adjusted"] is False


def test_small_building_part_bypasses_area_filter_when_physically_printable():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 1.30),
            (1.20, 1.30),
            (1.20, 0.0),
        ],
        area_m2=7.5,
        estimated_height=4.0,
        is_building_part=True,
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is not None
    assert diagnostics["accepted"] is True

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_small_regular_building_still_uses_area_filter():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 1.30),
            (1.20, 1.30),
            (1.20, 0.0),
        ],
        area_m2=7.5,
        estimated_height=4.0,
        is_building_part=False,
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics["reason"] == "building_area_below_minimum"



def test_tiny_building_part_still_uses_physical_dimension_filter():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 1.30),
            (0.80, 1.30),
            (0.80, 0.0),
        ],
        area_m2=5.0,
        estimated_height=4.0,
        is_building_part=True,
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics["accepted"] is False
    assert diagnostics["reason"] == "model_depth_below_minimum"



def test_legacy_mesh_builder_allows_physically_printable_building_part():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 1.30),
            (1.20, 1.30),
            (1.20, 0.0),
        ],
        area_m2=7.5,
        estimated_height=4.0,
        is_building_part=True,
    )

    diagnostics = {}

    points = AtlasMeshBuilder.prepare_geometry(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        diagnostics=diagnostics,
    )

    assert points is not None
    assert diagnostics == {}


def test_building_part_accepts_printable_narrow_column_dimensions():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 1.27),
            (1.13, 1.27),
            (1.13, 0.0),
        ],
        area_m2=7.5,
        estimated_height=22.0,
        is_building_part=True,
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is not None
    assert diagnostics["accepted"] is True


def test_legacy_mesh_builder_accepts_printable_narrow_column_dimensions():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 1.27),
            (1.13, 1.27),
            (1.13, 0.0),
        ],
        area_m2=7.5,
        estimated_height=22.0,
        is_building_part=True,
    )

    diagnostics = {}

    points = AtlasMeshBuilder.prepare_geometry(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        diagnostics=diagnostics,
    )

    assert points is not None
    assert diagnostics == {}



def test_submillimeter_minaret_footprint_is_preserved():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.70),
            (0.70, 0.70),
            (0.70, 0.0),
        ],
        area_m2=10.0,
        estimated_height=12.0,
        is_building_part=True,
        tags={
            "building:part": "yes",
            "man_made": "tower",
            "tower:type": "minaret",
            "height": "72",
            "roof:shape": "pyramidal",
        },
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is not None
    assert diagnostics["accepted"] is True
    assert mesh["bottom_z"] == pytest.approx(0.0)
    assert mesh["top_z"] == pytest.approx(12.0)

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_legacy_mesh_builder_preserves_submillimeter_minaret_footprint():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.70),
            (0.70, 0.70),
            (0.70, 0.0),
        ],
        area_m2=10.0,
        estimated_height=12.0,
        is_building_part=True,
        tags={
            "building:part": "yes",
            "man_made": "tower",
            "tower:type": "minaret",
            "height": "72",
            "roof:shape": "pyramidal",
        },
    )

    diagnostics = {}

    points = AtlasMeshBuilder.prepare_geometry(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        diagnostics=diagnostics,
    )

    assert points is not None
    assert diagnostics == {}

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    assert max(xs) - min(xs) == pytest.approx(1.0)
    assert max(ys) - min(ys) == pytest.approx(1.0)

def test_suspect_building_report_is_silent_when_debug_is_false(
    capsys,
):
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.80),
            (6.0, 0.80),
            (6.0, 0.0),
        ],
        area_m2=100.0,
    )

    AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        debug=False,
    )

    captured = capsys.readouterr()

    assert (
        "ATLAS GEOMETRY INSPECTOR — SUSPECT BUILDING"
        not in captured.out
    )


def test_suspect_building_report_is_printed_when_debug_is_true(
    capsys,
):
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.80),
            (6.0, 0.80),
            (6.0, 0.0),
        ],
        area_m2=100.0,
    )

    AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        debug=True,
    )

    captured = capsys.readouterr()

    assert (
        "ATLAS GEOMETRY INSPECTOR — SUSPECT BUILDING"
        in captured.out
    )


def test_legacy_mesh_builder_is_silent_when_debug_is_false(
    capsys,
):
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.80),
            (6.0, 0.80),
            (6.0, 0.0),
        ],
        area_m2=100.0,
    )

    AtlasMeshBuilder.build_mesh(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        debug=False,
    )

    captured = capsys.readouterr()

    assert (
        "ATLAS GEOMETRY INSPECTOR — SUSPECT BUILDING"
        not in captured.out
    )


def test_legacy_mesh_builder_prints_report_when_debug_is_true(
    capsys,
):
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.80),
            (6.0, 0.80),
            (6.0, 0.0),
        ],
        area_m2=100.0,
    )

    AtlasMeshBuilder.build_mesh(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        debug=True,
    )

    captured = capsys.readouterr()

    assert (
        "ATLAS GEOMETRY INSPECTOR — SUSPECT BUILDING"
        in captured.out
    )


def test_monument_column_part_expands_to_printable_dimensions():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.75),
            (0.82, 0.75),
            (0.82, 0.0),
        ],
        area_m2=7.5,
        estimated_height=15.0,
        is_building_part=True,
        tags={
            "building:part": "yes",
            "atlas:monument_column_part": "yes",
        },
    )

    diagnostics = {}

    mesh = AtlasFoundationMeshExtruder.extrude(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        foundation_z=0.0,
        diagnostics=diagnostics,
    )

    assert mesh is not None
    assert diagnostics["accepted"] is True

    xs = [point[0] for point in mesh["bottom"]]
    ys = [point[1] for point in mesh["bottom"]]

    assert max(xs) - min(xs) == pytest.approx(1.0)
    assert max(ys) - min(ys) == pytest.approx(1.0)


def test_legacy_mesh_builder_expands_monument_column_part():
    building = DummyBuilding(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.75),
            (0.82, 0.75),
            (0.82, 0.0),
        ],
        area_m2=7.5,
        estimated_height=15.0,
        is_building_part=True,
        tags={
            "building:part": "yes",
            "atlas:monument_column_part": "yes",
        },
    )

    diagnostics = {}

    points = AtlasMeshBuilder.prepare_geometry(
        building=building,
        coordinate_engine=DummyCoordinateEngine(),
        diagnostics=diagnostics,
    )

    assert points is not None
    assert diagnostics == {}

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    assert max(xs) - min(xs) == pytest.approx(1.0)
    assert max(ys) - min(ys) == pytest.approx(1.0)
