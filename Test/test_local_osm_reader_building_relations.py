from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def _outer_geometry():
    return [
        (41.0000, 28.0000),
        (41.0000, 28.0010),
        (41.0010, 28.0010),
        (41.0010, 28.0000),
    ]


def _inner_geometry():
    return [
        (41.0003, 28.0003),
        (41.0003, 28.0007),
        (41.0007, 28.0007),
        (41.0007, 28.0003),
    ]


def test_building_multipolygon_relation_is_recognized():
    tags = {
        "type": "multipolygon",
        "building": "mosque",
        "name": "Example Mosque",
    }

    assert AtlasLocalOSMReader._is_building_relation(tags)


def test_building_part_multipolygon_relation_is_recognized():
    tags = {
        "type": "multipolygon",
        "building:part": "yes",
        "height": "20",
    }

    assert AtlasLocalOSMReader._is_building_relation(tags)


def test_non_building_multipolygon_relation_is_rejected():
    tags = {
        "type": "multipolygon",
        "natural": "water",
    }

    assert not AtlasLocalOSMReader._is_building_relation(tags)


def test_non_multipolygon_building_relation_is_rejected():
    tags = {
        "type": "route",
        "building": "yes",
    }

    assert not AtlasLocalOSMReader._is_building_relation(tags)


def test_building_relation_record_preserves_outer_and_inner_geometry():
    tags = {
        "type": "multipolygon",
        "building": "mosque",
        "name": "Example Mosque",
    }

    record = AtlasLocalOSMReader._create_building_relation_record(
        relation_id=18055570,
        tags=tags,
        outer_geometries=[
            _outer_geometry(),
        ],
        inner_geometries=[
            _inner_geometry(),
        ],
    )

    assert record is not None
    assert record["id"] == 18055570
    assert record["geometry_type"] == "relation"
    assert record["geometry"] == _outer_geometry()
    assert record["outer_geometries"] == [
        _outer_geometry(),
    ]
    assert record["inner_geometries"] == [
        _inner_geometry(),
    ]
    assert record["tags"]["building"] == "mosque"
    assert record["tags"]["name"] == "Example Mosque"


def test_building_relation_without_valid_outer_geometry_is_rejected():
    record = AtlasLocalOSMReader._create_building_relation_record(
        relation_id=18055570,
        tags={
            "type": "multipolygon",
            "building": "mosque",
        },
        outer_geometries=[],
        inner_geometries=[
            _inner_geometry(),
        ],
    )

    assert record is None


def test_real_sultanahmet_building_relation_is_read():
    data = AtlasLocalOSMReader.read(
        "Data/OSM/hagia-sophia-sultanahmet-test.osm.pbf",
        (
            41.0025,
            28.9715,
            41.0095,
            28.9845,
        ),
    )

    matches = [
        record
        for record in data["buildings"]
        if record.get("id") == 18055570
    ]

    assert len(matches) == 1

    record = matches[0]

    assert record["geometry_type"] == "relation"
    assert record["tags"]["type"] == "multipolygon"
    assert record["tags"]["building"] == "mosque"
    assert record["tags"]["name"] == "Sultanahmet Camii"
    assert len(record["outer_geometries"]) == 1
    assert len(record["inner_geometries"]) == 1
    assert len(record["geometry"]) >= 3


def test_real_ayasofya_sultanahmet_hierarchy_is_complete():
    from CORE.atlas_building_part_hierarchy_profiler import (
        AtlasBuildingPartHierarchyProfiler,
    )

    data = AtlasLocalOSMReader.read(
        "Data/OSM/hagia-sophia-sultanahmet-test.osm.pbf",
        (
            41.0025,
            28.9715,
            41.0095,
            28.9845,
        ),
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        data["buildings"]
    )

    ayasofya_id = 109862851
    sultanahmet_id = 18055570

    assert len(result["parents"][ayasofya_id]["parts"]) == 48
    assert len(result["parents"][sultanahmet_id]["parts"]) == 88

    assert result["summary"]["assigned_building_part_count"] == 144
    assert result["summary"]["unassigned_building_part_count"] == 0
    assert result["unassigned_part_ids"] == []

    sultanahmet_minarets = [
        part
        for part in result["parents"][sultanahmet_id]["parts"]
        if part.get("tags", {}).get("tower:type") == "minaret"
    ]

    ayasofya_minarets = [
        part
        for part in result["parents"][ayasofya_id]["parts"]
        if part.get("tags", {}).get("tower:type") == "minaret"
    ]

    assert len(sultanahmet_minarets) == 6
    assert len(ayasofya_minarets) == 4

    assert result["part_to_parent"][776020486] == ayasofya_id

    assert ayasofya_id not in result["suppressed_parent_ids"]
    assert sultanahmet_id not in result["suppressed_parent_ids"]

    assert result["suppressed_parent_ids"] == [
        1318101891,
    ]

    assert result["residual_replacement_parent_ids"] == [
        sultanahmet_id,
        ayasofya_id,
    ]

    residual_counts = {
        parent_id: sum(
            1
            for record in result["residual_parent_records"]
            if record.get("source_parent_id") == parent_id
        )
        for parent_id in (
            ayasofya_id,
            sultanahmet_id,
        )
    }

    assert residual_counts[sultanahmet_id] == 4
    assert residual_counts[ayasofya_id] == 89

    assert (
        result["parent_metrics"][sultanahmet_id]
        ["should_create_residual"]
        is True
    )
    assert (
        result["parent_metrics"][ayasofya_id]
        ["should_create_residual"]
        is True
    )


def test_building_relation_geometries_are_clipped_to_bbox():
    outer_geometries = [
        [
            (41.0000, 28.0000),
            (41.0000, 28.0030),
            (41.0030, 28.0030),
            (41.0030, 28.0000),
        ],
    ]
    inner_geometries = [
        [
            (41.0020, 28.0020),
            (41.0020, 28.0025),
            (41.0025, 28.0025),
            (41.0025, 28.0020),
        ],
    ]

    clipped_outer, clipped_inner = (
        AtlasLocalOSMReader
        ._clip_relation_geometries_to_bbox(
            outer_geometries=outer_geometries,
            inner_geometries=inner_geometries,
            bbox=(
                41.0005,
                28.0005,
                41.0015,
                28.0015,
            ),
        )
    )

    assert len(clipped_outer) == 1
    assert clipped_inner == []

    points = clipped_outer[0]

    assert len(points) >= 4
    assert all(
        41.0005 <= lat <= 41.0015
        and 28.0005 <= lon <= 28.0015
        for lat, lon in points
    )

    assert min(lat for lat, _ in points) == 41.0005
    assert max(lat for lat, _ in points) == 41.0015
    assert min(lon for _, lon in points) == 28.0005
    assert max(lon for _, lon in points) == 28.0015



def test_building_relation_open_outer_segments_are_assembled():
    first_outer_segment = [
        (52.4450, 13.5740),
        (52.4450, 13.5750),
        (52.4460, 13.5750),
    ]
    second_outer_segment = [
        (52.4460, 13.5750),
        (52.4460, 13.5740),
        (52.4450, 13.5740),
    ]

    assembled = (
        AtlasLocalOSMReader
        ._assemble_relation_ring_geometries(
            geometries=[
                first_outer_segment,
                second_outer_segment,
            ]
        )
    )

    assert len(assembled) == 1
    assert len(assembled[0]) == 4
    assert set(assembled[0]) == {
        (52.4450, 13.5740),
        (52.4450, 13.5750),
        (52.4460, 13.5750),
        (52.4460, 13.5740),
    }


def test_building_relation_record_uses_assembled_outer_geometry():
    first_outer_segment = [
        (52.4450, 13.5740),
        (52.4450, 13.5750),
        (52.4460, 13.5750),
    ]
    second_outer_segment = [
        (52.4460, 13.5750),
        (52.4460, 13.5740),
        (52.4450, 13.5740),
    ]

    record = AtlasLocalOSMReader._create_building_relation_record(
        relation_id=57493,
        tags={
            "type": "multipolygon",
            "building": "yes",
            "name": "Rathaus Köpenick",
        },
        outer_geometries=[
            first_outer_segment,
            second_outer_segment,
        ],
        inner_geometries=[],
    )

    assert record is not None
    assert len(record["outer_geometries"]) == 1
    assert record["geometry"] == record["outer_geometries"][0]
    assert set(record["geometry"]) == {
        (52.4450, 13.5740),
        (52.4450, 13.5750),
        (52.4460, 13.5750),
        (52.4460, 13.5740),
    }


def test_scene_builder_preserves_building_relation_inner_geometries():
    from CORE.atlas_scene_builder import AtlasSceneBuilder

    inner_geometry = [
        (52.4453, 13.5743),
        (52.4453, 13.5747),
        (52.4457, 13.5747),
        (52.4457, 13.5743),
    ]

    atlas_building = AtlasSceneBuilder._to_atlas_building(
        {
            "id": 57493,
            "geometry": _outer_geometry(),
            "outer_geometries": [
                _outer_geometry(),
            ],
            "inner_geometries": [
                inner_geometry,
            ],
            "geometry_type": "relation",
            "tags": {
                "type": "multipolygon",
                "building": "yes",
                "name": "Rathaus Köpenick",
            },
        }
    )

    assert atlas_building.geometry_type == "relation"
    assert atlas_building.outer_geometries == [
        _outer_geometry(),
    ]
    assert atlas_building.inner_geometries == [
        inner_geometry,
    ]
