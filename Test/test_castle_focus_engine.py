"""
ATLAS Castle Focus Engine Regression Tests

Relation outer/inner rollerinin ters veya hatalı geldiği durumlarda
focus bbox hesabının gerçek dış kale sınırını kullanmasını doğrular.
"""

from CORE.atlas_castle_focus_engine import (
    AtlasCastleFocusEngine,
)


def test_focus_bbox_uses_largest_relation_ring_as_real_outer():
    small_ring = [
        (41.0840, 29.0555),
        (41.0840, 29.0565),
        (41.0858, 29.0565),
        (41.0858, 29.0555),
        (41.0840, 29.0555),
    ]

    large_ring = [
        (41.0838, 29.0553),
        (41.0838, 29.0568),
        (41.0860, 29.0568),
        (41.0860, 29.0553),
        (41.0838, 29.0553),
    ]

    shell_castle = {
        "id": 7318154,
        "geometry_type": "relation",
        "geometry": small_ring,
        "outer_geometries": [small_ring],
        "inner_geometries": [large_ring],
        "tags": {
            "historic": "castle",
        },
    }

    source_bbox = (
        41.0800,
        29.0500,
        41.0900,
        29.0600,
    )

    result = AtlasCastleFocusEngine.calculate_focus_bbox(
        raw_buildings=[],
        castles=[shell_castle],
        independent_castle_walls=[],
        shell_castles=[shell_castle],
        source_bbox=source_bbox,
        min_points=3,
        max_points=500,
        padding_m=0.0,
        debug=False,
    )

    assert result["raw_bbox"] == (
        41.0838,
        29.0553,
        41.0860,
        29.0568,
    )


def test_focus_bbox_keeps_valid_relation_outer_ring():
    outer_ring = [
        (41.0838, 29.0553),
        (41.0838, 29.0568),
        (41.0860, 29.0568),
        (41.0860, 29.0553),
        (41.0838, 29.0553),
    ]

    inner_ring = [
        (41.0840, 29.0555),
        (41.0840, 29.0565),
        (41.0858, 29.0565),
        (41.0858, 29.0555),
        (41.0840, 29.0555),
    ]

    shell_castle = {
        "id": 1,
        "geometry_type": "relation",
        "geometry": outer_ring,
        "outer_geometries": [outer_ring],
        "inner_geometries": [inner_ring],
        "tags": {
            "historic": "castle",
        },
    }

    source_bbox = (
        41.0800,
        29.0500,
        41.0900,
        29.0600,
    )

    result = AtlasCastleFocusEngine.calculate_focus_bbox(
        raw_buildings=[],
        castles=[shell_castle],
        independent_castle_walls=[],
        shell_castles=[shell_castle],
        source_bbox=source_bbox,
        min_points=3,
        max_points=500,
        padding_m=0.0,
        debug=False,
    )

    assert result["raw_bbox"] == (
        41.0838,
        29.0553,
        41.0860,
        29.0568,
    )
