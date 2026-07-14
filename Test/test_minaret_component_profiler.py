import pytest

from CORE.atlas_minaret_component_profiler import (
    AtlasMinaretComponentProfiler,
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


def test_elevated_circular_wall_is_assigned_to_nearby_minaret():
    minaret = _record(
        100,
        [
            (41.000000, 29.000000),
            (41.000000, 29.000020),
            (41.000020, 29.000020),
            (41.000020, 29.000000),
        ],
        {
            "building:part": "yes",
            "tower:type": "minaret",
            "height": "72",
            "roof:shape": "pyramidal",
        },
    )

    balcony_ring = _record(
        200,
        [
            (40.999995, 28.999995),
            (40.999995, 29.000025),
            (41.000025, 29.000025),
            (41.000025, 28.999995),
        ],
        {
            "barrier": "wall",
            "building:part": "yes",
            "height": "52",
            "min_height": "50",
        },
    )

    unrelated_part = _record(
        300,
        [
            (41.001000, 29.001000),
            (41.001000, 29.001020),
            (41.001020, 29.001020),
            (41.001020, 29.001000),
        ],
        {
            "barrier": "wall",
            "building:part": "yes",
            "height": "52",
            "min_height": "50",
        },
    )

    result = AtlasMinaretComponentProfiler.analyze(
        [
            minaret,
            balcony_ring,
            unrelated_part,
        ]
    )

    assert result["minaret_ids"] == [
        100,
    ]

    assert result["component_to_minaret"] == {
        200: 100,
    }

    assert result["attached_component_ids"] == [
        200,
    ]

    assert result["unassigned_component_ids"] == [
        300,
    ]

    component = result["components_by_minaret"][100][0]

    assert component["id"] == 200
    assert component["component_type"] == "balcony_ring"
    assert component["vertical_thickness_m"] == pytest.approx(2.0)
    assert component["center_distance_m"] < 1.0


def test_regular_building_part_is_not_a_minaret_component():
    result = AtlasMinaretComponentProfiler.analyze(
        [
            _record(
                100,
                [
                    (41.0, 29.0),
                    (41.0, 29.00002),
                    (41.00002, 29.00002),
                    (41.00002, 29.0),
                ],
                {
                    "building:part": "yes",
                    "tower:type": "minaret",
                    "height": "72",
                },
            ),
            _record(
                200,
                [
                    (41.0, 29.0),
                    (41.0, 29.00002),
                    (41.00002, 29.00002),
                    (41.00002, 29.0),
                ],
                {
                    "building:part": "yes",
                    "height": "20",
                },
            ),
        ]
    )

    assert result["component_to_minaret"] == {}
    assert result["attached_component_ids"] == []
