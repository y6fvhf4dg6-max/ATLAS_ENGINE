import pytest

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


def test_repeated_small_parts_with_incomplete_coverage_create_residual_parent():
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
            "height": "20",
        },
    )

    parts = []

    # Parent alanının yalnızca sol yaklaşık %80 bölümünü,
    # çok sayıda küçük building:part ile doldur.
    row_count = 10
    column_count = 10

    lat_step = 0.1 / row_count
    lon_step = 0.08 / column_count

    source_id = 200

    for row in range(row_count):
        for column in range(column_count):
            lat_1 = 39.0 + row * lat_step
            lat_2 = lat_1 + lat_step
            lon_1 = 32.0 + column * lon_step
            lon_2 = lon_1 + lon_step

            parts.append(
                _record(
                    source_id,
                    [
                        (lat_1, lon_1),
                        (lat_1, lon_2),
                        (lat_2, lon_2),
                        (lat_2, lon_1),
                    ],
                    {
                        "building:part": "yes",
                        "height": "10",
                    },
                )
            )

            source_id += 1

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            *parts,
        ]
    )

    metrics = result["parent_metrics"][100]

    assert metrics["repeated_detail_decomposition"] is True
    assert 0.75 <= metrics["coverage_ratio"] <= 0.85

    # Eksik kapsamada parent bütünüyle mesh dışına atılmamalı;
    # yalnızca uncovered alan residual kayıt olarak üretilmeli.
    assert result["suppressed_parent_ids"] == []
    assert len(result["residual_parent_records"]) == 1

    residual = result["residual_parent_records"][0]

    assert residual["source_parent_id"] == 100
    assert residual["tags"]["building"] == "mosque"
    assert residual["tags"]["atlas:residual_parent"] == "yes"

    residual_polygon = (
        AtlasBuildingPartHierarchyProfiler._make_polygon(
            residual
        )
    )

    assert residual_polygon is not None
    assert residual_polygon.area > 0.0

    parent_polygon = (
        AtlasBuildingPartHierarchyProfiler._make_polygon(
            parent
        )
    )

    assert residual_polygon.area / parent_polygon.area == pytest.approx(
        0.20,
        abs=0.02,
    )

    mesh_ids = [
        record["id"]
        for record in result["mesh_buildings"]
    ]

    assert 100 not in mesh_ids
    assert residual["id"] in mesh_ids


def test_residual_parent_height_uses_lowest_positive_part_min_height():
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

    parts = []
    source_id = 200

    row_count = 10
    column_count = 10

    lat_step = 0.1 / row_count
    lon_step = 0.08 / column_count

    for row in range(row_count):
        for column in range(column_count):
            lat_1 = 39.0 + row * lat_step
            lat_2 = lat_1 + lat_step
            lon_1 = 32.0 + column * lon_step
            lon_2 = lon_1 + lon_step

            min_height = "5" if source_id == 200 else "12"

            parts.append(
                _record(
                    source_id,
                    [
                        (lat_1, lon_1),
                        (lat_1, lon_2),
                        (lat_2, lon_2),
                        (lat_2, lon_1),
                    ],
                    {
                        "building:part": "yes",
                        "height": "20",
                        "min_height": min_height,
                    },
                )
            )

            source_id += 1

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            *parts,
        ]
    )

    residuals = result["residual_parent_records"]

    assert residuals
    assert all(
        record["tags"]["height"] == "5.0"
        for record in residuals
    )
    assert all(
        record["tags"].get("min_height") is None
        for record in residuals
    )

    metrics = result["parent_metrics"][100]

    assert metrics["residual_height_m"] == pytest.approx(5.0)
    assert metrics["residual_height_source"] == "minimum_part_min_height"


def test_attached_minaret_components_are_not_independent_mesh_buildings():
    parent = _record(
        100,
        [
            (41.0, 29.0),
            (41.0, 29.001),
            (41.001, 29.001),
            (41.001, 29.0),
        ],
        {
            "building": "mosque",
        },
    )

    minaret = _record(
        200,
        [
            (41.00010, 29.00010),
            (41.00010, 29.00014),
            (41.00014, 29.00014),
            (41.00014, 29.00010),
        ],
        {
            "building:part": "yes",
            "tower:type": "minaret",
            "height": "72",
        },
    )

    balcony_ring = _record(
        201,
        [
            (41.00009, 29.00009),
            (41.00009, 29.00015),
            (41.00015, 29.00015),
            (41.00015, 29.00009),
        ],
        {
            "barrier": "wall",
            "building:part": "yes",
            "height": "52",
            "min_height": "50",
        },
    )

    result = AtlasBuildingPartHierarchyProfiler.analyze(
        [
            parent,
            minaret,
            balcony_ring,
        ]
    )

    assert result["attached_minaret_component_ids"] == [
        201,
    ]

    assert result["minaret_component_to_minaret"] == {
        201: 200,
    }

    mesh_ids = [
        record["id"]
        for record in result["mesh_buildings"]
    ]

    assert 200 in mesh_ids
    assert 201 not in mesh_ids

    assert (
        result["minaret_components_by_minaret"][200][0]["id"]
        == 201
    )
