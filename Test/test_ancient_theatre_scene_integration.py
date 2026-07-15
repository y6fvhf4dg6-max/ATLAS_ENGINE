from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
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


def _scene():
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
        xy_scale=5500.0,
        z_scale=5500.0,
    )

    terrain = (
        AtlasTerrainPipeline
        .build_terrain_slab(
            bbox=BBOX,
            target_size_mm=160.0,
            size_x_mm=160.0,
            size_y_mm=160.0,
            z_scale=5500.0,
            base_z=0.80,
            bottom_z=0.0,
            grid_size=101,
            terrain_provider_name="srtm",
            smoothing_passes=0,
            debug=False,
        )
    )

    scene = (
        AtlasFoundationSceneBuilder
        .build_scene(
            raw_buildings=[theatre],
            coordinate_engine=(
                coordinate_engine
            ),
            terrain_mesh=terrain,
            castles=[],
            bbox=BBOX,
            target_size_mm=160.0,
            xy_scale=5500.0,
            z_scale=5500.0,
            debug=False,
        )
    )

    return scene


def test_scene_builds_all_ancient_theatre_components():
    scene = _scene()

    building_meshes = scene.layers[
        "buildings"
    ]

    roles = {
        mesh.get("architectural_role")
        for mesh in building_meshes
    }

    assert roles == {
        "ancient_theatre_stage",
        "ancient_theatre_cavea",
        "ancient_theatre_stage_facade",
        "ancient_theatre_upper_gallery",
    }


def test_scene_counts_theatre_as_one_building():
    scene = _scene()

    report = scene.metadata[
        "building_report"
    ]

    assert report["accepted"] == 1
    assert (
        report["accepted_main_buildings"]
        == 1
    )
    assert report["skipped"] == 0


def test_scene_theatre_components_have_triangles():
    scene = _scene()

    building_meshes = scene.layers[
        "buildings"
    ]

    assert len(building_meshes) == 4

    assert all(
        mesh.get("triangles")
        for mesh in building_meshes
    )


def test_scene_theatre_components_are_closed():
    scene = _scene()

    building_meshes = scene.layers[
        "buildings"
    ]

    for mesh in building_meshes:
        if (
            mesh.get("architectural_role")
            == "ancient_theatre_upper_gallery"
        ):
            components = mesh[
                "component_meshes"
            ]
        else:
            components = [mesh]

        for component in components:
            report = (
                AtlasMeshValidator
                ._topology_report(component)
            )

            assert (
                report["open_edge_count"]
                == 0
            )

            assert (
                report[
                    "non_manifold_edge_count"
                ]
                == 0
            )


def test_scene_does_not_emit_standard_building_mesh():
    scene = _scene()

    building_meshes = scene.layers[
        "buildings"
    ]

    assert all(
        mesh.get("architectural_role")
        is not None
        for mesh in building_meshes
    )

    assert not any(
        mesh.get("geometry_type")
        == "foundation_building"
        for mesh in building_meshes
    )
