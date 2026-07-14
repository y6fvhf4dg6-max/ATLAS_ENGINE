from CORE.atlas_ancient_theatre_orchestra_builder import (
    AtlasAncientTheatreOrchestraBuilder,
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


PBF_PATH = (
    "Data/OSM/"
    "aspendos-theatre-test.osm.pbf"
)

BBOX = (
    36.9365,
    31.1695,
    36.9410,
    31.1750,
)

Z_SCALE = 5500.0
SIZE_MM = 160.0


def _fixture():
    data = AtlasLocalOSMReader.read(
        PBF_PATH,
        BBOX,
    )

    theatre = next(
        building
        for building in data["buildings"]
        if (
            building.get("tags", {}).get(
                "historic"
            )
            == "theatre"
        )
    )

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=BBOX[0],
        origin_lon=BBOX[1],
        xy_scale=Z_SCALE,
        z_scale=Z_SCALE,
    )

    terrain = AtlasTerrainPipeline.build_terrain_slab(
        bbox=BBOX,
        target_size_mm=SIZE_MM,
        size_x_mm=SIZE_MM,
        size_y_mm=SIZE_MM,
        z_scale=Z_SCALE,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=25,
        terrain_provider_name="srtm",
        smoothing_passes=0,
        debug=False,
    )

    return theatre, coordinate_engine, terrain


def test_aspendos_orchestra_mesh_is_created():
    theatre, coordinate_engine, terrain = (
        _fixture()
    )

    mesh = (
        AtlasAncientTheatreOrchestraBuilder
        .build(
            raw_building=theatre,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain,
        )
    )

    assert mesh is not None

    assert mesh["type"] == (
        "ancient_theatre_orchestra"
    )

    assert mesh[
        "ancient_theatre_component"
    ] == "orchestra"


def test_aspendos_orchestra_mesh_is_closed():
    theatre, coordinate_engine, terrain = (
        _fixture()
    )

    mesh = (
        AtlasAncientTheatreOrchestraBuilder
        .build(
            raw_building=theatre,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain,
        )
    )

    report = AtlasMeshValidator.report(
        mesh
    )

    assert report["open_edge_count"] == 0
    assert report[
        "non_manifold_edge_count"
    ] == 0


def test_aspendos_orchestra_has_visible_thickness():
    theatre, coordinate_engine, terrain = (
        _fixture()
    )

    mesh = (
        AtlasAncientTheatreOrchestraBuilder
        .build(
            raw_building=theatre,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain,
        )
    )

    assert mesh["top_z"] > mesh["bottom_z"]

    assert (
        mesh["top_z"]
        - mesh["bottom_z"]
    ) >= 0.25


def test_invalid_geometry_returns_none():
    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=36.0,
        origin_lon=31.0,
        xy_scale=Z_SCALE,
        z_scale=Z_SCALE,
    )

    diagnostics = {}

    mesh = (
        AtlasAncientTheatreOrchestraBuilder
        .build(
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
    )

    assert mesh is None

    assert diagnostics["reason"] == (
        "insufficient_geometry"
    )
