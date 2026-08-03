from collections import Counter

import pytest

from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_tower_builder import (
    AtlasTowerBuilder,
    AtlasTowerGeometry,
)


class Landmark:
    geometry = (
        (0.0, 0.0),
        (4.0, 0.0),
        (4.0, 4.0),
        (0.0, 4.0),
    )
    tags = {
        "height": "54",
        "roof:shape": "pyramidal",
        "roof:height": "10",
    }


def _topology(triangles):
    counts = Counter()

    def key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    for first, second, third in triangles:
        for point_a, point_b in (
            (first, second),
            (second, third),
            (third, first),
        ):
            counts[
                tuple(
                    sorted(
                        (
                            key(point_a),
                            key(point_b),
                        )
                    )
                )
            ] += 1

    return {
        "open": sum(
            count == 1
            for count in counts.values()
        ),
        "non_manifold": sum(
            count > 2
            for count in counts.values()
        ),
    }


def test_generic_tower_uses_osm_pyramidal_roof():
    geometry = AtlasTowerBuilder.build(Landmark())

    assert geometry.roof_shape == "pyramidal"
    assert geometry.roof_height_m == pytest.approx(10.0)

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        geometry
    )

    assert mesh["profile"] == "generic"
    assert mesh["roof_shape"] == "pyramidal"
    assert mesh["body_top_z"] == pytest.approx(44.0)
    assert mesh["roof_top_z"] == pytest.approx(54.0)

    assert len(mesh["body_top"]) == 4
    assert len(mesh["roof_triangles"]) == 4
    assert len(mesh["triangles"]) == 14

    apexes = {
        point
        for triangle in mesh["roof_triangles"]
        for point in triangle
        if point[2] == pytest.approx(54.0)
    }

    assert len(apexes) == 1

    topology = _topology(mesh["triangles"])

    assert topology["open"] == 0
    assert topology["non_manifold"] == 0


def test_clock_tower_profile_builds_broad_staged_body_with_compact_roof():
    geometry = AtlasTowerGeometry(
        footprint=(
            (0.0, 0.0),
            (4.0, 0.0),
            (4.0, 4.0),
            (0.0, 4.0),
        ),
        height_m=54.0,
        profile="clock",
        roof_shape="pyramidal",
        roof_height_m=10.0,
    )

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        geometry
    )

    assert mesh["profile"] == "clock"
    assert mesh["roof_shape"] == "pyramidal"

    assert len(mesh["rings"]) >= 4

    body_base = mesh["rings"][0]
    clock_stage = mesh["rings"][-2]
    roof_base = mesh["rings"][-1]

    def span(ring):
        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]

        return (
            max(xs) - min(xs),
            max(ys) - min(ys),
        )

    base_width, base_depth = span(body_base)
    clock_width, clock_depth = span(clock_stage)
    roof_width, roof_depth = span(roof_base)

    assert clock_width > base_width
    assert clock_depth > base_depth

    assert roof_width < clock_width
    assert roof_depth < clock_depth

    assert mesh["body_top_z"] == pytest.approx(44.0)
    assert mesh["roof_top_z"] == pytest.approx(54.0)

    assert mesh["roof_top_z"] - mesh["body_top_z"] == pytest.approx(
        10.0
    )

    assert len(mesh["triangles"]) > 14


def test_clock_tower_has_vertical_shaft_projecting_clock_stage_and_narrow_roof():
    geometry = AtlasTowerGeometry(
        footprint=(
            (0.0, 0.0),
            (4.0, 0.0),
            (4.0, 4.0),
            (0.0, 4.0),
        ),
        height_m=18.0,
        profile="clock",
        roof_shape="pyramidal",
        roof_height_m=3.3333333333333335,
    )

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        geometry
    )

    rings = mesh["rings"]

    assert len(rings) == 5

    def span(ring):
        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]

        return (
            max(xs) - min(xs),
            max(ys) - min(ys),
        )

    base_width, base_depth = span(rings[0])
    shaft_top_width, shaft_top_depth = span(rings[1])
    clock_base_width, clock_base_depth = span(rings[2])
    clock_top_width, clock_top_depth = span(rings[3])
    roof_base_width, roof_base_depth = span(rings[4])

    # Uzun ana gövde dikey olmalı; obelisk gibi daralmamalı.
    assert shaft_top_width == pytest.approx(base_width)
    assert shaft_top_depth == pytest.approx(base_depth)

    # Saat katı ana gövdeden hafifçe dışarı taşmalı.
    assert clock_base_width > shaft_top_width
    assert clock_base_depth > shaft_top_depth
    assert clock_top_width == pytest.approx(clock_base_width)
    assert clock_top_depth == pytest.approx(clock_base_depth)

    # Ana külah daha dar bir çatı tabanından başlamalı.
    assert roof_base_width < clock_top_width
    assert roof_base_depth < clock_top_depth

    ring_z_values = [
        ring[0][2]
        for ring in rings
    ]

    assert ring_z_values == sorted(ring_z_values)
    assert ring_z_values[1] >= mesh["body_top_z"] * 0.65
    assert ring_z_values[3] < mesh["body_top_z"]
    assert ring_z_values[4] == pytest.approx(
        mesh["body_top_z"]
    )

    assert (
        mesh["roof_top_z"]
        - mesh["body_top_z"]
    ) == pytest.approx(
        3.3333333333333335
    )



def test_clock_tower_side_turrets_are_external_and_tangent_to_main_tower():
    geometry = AtlasTowerGeometry(
        footprint=(
            (0.0, 0.0),
            (4.0, 0.0),
            (4.0, 4.0),
            (0.0, 4.0),
        ),
        height_m=18.0,
        profile="clock",
        roof_shape="pyramidal",
        roof_height_m=3.3333333333333335,
    )

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        geometry
    )

    turrets = mesh["clock_tower_side_turrets"]

    assert len(turrets) == 2
    assert mesh["clock_tower_side_turret_count"] == 2

    left, right = turrets

    assert left["side"] == "left"
    assert right["side"] == "right"

    # Merkezler eski yerleştirme yarıçapına göre sabit kalır.
    assert left["center"][0] == pytest.approx(
        -left["placement_radius"]
    )
    assert right["center"][0] == pytest.approx(
        4.0 + right["placement_radius"]
    )

    # Fiziksel yarıçap büyütülerek ana kuleye hafifçe girer.
    assert left["center"][0] + left["radius"] > 0.0
    assert right["center"][0] - right["radius"] < 4.0

    assert left["radius"] > left["placement_radius"]
    assert right["radius"] > right["placement_radius"]

    from shapely.geometry import Polygon

    main_polygon = Polygon(
        [
            (0.0, 0.0),
            (4.0, 0.0),
            (4.0, 4.0),
            (0.0, 4.0),
        ]
    )

    for turret in turrets:
        turret_polygon = Polygon(
            [
                (point[0], point[1])
                for point in turret["body_rings"][0]
            ]
        )

        assert turret_polygon.intersects(
            main_polygon
        )
        assert turret_polygon.intersection(
            main_polygon
        ).area > 0.0

    # Üç kulenin merkezleri aynı doğruyu oluşturur.
    assert left["center"][1] == pytest.approx(2.0)
    assert right["center"][1] == pytest.approx(2.0)

    for turret in turrets:
        assert len(turret["body_rings"]) == 2
        assert len(turret["body_rings"][0]) == 12
        assert len(turret["cap_triangles"]) == 12
        assert turret["cap_apex"][2] == pytest.approx(
            18.0 * 0.62
        )
