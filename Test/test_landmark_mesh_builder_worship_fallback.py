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
