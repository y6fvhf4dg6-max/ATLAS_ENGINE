from CORE.atlas_landmark_foundation_builder import (
    AtlasLandmarkFoundationBuilder,
)


class FixtureCoordinateEngine:
    xy_scale = 5500.0

    @staticmethod
    def latlon_to_local_meters(lat, lon):
        return (
            float(lon) * 1000.0,
            float(lat) * 1000.0,
        )

    @staticmethod
    def geometry_to_stl_mm(geometry):
        return tuple(
            (
                float(lon) * 1000.0 / 5500.0,
                float(lat) * 1000.0 / 5500.0,
            )
            for lat, lon in geometry
        )

    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m) * 1000.0 / 5500.0


class FixtureTerrain:
    @staticmethod
    def sample_height(x, y):
        return 1.25


def test_foundation_builder_accepts_church_landmark():
    source = {
        "id": 801,
        "geometry": (
            (50.0000, 7.0000),
            (50.0000, 7.0010),
            (50.0010, 7.0010),
            (50.0010, 7.0000),
        ),
        "geometry_type": "way",
        "tags": {
            "building": "church",
            "religion": "christian",
            "height": "30",
            "name": "Fixture Church",
        },
    }

    mesh = (
        AtlasLandmarkFoundationBuilder
        ._build_landmark_mesh(
            source=source,
            coordinate_engine=FixtureCoordinateEngine(),
            terrain_mesh=FixtureTerrain(),
        )
    )

    assert mesh is not None
    assert mesh["type"] == "church_landmark"
    assert mesh["landmark_class"] == "church"
    assert mesh["foundation_z"] == 1.25
    assert len(mesh["triangles"]) > 0


def test_foundation_builder_accepts_cathedral_landmark():
    source = {
        "id": 802,
        "geometry": (
            (50.0000, 7.0000),
            (50.0000, 7.0020),
            (50.0020, 7.0020),
            (50.0020, 7.0000),
        ),
        "geometry_type": "way",
        "tags": {
            "building": "cathedral",
            "religion": "christian",
            "name": "Fixture Cathedral",
        },
    }

    mesh = (
        AtlasLandmarkFoundationBuilder
        ._build_landmark_mesh(
            source=source,
            coordinate_engine=FixtureCoordinateEngine(),
            terrain_mesh=FixtureTerrain(),
        )
    )

    assert mesh is not None
    assert mesh["landmark_class"] == "cathedral"
    assert len(mesh["tower_meshes"]) == 2
    assert mesh["spire_meshes"] == []


def _hierarchy_context(
    *,
    parent_id,
    tower_count,
):
    parts = [
        {
            "id": 9000 + index,
            "tags": {
                "building:part": "yes",
                "tower:type": "bell_tower",
            },
        }
        for index in range(tower_count)
    ]

    return {
        "parents": {
            parent_id: {
                "parts": parts,
                "part_ids": [
                    part["id"]
                    for part in parts
                ],
            },
        },
    }


def test_foundation_builder_uses_hierarchy_single_bell_tower_profile():
    source = {
        "id": 803,
        "geometry": (
            (50.0000, 7.0000),
            (50.0000, 7.0020),
            (50.0020, 7.0020),
            (50.0020, 7.0000),
        ),
        "geometry_type": "way",
        "tags": {
            "building": "cathedral",
            "religion": "christian",
            "name": "Single Tower Cathedral",
        },
    }

    mesh = (
        AtlasLandmarkFoundationBuilder
        ._build_landmark_mesh(
            source=source,
            coordinate_engine=FixtureCoordinateEngine(),
            terrain_mesh=FixtureTerrain(),
            hierarchy_context=_hierarchy_context(
                parent_id=803,
                tower_count=1,
            ),
        )
    )

    assert mesh is not None
    assert mesh["type"] == "church_landmark"
    assert mesh["grammar_name"] == "single_west_tower"
    assert len(mesh["tower_meshes"]) == 1


def test_foundation_builder_uses_hierarchy_twin_bell_tower_profile():
    source = {
        "id": 804,
        "geometry": (
            (50.0000, 7.0000),
            (50.0000, 7.0010),
            (50.0010, 7.0010),
            (50.0010, 7.0000),
        ),
        "geometry_type": "way",
        "tags": {
            "building": "church",
            "religion": "christian",
            "name": "Twin Tower Church",
        },
    }

    mesh = (
        AtlasLandmarkFoundationBuilder
        ._build_landmark_mesh(
            source=source,
            coordinate_engine=FixtureCoordinateEngine(),
            terrain_mesh=FixtureTerrain(),
            hierarchy_context=_hierarchy_context(
                parent_id=804,
                tower_count=2,
            ),
        )
    )

    assert mesh is not None
    assert mesh["type"] == "church_landmark"
    assert mesh["grammar_name"] == "twin_west_towers"
    assert len(mesh["tower_meshes"]) == 2
