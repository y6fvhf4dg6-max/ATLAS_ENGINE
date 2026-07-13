"""
ATLAS Foundation Scene BBOX Filter Regression Tests

Geniş kaynak alanından okunan binaların, sonradan hesaplanan
working_bbox dışında kalmaları durumunda sahneye eklenmemesini doğrular.
"""

from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
)


BBOX = (
    41.0830,
    29.0540,
    41.0870,
    29.0580,
)


def test_building_inside_bbox_is_kept():
    geometry = [
        (41.0840, 29.0550),
        (41.0840, 29.0560),
        (41.0850, 29.0560),
        (41.0850, 29.0550),
    ]

    assert (
        AtlasFoundationSceneBuilder
        ._geometry_intersects_bbox(
            geometry=geometry,
            bbox=BBOX,
        )
        is True
    )


def test_building_outside_bbox_is_rejected():
    geometry = [
        (41.0800, 29.0500),
        (41.0800, 29.0510),
        (41.0810, 29.0510),
        (41.0810, 29.0500),
    ]

    assert (
        AtlasFoundationSceneBuilder
        ._geometry_intersects_bbox(
            geometry=geometry,
            bbox=BBOX,
        )
        is False
    )


def test_building_crossing_bbox_boundary_is_kept():
    geometry = [
        (41.0825, 29.0550),
        (41.0825, 29.0560),
        (41.0835, 29.0560),
        (41.0835, 29.0550),
    ]

    assert (
        AtlasFoundationSceneBuilder
        ._geometry_intersects_bbox(
            geometry=geometry,
            bbox=BBOX,
        )
        is True
    )
