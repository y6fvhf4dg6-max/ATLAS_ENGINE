from CORE.atlas_building_part_hierarchy_profiler import (
    AtlasBuildingPartHierarchyProfiler,
)


def _record(
    source_id,
    geometry,
    tags,
):
    return {
        "id": source_id,
        "geometry": geometry,
        "tags": tags,
    }


def test_assigns_contained_building_parts_to_parent():
    parent = _record(
        100,
        [
            (39.0, 32.0),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.0),
        ],
        {
            "building": "yes",
        },
    )

    part = _record(
        200,
        [
            (39.02, 32.02),
            (39.02, 32.04),
            (39.04, 32.04),
            (39.04, 32.02),
        ],
        {
            "building:part": "yes",
            "height": "22",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            part,
        ]
    )

    assert result["part_to_parent"] == {
        200: 100,
    }
    assert result["parents"][100]["part_ids"] == [
        200,
    ]
    assert result["summary"]["parent_with_parts_count"] == 1
    assert result["summary"]["assigned_building_part_count"] == 1
    assert result["summary"]["unassigned_building_part_count"] == 0


def test_uses_smallest_containing_parent():
    outer_parent = _record(
        100,
        [
            (39.0, 32.0),
            (39.0, 32.2),
            (39.2, 32.2),
            (39.2, 32.0),
        ],
        {
            "building": "yes",
        },
    )

    inner_parent = _record(
        101,
        [
            (39.02, 32.02),
            (39.02, 32.10),
            (39.10, 32.10),
            (39.10, 32.02),
        ],
        {
            "building": "yes",
        },
    )

    part = _record(
        200,
        [
            (39.04, 32.04),
            (39.04, 32.06),
            (39.06, 32.06),
            (39.06, 32.04),
        ],
        {
            "building:part": "yes",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            outer_parent,
            inner_parent,
            part,
        ]
    )

    assert result["part_to_parent"][200] == 101


def test_leaves_non_contained_part_unassigned():
    parent = _record(
        100,
        [
            (39.0, 32.0),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.0),
        ],
        {
            "building": "yes",
        },
    )

    part = _record(
        200,
        [
            (39.2, 32.2),
            (39.2, 32.3),
            (39.3, 32.3),
            (39.3, 32.2),
        ],
        {
            "building:part": "yes",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            part,
        ]
    )

    assert result["part_to_parent"] == {}
    assert result["unassigned_part_ids"] == [
        200,
    ]
    assert result["summary"]["assigned_building_part_count"] == 0
    assert result["summary"]["unassigned_building_part_count"] == 1


def test_record_with_both_tags_is_classified_as_building_part_only():
    record = _record(
        200,
        [
            (39.0, 32.0),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.0),
        ],
        {
            "building": "yes",
            "building:part": "yes",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            record,
        ]
    )

    assert result["summary"]["main_building_count"] == 0
    assert result["summary"]["building_part_count"] == 1


def test_single_partial_part_does_not_suppress_parent():
    parent = _record(
        100,
        [
            (39.0, 32.0),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.0),
        ],
        {
            "building": "yes",
        },
    )

    part = _record(
        200,
        [
            (39.02, 32.02),
            (39.02, 32.04),
            (39.04, 32.04),
            (39.04, 32.02),
        ],
        {
            "building:part": "yes",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            part,
        ]
    )

    assert result["suppressed_parent_ids"] == []

    assert [
        record["id"]
        for record in result["mesh_buildings"]
    ] == [
        100,
        200,
    ]

    metrics = result["parent_metrics"][100]

    assert metrics["part_count"] == 1
    assert metrics["full_decomposition"] is False
    assert metrics["repeated_detail_decomposition"] is False
    assert metrics["should_suppress"] is False


def test_full_part_decomposition_suppresses_parent():
    parent = _record(
        100,
        [
            (39.0, 32.0),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.0),
        ],
        {
            "building": "yes",
        },
    )

    left_part = _record(
        200,
        [
            (39.0, 32.0),
            (39.0, 32.05),
            (39.1, 32.05),
            (39.1, 32.0),
        ],
        {
            "building:part": "yes",
        },
    )

    right_part = _record(
        201,
        [
            (39.0, 32.05),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.05),
        ],
        {
            "building:part": "yes",
        },
    )

    independent_building = _record(
        300,
        [
            (39.2, 32.2),
            (39.2, 32.3),
            (39.3, 32.3),
            (39.3, 32.2),
        ],
        {
            "building": "yes",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            left_part,
            right_part,
            independent_building,
        ]
    )

    assert result["suppressed_parent_ids"] == [
        100,
    ]

    assert [
        record["id"]
        for record in result["mesh_buildings"]
    ] == [
        200,
        201,
        300,
    ]

    metrics = result["parent_metrics"][100]

    assert metrics["part_count"] == 2
    assert metrics["coverage_ratio"] >= 0.95
    assert metrics["full_decomposition"] is True
    assert metrics["should_suppress"] is True


def test_assigns_boundary_crossing_part_when_majority_overlaps_parent():
    parent = _record(
        100,
        [
            (39.0, 32.0),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.0),
        ],
        {
            "building": "mosque",
        },
    )

    part = _record(
        200,
        [
            (39.02, 32.08),
            (39.02, 32.12),
            (39.04, 32.12),
            (39.04, 32.08),
        ],
        {
            "building:part": "yes",
            "height": "20",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            part,
        ]
    )

    assert result["part_to_parent"] == {
        200: 100,
    }
    assert result["unassigned_part_ids"] == []


def test_does_not_assign_boundary_crossing_part_when_only_minority_overlaps():
    parent = _record(
        100,
        [
            (39.0, 32.0),
            (39.0, 32.1),
            (39.1, 32.1),
            (39.1, 32.0),
        ],
        {
            "building": "yes",
        },
    )

    part = _record(
        200,
        [
            (39.02, 32.09),
            (39.02, 32.15),
            (39.04, 32.15),
            (39.04, 32.09),
        ],
        {
            "building:part": "yes",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            part,
        ]
    )

    assert result["part_to_parent"] == {}
    assert result["unassigned_part_ids"] == [
        200,
    ]
