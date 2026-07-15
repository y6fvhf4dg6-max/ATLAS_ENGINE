import pytest

from CORE.atlas_ancient_theatre_stage_builder import (
    AtlasAncientTheatreStageBuilder,
)
from CORE.atlas_ancient_theatre_stage_facade_builder import (
    AtlasAncientTheatreStageFacadeBuilder,
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

    stage = (
        AtlasAncientTheatreStageBuilder
        .build(
            raw_building=theatre,
            coordinate_engine=(
                coordinate_engine
            ),
            terrain_mesh=terrain,
        )
    )

    return stage


def test_aspendos_stage_facade_builds():
    facade = (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=_fixture(),
        )
    )

    assert facade is not None
    assert facade["column_count"] == 9
    assert facade["row_count"] == 3
    assert facade["panel_count"] == 27


def test_stage_facade_components_are_closed():
    facade = (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=_fixture(),
        )
    )

    for component in facade[
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


def test_stage_facade_stays_below_wall_top():
    facade = (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=_fixture(),
        )
    )

    assert facade[
        "top_clearance_mm"
    ] > 0.0

    assert (
        facade["facade_top_z"]
        < facade["wall_top_z"]
    )


def test_stage_facade_triangle_count_matches_components():
    facade = (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=_fixture(),
        )
    )

    expected = sum(
        len(component["triangles"])
        for component in facade[
            "component_meshes"
        ]
    )

    assert len(
        facade["triangles"]
    ) == expected


def test_stage_facade_derives_grid_from_dimensions():
    stage_mesh = {
        "stage_front_wall_quad": (
            (0.0, 0.0, 0.0),
            (12.0, 0.0, 0.0),
            (12.0, 0.0, 4.8),
            (0.0, 0.0, 4.8),
        ),
    }

    facade = (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=stage_mesh,
            target_column_spacing_mm=2.0,
            target_row_height_mm=2.0,
        )
    )

    assert facade["column_count"] == 6
    assert facade["row_count"] == 2


def test_stage_facade_respects_grid_limits():
    stage_mesh = {
        "stage_front_wall_quad": (
            (0.0, 0.0, 0.0),
            (100.0, 0.0, 0.0),
            (100.0, 0.0, 50.0),
            (0.0, 0.0, 50.0),
        ),
    }

    facade = (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=stage_mesh,
            max_columns=8,
            max_rows=2,
        )
    )

    assert facade["column_count"] == 8
    assert facade["row_count"] == 2


def test_stage_facade_accepts_custom_geometry():
    facade = (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=_fixture(),
            depth_mm=0.35,
            embed_mm=0.10,
            arch_segments=8,
        )
    )

    assert facade["depth_mm"] == 0.35
    assert facade["embed_mm"] == 0.10
    assert facade["arch_segments"] == 8


def test_stage_facade_rejects_missing_stage():
    assert (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh=None,
        )
        is None
    )


def test_stage_facade_rejects_missing_front_wall():
    assert (
        AtlasAncientTheatreStageFacadeBuilder
        .build(
            stage_mesh={
                "triangles": [],
            },
        )
        is None
    )


@pytest.mark.parametrize(
    "spacing,row_height",
    [
        (0.0, 2.0),
        (-1.0, 2.0),
        (2.0, 0.0),
        (2.0, -1.0),
    ],
)
def test_stage_facade_rejects_invalid_targets(
    spacing,
    row_height,
):
    with pytest.raises(ValueError):
        (
            AtlasAncientTheatreStageFacadeBuilder
            .build(
                stage_mesh=_fixture(),
                target_column_spacing_mm=(
                    spacing
                ),
                target_row_height_mm=(
                    row_height
                ),
            )
        )
