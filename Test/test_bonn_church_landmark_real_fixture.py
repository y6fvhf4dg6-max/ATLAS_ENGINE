from collections import Counter

from CORE.atlas_landmark_mesh_builder import (
    AtlasLandmarkMeshBuilder,
)
from CORE.atlas_landmark_provider_osm import (
    AtlasLandmarkProviderOsm,
)
from CORE.atlas_local_osm_reader import (
    AtlasLocalOSMReader,
)
from CORE.atlas_product_area_engine import (
    AtlasProductAreaEngine,
)


PBF_PATH = "Data/OSM/bonn-muensterplatz-test.osm.pbf"

CENTER_LAT = 50.733992
CENTER_LON = 7.099814
PRODUCT_SIZE_MM = 150.0
SCALE_RATIO = 5500.0


def _topology(triangles):
    edge_counts = Counter()

    def point_key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    for first, second, third in triangles:
        for a, b in (
            (first, second),
            (second, third),
            (third, first),
        ):
            edge = tuple(
                sorted(
                    (
                        point_key(a),
                        point_key(b),
                    )
                )
            )
            edge_counts[edge] += 1

    return {
        "open_edges": sum(
            count == 1
            for count in edge_counts.values()
        ),
        "non_manifold_edges": sum(
            count > 2
            for count in edge_counts.values()
        ),
    }


def _build_real_church_meshes():
    bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=CENTER_LAT,
        center_lon=CENTER_LON,
        product_size_mm=PRODUCT_SIZE_MM,
        scale_ratio=SCALE_RATIO,
        debug=False,
    )

    reader = AtlasLocalOSMReader(bbox)
    reader.apply_file(
        PBF_PATH,
        locations=True,
    )

    meshes = {}

    for raw in reader.landmarks:
        tags = raw.get("tags", {})

        if tags.get("building") not in {
            "church",
            "cathedral",
        }:
            continue

        landmark = AtlasLandmarkProviderOsm.from_osm(
            raw
        )

        meshes[tags.get("name")] = (
            landmark,
            AtlasLandmarkMeshBuilder.build(
                landmark,
                terrain_mesh=None,
            ),
        )

    return meshes


def test_bonn_fixture_builds_kreuzkirche_and_bonner_muenster():
    meshes = _build_real_church_meshes()

    assert "Kreuzkirche" in meshes
    assert "Bonner Münster" in meshes


def test_bonn_real_church_meshes_are_closed_and_manifold():
    meshes = _build_real_church_meshes()

    for _, mesh in meshes.values():
        topology = _topology(
            mesh["triangles"]
        )

        assert topology["open_edges"] == 0
        assert topology["non_manifold_edges"] == 0


def test_bonner_muenster_uses_cathedral_twin_tower_profile():
    meshes = _build_real_church_meshes()

    landmark, mesh = meshes["Bonner Münster"]

    assert landmark.landmark_type.name == "CATHEDRAL"
    assert len(mesh["tower_meshes"]) == 4
    assert mesh["spire_meshes"] == []


def test_bonner_muenster_outer_polygon_tower_center_stays_inside_real_footprint():
    from shapely.geometry import Point, Polygon

    from CORE.atlas_church_footprint_resolver import (
        AtlasChurchFootprintResolver,
    )

    meshes = _build_real_church_meshes()
    landmark, mesh = meshes["Bonner Münster"]

    frame = AtlasChurchFootprintResolver.resolve(
        landmark.geometry
    )
    footprint = Polygon(
        landmark.geometry
    )

    outer = next(
        tower
        for tower in mesh["tower_meshes"]
        if tower["tower_type"]
        == "outer_polygon_tower"
    )

    world_x, world_y = frame.to_world(
        longitudinal=outer["center_longitudinal"],
        lateral=outer["center_lateral"],
    )

    assert footprint.covers(
        Point(world_x, world_y)
    )

def test_bonner_muenster_side_octagon_roof_top_aligns_with_adjacent_aisle_roof():
    import pytest

    meshes = _build_real_church_meshes()
    _, mesh = meshes["Bonner Münster"]

    adjacent_roof = next(
        roof
        for roof in mesh["roof_meshes"]
        if roof["section_type"] == "outer_aisle_right"
    )

    side_octagon = next(
        tower
        for tower in mesh["tower_meshes"]
        if tower["tower_type"] == "outer_polygon_tower"
    )

    assert side_octagon["roof_top_z"] == pytest.approx(
        adjacent_roof["ridge_z"],
        abs=1e-8,
    )


def test_bonner_muenster_has_no_front_apse_addition():
    meshes = _build_real_church_meshes()
    _, mesh = meshes["Bonner Münster"]

    assert mesh["apse_meshes"] == []
    assert all(
        roof["section_type"] != "apse"
        for roof in mesh["roof_meshes"]
    )
