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


def test_foundation_builder_routes_premium_mosque_grammar():
    source = {
        **_source(
            source_id=904,
            building="mosque",
            religion="muslim",
        ),
        "tags": {
            "building": "mosque",
            "amenity": "place_of_worship",
            "religion": "muslim",
            "height": "27",
            "atlas:worship_grammar": (
                "single_dome_single_minaret"
            ),
        },
    }

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "mosque_landmark"
    assert mesh["worship_grammar"] == (
        "single_dome_single_minaret"
    )
    assert mesh["special_architecture_applied"] is True
    assert mesh["height_m"] == 27.0
    assert mesh["height_mm"] == 9.0
    assert mesh["foundation_z"] == 0.7
    assert len(mesh["dome_meshes"]) == 1
    assert len(mesh["minaret_meshes"]) == 1

    triangle_z_values = {
        round(point[2], 8)
        for triangle in mesh["triangles"]
        for point in triangle
    }

    assert min(triangle_z_values) == 0.7
    assert max(triangle_z_values) == 9.7


def test_foundation_builder_routes_catalog_worship_grammar_before_mesh(
    monkeypatch,
):
    from CORE.atlas_master_landmark_catalog import (
        AtlasMasterLandmarkCatalog,
        AtlasMasterLandmarkCatalogEntry,
    )

    catalog_entry = AtlasMasterLandmarkCatalogEntry(
        key="catalog-mosque",
        landmark_family="mosque",
        osm_ids=(905,),
        grammar_name="single_dome_single_minaret",
    )

    monkeypatch.setattr(
        AtlasMasterLandmarkCatalog,
        "resolve",
        classmethod(
            lambda cls, **kwargs: catalog_entry
        ),
    )

    source = {
        **_source(
            source_id=905,
            building="mosque",
            religion="muslim",
        ),
        "tags": {
            "building": "mosque",
            "amenity": "place_of_worship",
            "religion": "muslim",
            "height": "27",
        },
    }

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "mosque_landmark"
    assert mesh["worship_grammar"] == (
        "single_dome_single_minaret"
    )
    assert mesh["special_architecture_applied"] is True
    assert len(mesh["dome_meshes"]) == 1
    assert len(mesh["minaret_meshes"]) == 1
    assert len(mesh["minaret_balcony_meshes"]) == 1
    assert len(mesh["minaret_cap_meshes"]) == 1


def test_real_ankara_pbf_mosque_routes_catalog_grammar_end_to_end(
    monkeypatch,
):
    from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
    from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
    from CORE.atlas_master_landmark_catalog import (
        AtlasMasterLandmarkCatalog,
        AtlasMasterLandmarkCatalogEntry,
    )

    bbox = (
        39.9351328,
        32.8582838,
        39.9521044,
        32.8780862,
    )

    data = AtlasLocalOSMReader.read(
        "Data/OSM/ankara-kalesi-test.osm.pbf",
        bbox,
    )

    source = next(
        record
        for record in data["landmarks"]
        if record.get("id") == 363091623
    )

    assert source["tags"]["name"] == (
        "Sığınaklar Mahallesi Cami"
    )
    assert source["tags"]["building"] == "mosque"
    assert source["tags"]["religion"] == "muslim"
    assert len(source["geometry"]) >= 3
    assert "atlas:worship_grammar" not in source["tags"]

    catalog_entry = AtlasMasterLandmarkCatalogEntry(
        key="real-ankara-pbf-mosque-test",
        landmark_family="mosque",
        osm_ids=(363091623,),
        grammar_name="single_dome_single_minaret",
    )

    original_resolve = AtlasMasterLandmarkCatalog.resolve

    def resolve_catalog(cls, **kwargs):
        if kwargs.get("osm_id") == 363091623:
            return catalog_entry

        return original_resolve(**kwargs)

    monkeypatch.setattr(
        AtlasMasterLandmarkCatalog,
        "resolve",
        classmethod(resolve_catalog),
    )

    class FixtureTerrain:
        @staticmethod
        def sample_height(x, y):
            return 1.25

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=bbox[0],
        origin_lon=bbox[1],
        xy_scale=5500.0,
        z_scale=5500.0,
    )

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=coordinate_engine,
        terrain_mesh=FixtureTerrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["landmark_id"] == 363091623
    assert mesh["type"] == "mosque_landmark"
    assert mesh["worship_grammar"] == (
        "single_dome_single_minaret"
    )
    assert mesh["special_architecture_applied"] is True
    assert mesh["foundation_z"] == 1.25

    assert len(mesh["dome_meshes"]) == 1
    assert len(mesh["minaret_meshes"]) == 1
    assert len(mesh["minaret_balcony_meshes"]) == 1
    assert len(mesh["minaret_cap_meshes"]) == 1

    assert len(mesh["footprint"]) == len(
        source["geometry"]
    )
    assert len(mesh["triangles"]) > 0


def test_production_catalog_promotes_real_cenabi_ahmet_pasha_to_mosque():
    from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
    from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
    from CORE.atlas_master_landmark_catalog import (
        AtlasMasterLandmarkCatalog,
    )

    bbox = (
        39.9351328,
        32.8582838,
        39.9521044,
        32.8780862,
    )

    data = AtlasLocalOSMReader.read(
        "Data/OSM/ankara-kalesi-test.osm.pbf",
        bbox,
    )

    source = next(
        record
        for record in data["buildings"]
        if record.get("id") == 322722702
    )

    assert source["tags"]["name"] == (
        "Cenabi Ahmet Paşa Cami"
    )
    assert source["tags"]["wikidata"] == "Q96278624"
    assert source["tags"]["building"] == "church"
    assert source["tags"]["religion"] == "muslim"
    assert source["tags"]["amenity"] == (
        "place_of_worship"
    )

    catalog_entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id=source["tags"]["wikidata"],
        osm_id=source["id"],
    )

    assert catalog_entry is not None
    assert catalog_entry.key == (
        "cenabi-ahmet-pasha-mosque"
    )
    assert catalog_entry.landmark_family == "mosque"
    assert catalog_entry.grammar_name == (
        "single_dome_single_minaret"
    )

    class FixtureTerrain:
        @staticmethod
        def sample_height(x, y):
            return 1.25

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=bbox[0],
        origin_lon=bbox[1],
        xy_scale=5500.0,
        z_scale=5500.0,
    )

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=coordinate_engine,
        terrain_mesh=FixtureTerrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["landmark_id"] == 322722702
    assert mesh["type"] == "mosque_landmark"
    assert mesh["worship_grammar"] == (
        "single_dome_single_minaret"
    )
    assert mesh["special_architecture_applied"] is True
    assert mesh["foundation_z"] == 1.25
    assert len(mesh["dome_meshes"]) == 1
    assert len(mesh["minaret_meshes"]) == 1
    assert len(mesh["minaret_balcony_meshes"]) == 1
    assert len(mesh["minaret_cap_meshes"]) == 1

def test_foundation_builder_routes_from_validation_engine_result(
    monkeypatch,
):
    from CORE.atlas_landmark_validation_engine import (
        AtlasLandmarkValidationEngine,
        AtlasLandmarkValidationResult,
    )

    source = _source(
        source_id=9901,
        building="church",
        religion="christian",
    )

    def validate_as_mosque(cls, candidate):
        assert candidate is source

        return AtlasLandmarkValidationResult(
            family="mosque",
            confidence="high",
            action="fallback",
            evidence=("integration_test",),
        )

    monkeypatch.setattr(
        AtlasLandmarkValidationEngine,
        "validate",
        classmethod(validate_as_mosque),
    )

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        debug=False,
    )

    assert len(meshes) == 1
    assert meshes[0]["type"] == (
        "worship_landmark_fallback"
    )
    assert meshes[0]["worship_profile"] == "mosque"

def test_landmark_builder_forwards_hierarchy_context(
    monkeypatch,
):
    hierarchy_context = {
        "parents": {
            9902: {
                "parent": {"id": 9902},
                "parts": [],
                "part_ids": [],
            },
        },
    }

    captured = []

    def fake_build(
        cls,
        source,
        coordinate_engine,
        terrain_mesh,
        road_meshes=(),
        hierarchy_context=None,
    ):
        captured.append(
            {
                "source": source,
                "hierarchy_context": hierarchy_context,
            }
        )

        return {
            "type": "fixture",
            "triangles": (),
        }

    monkeypatch.setattr(
        AtlasLandmarkFoundationBuilder,
        "_build_landmark_mesh",
        classmethod(fake_build),
    )

    source = _source(
        source_id=9902,
        building="mosque",
        religion="muslim",
    )

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        hierarchy_context=hierarchy_context,
        debug=False,
    )

    assert len(meshes) == 1
    assert captured == [
        {
            "source": source,
            "hierarchy_context": hierarchy_context,
        },
    ]

def test_foundation_builder_uses_hierarchy_inferred_single_minaret_grammar():
    source = _source(
        source_id=6100,
        building="mosque",
        religion="muslim",
    )

    hierarchy_context = {
        "parents": {
            6100: {
                "parent": source,
                "parts": [
                    {
                        "id": 6101,
                        "geometry": [
                            (41.00001, 29.00001),
                            (41.00001, 29.00002),
                            (41.00002, 29.00002),
                            (41.00002, 29.00001),
                        ],
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                            "height": "28",
                        },
                    },
                ],
                "part_ids": [6101],
            },
        },
    }

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        hierarchy_context=hierarchy_context,
        debug=False,
    )

    assert len(meshes) == 1
    assert meshes[0]["type"] == "mosque_landmark"
    assert (
        meshes[0]["grammar_name"]
        == "single_dome_single_minaret"
    )


def test_foundation_builder_keeps_multi_minaret_without_dome_evidence_as_safe_fallback():
    source = _source(
        source_id=6200,
        building="mosque",
        religion="muslim",
    )

    hierarchy_context = {
        "parents": {
            6200: {
                "parent": source,
                "parts": [
                    {
                        "id": 6201,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 6202,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                ],
                "part_ids": [6201, 6202],
            },
        },
    }

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        hierarchy_context=hierarchy_context,
        debug=False,
    )

    assert len(meshes) == 1
    assert (
        meshes[0]["type"]
        == "worship_landmark_fallback"
    )
    assert (
        meshes[0]["grammar_name"]
        == "footprint_fallback"
    )

def test_foundation_builder_builds_multi_mosque_from_component_evidence():
    source = _source(
        source_id=6300,
        building="mosque",
        religion="muslim",
    )

    hierarchy_context = {
        "parents": {
            6300: {
                "parent": source,
                "parts": [
                    {
                        "id": 6301,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 6302,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 6311,
                        "tags": {
                            "building:part": "yes",
                            "roof:shape": "dome",
                        },
                    },
                    {
                        "id": 6312,
                        "tags": {
                            "building:part": "yes",
                            "roof:shape": "dome",
                        },
                    },
                    {
                        "id": 6313,
                        "tags": {
                            "building:part": "yes",
                            "roof:shape": "dome",
                        },
                    },
                ],
                "part_ids": [
                    6301,
                    6302,
                    6311,
                    6312,
                    6313,
                ],
            },
        },
    }

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        hierarchy_context=hierarchy_context,
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "mosque_landmark"
    assert mesh["grammar_name"] == (
        "multi_dome_multi_minaret"
    )
    assert len(mesh["dome_meshes"]) == 3
    assert len(mesh["dome_drum_meshes"]) == 3
    assert len(mesh["minaret_meshes"]) == 2
    assert len(
        mesh["minaret_balcony_meshes"]
    ) == 2
    assert len(mesh["minaret_cap_meshes"]) == 2


def test_foundation_builder_caps_multi_component_counts_at_profile_limit():
    source = _source(
        source_id=6400,
        building="mosque",
        religion="muslim",
    )

    parts = []

    for index in range(10):
        parts.append(
            {
                "id": 6410 + index,
                "tags": {
                    "building:part": "yes",
                    "tower:type": "minaret",
                },
            }
        )

        parts.append(
            {
                "id": 6510 + index,
                "tags": {
                    "building:part": "yes",
                    "roof:shape": "dome",
                },
            }
        )

    hierarchy_context = {
        "parents": {
            6400: {
                "parent": source,
                "parts": parts,
                "part_ids": [
                    part["id"]
                    for part in parts
                ],
            },
        },
    }

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_flat_terrain(),
        hierarchy_context=hierarchy_context,
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "mosque_landmark"
    assert mesh["grammar_name"] == (
        "multi_dome_multi_minaret"
    )
    assert len(mesh["dome_meshes"]) == 8
    assert len(mesh["minaret_meshes"]) == 8
