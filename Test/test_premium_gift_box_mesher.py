from collections import Counter

import pytest

from CORE.atlas_premium_gift_box_mesher import AtlasPremiumGiftBoxMesher
from CORE.atlas_premium_gift_box_spec import AtlasPremiumGiftBoxSpec


def _vertices(mesh):
    return [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]


def _edge_key(a, b):
    a = tuple(round(float(value), 9) for value in a)
    b = tuple(round(float(value), 9) for value in b)
    return tuple(sorted((a, b)))


def _edge_counts(mesh):
    counts = Counter()

    for triangle in mesh["triangles"]:
        a, b, c = triangle
        counts[_edge_key(a, b)] += 1
        counts[_edge_key(b, c)] += 1
        counts[_edge_key(c, a)] += 1

    return counts


def _assert_closed_manifold(mesh):
    counts = _edge_counts(mesh)

    assert counts
    assert all(count == 2 for count in counts.values())


@pytest.fixture
def spec():
    return AtlasPremiumGiftBoxSpec.for_wall_collection(
        product_width_mm=220.0,
        product_height_mm=220.0,
        product_depth_mm=12.0,
    )


def test_base_builds_open_top_closed_manifold_tray(spec):
    mesh = AtlasPremiumGiftBoxMesher.build_base(spec=spec)

    assert mesh["type"] == "premium_gift_box_base"
    assert mesh["outer_width_mm"] == pytest.approx(226.8)
    assert mesh["outer_height_mm"] == pytest.approx(226.8)
    assert mesh["inner_width_mm"] == pytest.approx(222.0)
    assert mesh["inner_height_mm"] == pytest.approx(222.0)
    assert mesh["total_depth_mm"] == pytest.approx(17.4)

    vertices = _vertices(mesh)

    assert min(x for x, _, _ in vertices) == pytest.approx(-113.4)
    assert max(x for x, _, _ in vertices) == pytest.approx(113.4)
    assert min(y for _, y, _ in vertices) == pytest.approx(-113.4)
    assert max(y for _, y, _ in vertices) == pytest.approx(113.4)
    assert min(z for _, _, z in vertices) == pytest.approx(0.0)
    assert max(z for _, _, z in vertices) == pytest.approx(17.4)

    _assert_closed_manifold(mesh)


def test_base_preserves_product_cavity(spec):
    mesh = AtlasPremiumGiftBoxMesher.build_base(spec=spec)
    vertices = _vertices(mesh)

    inner_x = spec.inner_width_mm / 2.0
    inner_y = spec.inner_height_mm / 2.0

    assert any(
        abs(abs(x) - inner_x) < 1e-9
        and abs(abs(y) - inner_y) < 1e-9
        and z >= spec.floor_thickness_mm
        for x, y, z in vertices
    )


def test_lid_builds_closed_manifold_cap(spec):
    mesh = AtlasPremiumGiftBoxMesher.build_lid(spec=spec)

    assert mesh["type"] == "premium_gift_box_lid"
    assert mesh["outer_width_mm"] == pytest.approx(231.6)
    assert mesh["outer_height_mm"] == pytest.approx(231.6)
    assert mesh["inner_width_mm"] == pytest.approx(227.6)
    assert mesh["inner_height_mm"] == pytest.approx(227.6)
    assert mesh["total_depth_mm"] == pytest.approx(10.0)

    vertices = _vertices(mesh)

    assert min(x for x, _, _ in vertices) == pytest.approx(-115.8)
    assert max(x for x, _, _ in vertices) == pytest.approx(115.8)
    assert min(y for _, y, _ in vertices) == pytest.approx(-115.8)
    assert max(y for _, y, _ in vertices) == pytest.approx(115.8)
    assert min(z for _, _, z in vertices) == pytest.approx(0.0)
    assert max(z for _, _, z in vertices) == pytest.approx(10.0)

    _assert_closed_manifold(mesh)


def test_lid_preserves_flat_personalization_surface(spec):
    mesh = AtlasPremiumGiftBoxMesher.build_lid(spec=spec)

    top_z = spec.lid_total_depth_mm
    top_vertices = [
        vertex
        for vertex in _vertices(mesh)
        if abs(vertex[2] - top_z) < 1e-9
    ]

    assert top_vertices
    assert min(x for x, _, _ in top_vertices) == pytest.approx(-115.8)
    assert max(x for x, _, _ in top_vertices) == pytest.approx(115.8)
    assert min(y for _, y, _ in top_vertices) == pytest.approx(-115.8)
    assert max(y for _, y, _ in top_vertices) == pytest.approx(115.8)



@pytest.mark.parametrize(
    (
        "factory_name",
        "expected_base_width_mm",
        "expected_base_depth_mm",
        "expected_lid_width_mm",
    ),
    (
        (
            "for_mini_wall_collection_v1",
            126.8,
            25.4,
            131.6,
        ),
        (
            "for_original_wall_collection_v1",
            176.8,
            35.4,
            181.6,
        ),
    ),
)
def test_standard_box_meshes_are_closed_manifold(
    factory_name,
    expected_base_width_mm,
    expected_base_depth_mm,
    expected_lid_width_mm,
):
    factory = getattr(
        AtlasPremiumGiftBoxSpec,
        factory_name,
    )
    standard_spec = factory()

    base_mesh = AtlasPremiumGiftBoxMesher.build_base(
        spec=standard_spec,
    )
    lid_mesh = AtlasPremiumGiftBoxMesher.build_lid(
        spec=standard_spec,
    )

    assert base_mesh["outer_width_mm"] == pytest.approx(
        expected_base_width_mm
    )
    assert base_mesh["outer_height_mm"] == pytest.approx(
        expected_base_width_mm
    )
    assert base_mesh["total_depth_mm"] == pytest.approx(
        expected_base_depth_mm
    )

    assert lid_mesh["outer_width_mm"] == pytest.approx(
        expected_lid_width_mm
    )
    assert lid_mesh["outer_height_mm"] == pytest.approx(
        expected_lid_width_mm
    )
    assert lid_mesh["total_depth_mm"] == pytest.approx(10.0)

    _assert_closed_manifold(base_mesh)
    _assert_closed_manifold(lid_mesh)
