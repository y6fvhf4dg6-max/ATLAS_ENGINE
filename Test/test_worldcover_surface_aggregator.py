import pytest

from CORE.atlas_worldcover_surface_aggregator import (
    AtlasWorldCoverSurfaceAggregator,
)


STEP = 1.0 / 12000.0


def _cell(
    row,
    column,
    *,
    base_lat=50.0,
    base_lon=8.0,
    class_id=10,
):
    return {
        "lat": base_lat + row * STEP,
        "lon": base_lon + column * STEP,
        "class_id": class_id,
        "source": "worldcover",
        "resolution_m": 10,
    }


def test_horizontal_adjacent_cells_merge_into_one_surface():
    cells = [
        _cell(0, 0),
        _cell(0, 1),
        _cell(0, 2),
    ]

    result = AtlasWorldCoverSurfaceAggregator.aggregate(
        cells=cells,
        surface_type="forest",
    )

    assert len(result) == 1

    surface = result[0]

    assert surface["surface_type"] == "forest"
    assert surface["source"] == "worldcover"
    assert surface["cell_count"] == 3
    assert len(surface["geometry"]) == 4

    south = 50.0 - STEP / 2.0
    north = 50.0 + STEP / 2.0
    west = 8.0 - STEP / 2.0
    east = 8.0 + 2.0 * STEP + STEP / 2.0

    expected_geometry = [
        (south, west),
        (south, east),
        (north, east),
        (north, west),
    ]

    for actual, expected in zip(
        surface["geometry"],
        expected_geometry,
    ):
        assert actual[0] == pytest.approx(
            expected[0],
            abs=1e-12,
        )
        assert actual[1] == pytest.approx(
            expected[1],
            abs=1e-12,
        )


def test_vertical_runs_with_same_column_extent_merge():
    cells = [
        _cell(0, 0),
        _cell(0, 1),
        _cell(1, 0),
        _cell(1, 1),
        _cell(2, 0),
        _cell(2, 1),
    ]

    result = AtlasWorldCoverSurfaceAggregator.aggregate(
        cells=cells,
        surface_type="forest",
    )

    assert len(result) == 1
    assert result[0]["cell_count"] == 6

    south = 50.0 - STEP / 2.0
    north = 50.0 + 2.0 * STEP + STEP / 2.0
    west = 8.0 - STEP / 2.0
    east = 8.0 + STEP + STEP / 2.0

    expected_geometry = [
        (south, west),
        (south, east),
        (north, east),
        (north, west),
    ]

    for actual, expected in zip(
        result[0]["geometry"],
        expected_geometry,
    ):
        assert actual[0] == pytest.approx(
            expected[0],
            abs=1e-12,
        )
        assert actual[1] == pytest.approx(
            expected[1],
            abs=1e-12,
        )


def test_disconnected_cells_remain_separate_surfaces():
    cells = [
        _cell(0, 0),
        _cell(0, 1),
        _cell(0, 4),
        _cell(0, 5),
    ]

    result = AtlasWorldCoverSurfaceAggregator.aggregate(
        cells=cells,
        surface_type="grass",
    )

    assert len(result) == 2
    assert [item["cell_count"] for item in result] == [2, 2]
    assert all(
        item["surface_type"] == "grass"
        for item in result
    )


def test_different_row_shapes_do_not_merge_incorrectly():
    cells = [
        _cell(0, 0),
        _cell(0, 1),
        _cell(1, 0),
        _cell(1, 1),
        _cell(1, 2),
    ]

    result = AtlasWorldCoverSurfaceAggregator.aggregate(
        cells=cells,
        surface_type="forest",
    )

    assert len(result) == 2
    assert sorted(
        item["cell_count"]
        for item in result
    ) == [2, 3]


def test_duplicate_cells_are_removed():
    cell = _cell(0, 0)

    result = AtlasWorldCoverSurfaceAggregator.aggregate(
        cells=[
            cell,
            dict(cell),
            _cell(0, 1),
        ],
        surface_type="forest",
    )

    assert len(result) == 1
    assert result[0]["cell_count"] == 2


def test_result_is_deterministic_for_reordered_input():
    cells = [
        _cell(0, 0),
        _cell(0, 1),
        _cell(1, 0),
        _cell(1, 1),
        _cell(4, 4),
    ]

    first = AtlasWorldCoverSurfaceAggregator.aggregate(
        cells=cells,
        surface_type="forest",
    )

    second = AtlasWorldCoverSurfaceAggregator.aggregate(
        cells=list(reversed(cells)),
        surface_type="forest",
    )

    assert first == second


def test_empty_input_returns_empty_list():
    assert (
        AtlasWorldCoverSurfaceAggregator.aggregate(
            cells=[],
            surface_type="grass",
        )
        == []
    )


def test_invalid_surface_type_is_rejected():
    try:
        AtlasWorldCoverSurfaceAggregator.aggregate(
            cells=[_cell(0, 0)],
            surface_type="water",
        )
    except ValueError as error:
        assert "surface_type" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_dissolve_merges_connected_grass_cells_into_polygon():
    cells = [
        _cell(0, 0, class_id=30),
        _cell(0, 1, class_id=30),
        _cell(1, 0, class_id=30),
        _cell(1, 1, class_id=30),
    ]

    result = AtlasWorldCoverSurfaceAggregator.dissolve(
        cells=cells,
        surface_type="grass",
    )

    assert len(result) == 1

    surface = result[0]

    assert surface["id"] == "worldcover_grass_surface_0"
    assert surface["surface_type"] == "grass"
    assert surface["source"] == "worldcover"
    assert surface["cell_count"] == 4
    assert surface["park_type"] == "worldcover:grass"
    assert len(surface["geometry"]) == 4
    assert surface["tags"]["source"] == "worldcover"
    assert surface["tags"]["class_id"] == 30


def test_dissolve_keeps_disconnected_components_separate():
    cells = [
        _cell(0, 0, class_id=30),
        _cell(0, 1, class_id=30),
        _cell(0, 5, class_id=30),
    ]

    result = AtlasWorldCoverSurfaceAggregator.dissolve(
        cells=cells,
        surface_type="grass",
    )

    assert len(result) == 2
    assert sorted(
        surface["cell_count"]
        for surface in result
    ) == [1, 2]


def test_dissolve_result_is_deterministic():
    cells = [
        _cell(0, 0, class_id=30),
        _cell(0, 1, class_id=30),
        _cell(1, 0, class_id=30),
    ]

    first = AtlasWorldCoverSurfaceAggregator.dissolve(
        cells=cells,
        surface_type="grass",
    )

    second = AtlasWorldCoverSurfaceAggregator.dissolve(
        cells=list(reversed(cells)),
        surface_type="grass",
    )

    assert first == second


def test_dissolve_can_remove_tiny_components():
    cells = [
        _cell(0, 0, class_id=30),
        _cell(0, 1, class_id=30),
        _cell(0, 5, class_id=30),
    ]

    result = AtlasWorldCoverSurfaceAggregator.dissolve(
        cells=cells,
        surface_type="grass",
        min_cell_count=2,
    )

    assert len(result) == 1
    assert result[0]["cell_count"] == 2


def test_dissolve_rejects_polygons_with_holes_by_default():
    cells = [
        _cell(0, 0, class_id=30),
        _cell(0, 1, class_id=30),
        _cell(0, 2, class_id=30),
        _cell(1, 0, class_id=30),
        _cell(1, 2, class_id=30),
        _cell(2, 0, class_id=30),
        _cell(2, 1, class_id=30),
        _cell(2, 2, class_id=30),
    ]

    result = AtlasWorldCoverSurfaceAggregator.dissolve(
        cells=cells,
        surface_type="grass",
    )

    assert result == []
