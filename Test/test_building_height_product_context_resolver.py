import pytest

from CORE.atlas_building_height_product_context_resolver import (
    AtlasBuildingHeightProductContextResolver,
)
from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)


def _coordinate_engine():
    return AtlasCoordinateEngine(
        origin_lat=50.0,
        origin_lon=8.0,
        xy_scale=5500.0,
        z_scale=5500.0,
    )


def test_resolves_block_height_context_in_real_meter_space():
    coordinate_engine = _coordinate_engine()

    buildings = (
        {
            "id": 100,
            "geometry": (
                (50.00010, 8.00010),
                (50.00010, 8.00020),
                (50.00020, 8.00020),
                (50.00020, 8.00010),
            ),
            "tags": {
                "building": "yes",
                "height": "10",
            },
        },
        {
            "id": 101,
            "geometry": (
                (50.00030, 8.00010),
                (50.00030, 8.00020),
                (50.00040, 8.00020),
                (50.00040, 8.00010),
            ),
            "tags": {
                "building": "yes",
                "height": "14",
            },
        },
        {
            "id": 102,
            "geometry": (
                (50.00050, 8.00010),
                (50.00050, 8.00020),
                (50.00060, 8.00020),
                (50.00060, 8.00010),
            ),
            "tags": {
                "building": "yes",
                "height": "24",
            },
        },
    )

    roads = (
        {
            "id": 1,
            "geometry": (
                (50.00000, 8.00000),
                (50.00000, 8.00100),
            ),
            "tags": {"highway": "residential"},
        },
        {
            "id": 2,
            "geometry": (
                (50.00000, 8.00100),
                (50.00100, 8.00100),
            ),
            "tags": {"highway": "residential"},
        },
        {
            "id": 3,
            "geometry": (
                (50.00100, 8.00100),
                (50.00100, 8.00000),
            ),
            "tags": {"highway": "residential"},
        },
        {
            "id": 4,
            "geometry": (
                (50.00100, 8.00000),
                (50.00000, 8.00000),
            ),
            "tags": {"highway": "residential"},
        },
    )

    context = (
        AtlasBuildingHeightProductContextResolver.resolve(
            buildings=buildings,
            roads=roads,
            landmarks=(),
            coordinate_engine=coordinate_engine,
        )
    )

    assert set(context) == {
        100,
        101,
        102,
    }

    assert context[100][
        "block_median_height_m"
    ] == pytest.approx(14.0)

    assert context[101][
        "block_median_height_m"
    ] == pytest.approx(14.0)

    assert context[102][
        "block_median_height_m"
    ] == pytest.approx(14.0)


def test_landmark_distance_is_reported_in_meters_not_latlon_degrees():
    coordinate_engine = _coordinate_engine()

    buildings = (
        {
            "id": 100,
            "geometry": (
                (50.00010, 8.00010),
                (50.00010, 8.00020),
                (50.00020, 8.00020),
                (50.00020, 8.00010),
            ),
            "tags": {
                "building": "yes",
                "height": "12",
            },
        },
    )

    roads = (
        {
            "id": 1,
            "geometry": (
                (50.00000, 8.00000),
                (50.00000, 8.00100),
            ),
            "tags": {"highway": "residential"},
        },
        {
            "id": 2,
            "geometry": (
                (50.00000, 8.00100),
                (50.00100, 8.00100),
            ),
            "tags": {"highway": "residential"},
        },
        {
            "id": 3,
            "geometry": (
                (50.00100, 8.00100),
                (50.00100, 8.00000),
            ),
            "tags": {"highway": "residential"},
        },
        {
            "id": 4,
            "geometry": (
                (50.00100, 8.00000),
                (50.00000, 8.00000),
            ),
            "tags": {"highway": "residential"},
        },
    )

    landmarks = (
        {
            "id": 900,
            "geometry": (
                (50.00050, 8.00050),
                (50.00050, 8.00060),
                (50.00060, 8.00060),
                (50.00060, 8.00050),
            ),
            "tags": {
                "historic": "monument",
            },
        },
    )

    context = (
        AtlasBuildingHeightProductContextResolver.resolve(
            buildings=buildings,
            roads=roads,
            landmarks=landmarks,
            coordinate_engine=coordinate_engine,
        )
    )

    distance = context[100][
        "landmark_distance_m"
    ]

    assert distance is not None
    assert 20.0 < distance < 100.0


def test_uses_existing_semantic_importance_without_inventing_priority():
    coordinate_engine = _coordinate_engine()

    buildings = (
        {
            "id": 100,
            "geometry": (
                (50.00010, 8.00010),
                (50.00010, 8.00020),
                (50.00020, 8.00020),
                (50.00020, 8.00010),
            ),
            "tags": {
                "building": "yes",
                "height": "12",
            },
            "semantic_importance": 0.75,
        },
    )

    context = (
        AtlasBuildingHeightProductContextResolver.resolve(
            buildings=buildings,
            roads=(),
            landmarks=(),
            coordinate_engine=coordinate_engine,
        )
    )

    assert context[100][
        "semantic_importance"
    ] == pytest.approx(0.75)


def test_falls_back_to_existing_product_priority_then_zero():
    coordinate_engine = _coordinate_engine()

    buildings = (
        {
            "id": 100,
            "geometry": (
                (50.00010, 8.00010),
                (50.00010, 8.00020),
                (50.00020, 8.00020),
                (50.00020, 8.00010),
            ),
            "tags": {
                "building": "yes",
                "height": "12",
            },
            "product_priority": 0.60,
        },
        {
            "id": 101,
            "geometry": (
                (50.00030, 8.00010),
                (50.00030, 8.00020),
                (50.00040, 8.00020),
                (50.00040, 8.00010),
            ),
            "tags": {
                "building": "yes",
                "height": "12",
            },
        },
    )

    context = (
        AtlasBuildingHeightProductContextResolver.resolve(
            buildings=buildings,
            roads=(),
            landmarks=(),
            coordinate_engine=coordinate_engine,
        )
    )

    assert context[100][
        "semantic_importance"
    ] == pytest.approx(0.60)

    assert context[101][
        "semantic_importance"
    ] == pytest.approx(0.0)


def test_preserves_source_height_truth_in_context():
    coordinate_engine = _coordinate_engine()

    building = {
        "id": 100,
        "geometry": (
            (50.00010, 8.00010),
            (50.00010, 8.00020),
            (50.00020, 8.00020),
            (50.00020, 8.00010),
        ),
        "tags": {
            "building": "yes",
            "height": "24",
        },
    }

    context = (
        AtlasBuildingHeightProductContextResolver.resolve(
            buildings=(building,),
            roads=(),
            landmarks=(),
            coordinate_engine=coordinate_engine,
        )
    )

    assert building["tags"]["height"] == "24"
    assert context[100][
        "source_height_m"
    ] == pytest.approx(24.0)
