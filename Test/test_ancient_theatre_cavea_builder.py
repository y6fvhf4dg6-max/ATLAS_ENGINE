from CORE.atlas_ancient_theatre_cavea_builder import (
    AtlasAncientTheatreCaveaBuilder,
)
from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_local_osm_reader import (
    AtlasLocalOSMReader,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_terrain_pipeline import (
    AtlasTerrainPipeline,
)


PBF_PATH = "Data/OSM/aspendos-theatre-test.osm.pbf"
BBOX = (36.9365, 31.1695, 36.9410, 31.1750)
SCALE = 5500.0
SIZE_MM = 160.0


def _fixture():
    data = AtlasLocalOSMReader.read(
        PBF_PATH,
        BBOX,
    )

    theatre = next(
        building
        for building in data["buildings"]
        if building.get(
            "tags",
            {},
        ).get("historic") == "theatre"
    )

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=BBOX[0],
        origin_lon=BBOX[1],
        xy_scale=SCALE,
        z_scale=SCALE,
    )

    terrain = AtlasTerrainPipeline.build_terrain_slab(
        bbox=BBOX,
        target_size_mm=SIZE_MM,
        size_x_mm=SIZE_MM,
        size_y_mm=SIZE_MM,
        z_scale=SCALE,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=25,
        terrain_provider_name="srtm",
        smoothing_passes=0,
        debug=False,
    )

    return (
        theatre,
        coordinate_engine,
        terrain,
    )


def test_aspendos_cavea_mesh_is_created():
    theatre, coordinate_engine, terrain = (
        _fixture()
    )

    mesh = AtlasAncientTheatreCaveaBuilder.build(
        raw_building=theatre,
        coordinate_engine=coordinate_engine,
        terrain_mesh=terrain,
    )

    assert mesh is not None
    assert mesh["type"] == (
        "ancient_theatre_cavea"
    )
    assert mesh[
        "ancient_theatre_component"
    ] == "cavea"
    assert len(mesh["triangles"]) > 100


def test_aspendos_cavea_mesh_is_closed():
    theatre, coordinate_engine, terrain = (
        _fixture()
    )

    mesh = AtlasAncientTheatreCaveaBuilder.build(
        raw_building=theatre,
        coordinate_engine=coordinate_engine,
        terrain_mesh=terrain,
    )

    report = AtlasMeshValidator.report(mesh)

    assert report["open_edge_count"] == 0
    assert report[
        "non_manifold_edge_count"
    ] == 0


def test_aspendos_cavea_preserves_inner_opening():
    theatre, coordinate_engine, terrain = (
        _fixture()
    )

    mesh = AtlasAncientTheatreCaveaBuilder.build(
        raw_building=theatre,
        coordinate_engine=coordinate_engine,
        terrain_mesh=terrain,
    )

    xs = [
        point[0]
        for point in mesh["top"]
    ]

    ys = [
        point[1]
        for point in mesh["top"]
    ]

    bounding_width_mm = max(xs) - min(xs)
    bounding_depth_mm = max(ys) - min(ys)

    assert bounding_width_mm > 8.0
    assert bounding_depth_mm > 8.0

    maximum_span_mm = max(
        (
            (
                point_a[0] - point_b[0]
            ) ** 2
            + (
                point_a[1] - point_b[1]
            ) ** 2
        ) ** 0.5
        for point_a in mesh["top"]
        for point_b in mesh["top"]
    )

    assert 16.0 < maximum_span_mm < 18.0

    inner_ring = mesh[
        "placed_bowl_grid"
    ]["top_rings"][0]

    unique_inner_points = {
        (
            round(point[0], 9),
            round(point[1], 9),
        )
        for point in inner_ring
    }

    assert len(inner_ring) == 33
    assert len(unique_inner_points) == 33

    assert (
        mesh["metric_bowl_grid"][
            "inner_radius_m"
        ]
        > 0.0
    )

    assert (
        mesh["metric_bowl_grid"][
            "outer_radius_m"
        ]
        > mesh["metric_bowl_grid"][
            "inner_radius_m"
        ]
    )


def test_invalid_geometry_returns_none():
    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=36.0,
        origin_lon=31.0,
        xy_scale=SCALE,
        z_scale=SCALE,
    )

    diagnostics = {}

    mesh = AtlasAncientTheatreCaveaBuilder.build(
        raw_building={
            "geometry": [
                (36.0, 31.0),
                (36.1, 31.1),
            ],
            "tags": {},
        },
        coordinate_engine=coordinate_engine,
        terrain_mesh={
            "top_points": [],
            "metadata": {},
        },
        diagnostics=diagnostics,
    )

    assert mesh is None
    assert diagnostics["reason"] == (
        "insufficient_geometry"
    )


def test_aspendos_metric_bowl_grid_rises_outward():
    theatre, _, _ = _fixture()

    from CORE.atlas_ancient_theatre_geometry_profiler import (
        AtlasAncientTheatreGeometryProfiler,
    )

    profile = (
        AtlasAncientTheatreGeometryProfiler.profile(
            theatre
        )
    )

    grid = (
        AtlasAncientTheatreCaveaBuilder
        ._build_metric_bowl_grid(
            profile
        )
    )

    assert grid is not None
    assert len(grid["rings"]) == 9
    assert all(
        len(ring) == 33
        for ring in grid["rings"]
    )

    heights = [
        ring[0][2]
        for ring in grid["rings"]
    ]

    assert heights == sorted(heights)
    assert heights[0] == 0.0
    assert abs(
        heights[-1]
        - grid["cavea_rise_m"]
    ) < 1e-9

    assert (
        grid["outer_radius_m"]
        > grid["inner_radius_m"]
    )


def test_aspendos_metric_bowl_has_vertical_cut_edges():
    theatre, _, _ = _fixture()

    from CORE.atlas_ancient_theatre_geometry_profiler import (
        AtlasAncientTheatreGeometryProfiler,
    )

    profile = (
        AtlasAncientTheatreGeometryProfiler.profile(
            theatre
        )
    )

    grid = (
        AtlasAncientTheatreCaveaBuilder
        ._build_metric_bowl_grid(
            profile
        )
    )

    left_cut = [
        ring[0]
        for ring in grid["rings"]
    ]

    right_cut = [
        ring[-1]
        for ring in grid["rings"]
    ]

    left_heights = [
        point[2]
        for point in left_cut
    ]

    right_heights = [
        point[2]
        for point in right_cut
    ]

    assert left_heights == sorted(
        left_heights
    )

    assert right_heights == sorted(
        right_heights
    )

    assert left_heights == right_heights
