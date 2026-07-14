from CORE.atlas_ancient_theatre_geometry_profiler import (
    AtlasAncientTheatreGeometryProfiler,
)
from CORE.atlas_local_osm_reader import (
    AtlasLocalOSMReader,
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


def _aspendos():
    data = AtlasLocalOSMReader.read(
        PBF_PATH,
        BBOX,
    )

    return next(
        building
        for building in data["buildings"]
        if (
            building.get("tags", {}).get(
                "historic"
            )
            == "theatre"
        )
    )


def test_aspendos_geometry_profile_is_valid():
    profile = (
        AtlasAncientTheatreGeometryProfiler
        .profile(_aspendos())
    )

    assert profile["valid"] is True
    assert profile["reason"] is None


def test_aspendos_stage_front_is_detected():
    profile = (
        AtlasAncientTheatreGeometryProfiler
        .profile(_aspendos())
    )

    assert profile["stage_edge_indices"] == (
        37,
        39,
        41,
    )

    assert 97.0 < profile[
        "stage_front_length_m"
    ] < 98.5


def test_aspendos_dimensions_are_stable():
    profile = (
        AtlasAncientTheatreGeometryProfiler
        .profile(_aspendos())
    )

    assert 97.0 < profile["width_m"] < 99.0
    assert 69.0 < profile[
        "usable_depth_m"
    ] < 71.0


def test_component_depths_are_scale_relative():
    profile = (
        AtlasAncientTheatreGeometryProfiler
        .profile(_aspendos())
    )

    assert 0.0 < profile[
        "stage_depth_m"
    ] < profile["usable_depth_m"]

    assert 0.0 < profile[
        "orchestra_depth_m"
    ] < profile["usable_depth_m"]

    assert 0.0 < profile[
        "cavea_inner_depth_m"
    ] < profile["usable_depth_m"]


def test_invalid_geometry_is_rejected():
    profile = (
        AtlasAncientTheatreGeometryProfiler
        .profile(
            {
                "geometry": [
                    (36.0, 31.0),
                    (36.1, 31.1),
                ]
            }
        )
    )

    assert profile["valid"] is False
    assert profile[
        "reason"
    ] == "insufficient_geometry"
