import pytest

from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_mesh_builder import (
    AtlasLandmarkMeshBuilder,
)
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_mesh_validator import AtlasMeshValidator


def _footprint():
    return (
        (0.0, 0.0),
        (12.0, 0.0),
        (12.0, 20.0),
        (0.0, 20.0),
    )


def test_mosque_uses_safe_footprint_fallback_mesh():
    landmark = AtlasLandmark(
        id=801,
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=_footprint(),
        tags={
            "building": "mosque",
            "amenity": "place_of_worship",
            "religion": "muslim",
        },
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=None,
    )

    assert mesh["type"] == "worship_landmark_fallback"
    assert mesh["worship_profile"] == "mosque"
    assert mesh["uses_real_footprint"] is True
    assert mesh["special_architecture_applied"] is False
    assert mesh["height_m"] == 18.0
    assert len(mesh["triangles"]) > 0

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True


def test_synagogue_uses_safe_footprint_fallback_mesh():
    landmark = AtlasLandmark(
        id=802,
        landmark_type=AtlasLandmarkType.SYNAGOGUE,
        geometry=_footprint(),
        tags={
            "building": "synagogue",
            "amenity": "place_of_worship",
            "religion": "jewish",
            "height": "21 m",
        },
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=None,
    )

    assert mesh["type"] == "worship_landmark_fallback"
    assert mesh["worship_profile"] == "synagogue"
    assert mesh["uses_real_footprint"] is True
    assert mesh["special_architecture_applied"] is False
    assert mesh["height_m"] == 21.0
    assert len(mesh["triangles"]) > 0

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True


class FakeTerrain:
    def sample_height(self, x, y):
        return 2.5


def test_mosque_fallback_can_be_embedded_into_terrain():
    landmark = AtlasLandmark(
        id=803,
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=_footprint(),
        tags={
            "building": "mosque",
            "amenity": "place_of_worship",
            "religion": "muslim",
        },
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=FakeTerrain(),
    )

    assert mesh["foundation_z"] == 2.5

    assert {
        round(point[2], 8)
        for point in mesh["bottom"]
    } == {2.5}

    assert min(
        point[2]
        for triangle in mesh["triangles"]
        for point in triangle
    ) == 2.5


def test_mosque_fallback_reports_resolved_worship_grammar():
    landmark = AtlasLandmark(
        id=804,
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=_footprint(),
        tags={
            "building": "mosque",
            "amenity": "place_of_worship",
            "religion": "muslim",
        },
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=None,
    )

    assert mesh["worship_grammar"] == "footprint_fallback"


def test_synagogue_fallback_reports_resolved_worship_grammar():
    landmark = AtlasLandmark(
        id=805,
        landmark_type=AtlasLandmarkType.SYNAGOGUE,
        geometry=_footprint(),
        tags={
            "building": "synagogue",
            "amenity": "place_of_worship",
            "religion": "jewish",
        },
        source="OSM",
    )

    mesh = AtlasLandmarkMeshBuilder.build(
        landmark,
        terrain_mesh=None,
    )

    assert mesh["worship_grammar"] == "footprint_fallback"


def test_fallback_mesher_rejects_unimplemented_special_mosque_grammar():
    landmark = AtlasLandmark(
        id=806,
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=_footprint(),
        tags={
            "building": "mosque",
            "religion": "muslim",
            "atlas:worship_grammar": (
                "single_dome_single_minaret"
            ),
        },
        source="OSM",
    )

    with pytest.raises(
        ValueError,
        match="not implemented",
    ):
        AtlasLandmarkMeshBuilder.build(
            landmark,
            terrain_mesh=None,
        )


def test_fallback_mesher_rejects_unimplemented_special_synagogue_grammar():
    landmark = AtlasLandmark(
        id=807,
        landmark_type=AtlasLandmarkType.SYNAGOGUE,
        geometry=_footprint(),
        tags={
            "building": "synagogue",
            "religion": "jewish",
            "atlas:worship_grammar": (
                "twin_tower_facade"
            ),
        },
        source="OSM",
    )

    with pytest.raises(
        ValueError,
        match="not implemented",
    ):
        AtlasLandmarkMeshBuilder.build(
            landmark,
            terrain_mesh=None,
        )
