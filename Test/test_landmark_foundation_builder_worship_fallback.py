from CORE.atlas_landmark_foundation_builder import (
    AtlasLandmarkFoundationBuilder,
)


class FakeCoordinateEngine:
    xy_scale = 3000.0

    def geometry_to_stl_mm(self, geometry):
        return [
            (
                float(lon) * 100_000.0,
                float(lat) * 100_000.0,
            )
            for lat, lon in geometry
        ]

    def latlon_to_local_meters(self, lat, lon):
        return (
            float(lon) * 100_000.0,
            float(lat) * 100_000.0,
        )

    def height_to_stl_mm(self, height_m):
        return (
            float(height_m)
            * 1000.0
            / self.xy_scale
        )


def _flat_terrain():
    return {
        "type": "terrain_closed_slab",
        "top_points": (
            (
                (0.0, 0.0, 1.0),
                (30.0, 0.0, 1.0),
            ),
            (
                (0.0, 30.0, 1.0),
                (30.0, 30.0, 1.0),
            ),
        ),
        "metadata": {
            "size_x_mm": 30.0,
            "size_y_mm": 30.0,
        },
    }


def _source(
    *,
    source_id,
    building,
    religion,
):
    return {
        "id": source_id,
        "geometry_type": "way",
        "geometry": (
            (0.0, 0.0),
            (0.0, 0.0001),
            (0.0001, 0.0001),
            (0.0001, 0.0),
        ),
        "tags": {
            "building": building,
            "amenity": "place_of_worship",
            "religion": religion,
        },
    }


def test_foundation_builder_places_mosque_fallback_on_terrain():
    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[
            _source(
                source_id=901,
                building="mosque",
                religion="muslim",
            )
        ],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "worship_landmark_fallback"
    assert mesh["worship_profile"] == "mosque"
    assert mesh["special_architecture_applied"] is False
    assert mesh["landmark_id"] == 901


def test_foundation_builder_places_synagogue_fallback_on_terrain():
    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[
            _source(
                source_id=902,
                building="synagogue",
                religion="jewish",
            )
        ],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "worship_landmark_fallback"
    assert mesh["worship_profile"] == "synagogue"
    assert mesh["special_architecture_applied"] is False
    assert mesh["landmark_id"] == 902


def test_foundation_builder_builds_worship_fallback_in_single_pass(
    monkeypatch,
):
    calls = []

    from CORE.atlas_worship_landmark_fallback_mesher import (
        AtlasWorshipLandmarkFallbackMesher,
    )

    original_build = AtlasWorshipLandmarkFallbackMesher.build

    def counting_build(landmark):
        calls.append(
            {
                "id": landmark.id,
                "geometry": tuple(landmark.geometry),
                "tags": dict(landmark.tags),
            }
        )
        return original_build(landmark)

    monkeypatch.setattr(
        AtlasWorshipLandmarkFallbackMesher,
        "build",
        counting_build,
    )

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[
            {
                **_source(
                    source_id=903,
                    building="mosque",
                    religion="muslim",
                ),
                "tags": {
                    "building": "mosque",
                    "amenity": "place_of_worship",
                    "religion": "muslim",
                    "height": "18",
                },
            }
        ],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        debug=False,
    )

    assert len(meshes) == 1
    assert len(calls) == 1

    mesh = meshes[0]

    assert mesh["height_m"] == 18.0
    assert mesh["height_mm"] == 6.0
    assert mesh["foundation_z"] == 0.7
    assert mesh["max_z"] == 6.0
    assert mesh["top_z"] == 6.0
    assert {
        round(point[2], 8)
        for triangle in mesh["triangles"]
        for point in triangle
    } == {
        0.7,
        6.7,
    }
