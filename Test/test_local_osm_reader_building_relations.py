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
