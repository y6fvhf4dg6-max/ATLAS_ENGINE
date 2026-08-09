from types import SimpleNamespace

import pytest

from CORE.atlas_foundation_mesh_extruder import (
    AtlasFoundationMeshExtruder,
)


class _CoordinateEngine:
    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m) * 1000.0 / 5500.0


def _building(
    *,
    estimated_height=40.0,
    tags=None,
    is_castle_building=False,
):
    return SimpleNamespace(
        estimated_height=float(estimated_height),
        tags=dict(tags or {}),
        is_castle_building=is_castle_building,
        castle_profile=None,
        is_building_part=False,
    )


def test_generic_extruder_can_use_separate_product_height_without_mutating_source_truth():
    building = _building(
        estimated_height=40.0,
    )

    height_mm = AtlasFoundationMeshExtruder._calculate_height(
        building,
        _CoordinateEngine(),
        product_height_m=20.0,
    )

    assert building.estimated_height == pytest.approx(40.0)
    assert height_mm == pytest.approx(
        20.0 * 1000.0 / 5500.0
    )


def test_generic_extruder_preserves_legacy_height_when_no_product_override_exists():
    building = _building(
        estimated_height=12.0,
    )

    height_mm = AtlasFoundationMeshExtruder._calculate_height(
        building,
        _CoordinateEngine(),
    )

    assert height_mm == pytest.approx(
        12.0 * 1000.0 / 5500.0
    )


def test_castle_height_policy_ignores_generic_product_height_override():
    building = _building(
        estimated_height=20.0,
        is_castle_building=True,
    )

    height_mm = AtlasFoundationMeshExtruder._calculate_height(
        building,
        _CoordinateEngine(),
        product_height_m=8.0,
    )

    source_scaled = (
        20.0 * 1000.0 / 5500.0
    )

    assert height_mm > (
        8.0 * 1000.0 / 5500.0
    )
    assert height_mm >= source_scaled


def test_extrude_signature_accepts_product_height_override(monkeypatch):
    captured = {}

    monkeypatch.setattr(
        AtlasFoundationMeshExtruder,
        "_prepare_geometry",
        staticmethod(
            lambda building, coordinate_engine, diagnostics=None, debug=False: (
                (0.0, 0.0),
                (1.0, 0.0),
                (1.0, 1.0),
                (0.0, 1.0),
            )
        ),
    )

    original = AtlasFoundationMeshExtruder._calculate_height

    def capture_height(building, coordinate_engine, product_height_m=None):
        captured["product_height_m"] = product_height_m
        return original(
            building,
            coordinate_engine,
            product_height_m=product_height_m,
        )

    monkeypatch.setattr(
        AtlasFoundationMeshExtruder,
        "_calculate_height",
        staticmethod(capture_height),
    )

    # Geometry creation can fail later in this focused propagation test.
    try:
        AtlasFoundationMeshExtruder.extrude(
            building=_building(estimated_height=20.0),
            coordinate_engine=_CoordinateEngine(),
            foundation_z=0.0,
            product_height_m=12.0,
        )
    except Exception:
        pass

    assert captured["product_height_m"] == pytest.approx(12.0)
