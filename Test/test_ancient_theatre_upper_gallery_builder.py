from CORE.atlas_ancient_theatre_cavea_builder import (
    AtlasAncientTheatreCaveaBuilder,
)
from CORE.atlas_ancient_theatre_upper_gallery_builder import (
    AtlasAncientTheatreUpperGalleryBuilder,
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

    cavea = (
        AtlasAncientTheatreCaveaBuilder
        .build(
            raw_building=theatre,
            coordinate_engine=(
                coordinate_engine
            ),
            terrain_mesh=terrain,
        )
    )

    return cavea


def test_aspendos_upper_gallery_builds():
    gallery = (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh=_fixture(),
        )
    )

    assert gallery is not None
    assert gallery["column_count"] == 13
    assert gallery["cap_top_z"] > (
        gallery["cap_base_z"]
    )
    assert gallery["terrace_z"] < (
        gallery["cap_base_z"]
    )


def test_upper_gallery_components_are_closed():
    gallery = (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh=_fixture(),
        )
    )

    for component in gallery[
        "component_meshes"
    ]:
        report = (
            AtlasMeshValidator
            ._topology_report(component)
        )

        assert report["open_edge_count"] == 0
        assert (
            report[
                "non_manifold_edge_count"
            ]
            == 0
        )


def test_upper_gallery_triangle_count_matches_components():
    gallery = (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh=_fixture(),
        )
    )

    expected = sum(
        len(component["triangles"])
        for component in gallery[
            "component_meshes"
        ]
    )

    assert len(
        gallery["triangles"]
    ) == expected


def test_upper_gallery_uses_flat_outer_terrace():
    cavea = _fixture()

    top_rings = cavea[
        "placed_bowl_grid"
    ]["top_rings"]

    assert {
        round(point[2], 9)
        for point in top_rings[-2]
    } == {
        round(point[2], 9)
        for point in top_rings[-1]
    }

    gallery = (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh=cavea,
        )
    )

    assert gallery is not None
    assert gallery["terrace_z"] == (
        top_rings[-1][0][2]
    )


def test_upper_gallery_accepts_custom_dimensions():
    gallery = (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh=_fixture(),
            column_radius_mm=0.40,
            column_height_mm=3.00,
            column_spacing_mm=2.50,
            column_segments=12,
            cap_height_mm=0.70,
        )
    )

    assert (
        gallery["column_radius_mm"]
        == 0.40
    )
    assert (
        gallery["column_height_mm"]
        == 3.00
    )
    assert gallery["cap_height_mm"] == 0.70


def test_upper_gallery_rejects_missing_cavea():
    assert (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh=None,
        )
        is None
    )


def test_upper_gallery_rejects_missing_grid():
    assert (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh={
                "triangles": [],
            },
        )
        is None
    )


def test_upper_gallery_rejects_sloped_outer_band():
    cavea = _fixture()

    top_rings = cavea[
        "placed_bowl_grid"
    ]["top_rings"]

    modified_outer_ring = [
        (
            point[0],
            point[1],
            point[2] + 0.20,
        )
        for point in top_rings[-1]
    ]

    invalid_cavea = {
        **cavea,
        "placed_bowl_grid": {
            **cavea[
                "placed_bowl_grid"
            ],
            "top_rings": [
                *top_rings[:-1],
                modified_outer_ring,
            ],
        },
    }

    assert (
        AtlasAncientTheatreUpperGalleryBuilder
        .build(
            cavea_mesh=invalid_cavea,
        )
        is None
    )
