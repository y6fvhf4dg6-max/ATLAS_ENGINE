import pytest

from CORE.atlas_terrain_contour_terrace_builder import (
    AtlasTerrainContourTerraceBuilder,
)


def test_sloped_triangle_produces_contour_segment():
    triangle = (
        (0.0, 0.0, 0.80),
        (10.0, 0.0, 1.40),
        (0.0, 10.0, 1.40),
    )

    segment = (
        AtlasTerrainContourTerraceBuilder
        .extract_triangle_contour_segment(
            triangle=triangle,
            contour_z=1.10,
        )
    )

    assert segment is not None
    assert segment[0] == pytest.approx(
        (0.0, 5.0, 1.10),
        abs=1e-12,
    )
    assert segment[1] == pytest.approx(
        (5.0, 0.0, 1.10),
        abs=1e-12,
    )


def test_triangle_entirely_below_contour_produces_no_segment():
    triangle = (
        (0.0, 0.0, 0.80),
        (10.0, 0.0, 0.90),
        (0.0, 10.0, 1.00),
    )

    assert (
        AtlasTerrainContourTerraceBuilder
        .extract_triangle_contour_segment(
            triangle=triangle,
            contour_z=1.10,
        )
        is None
    )


def test_triangle_entirely_above_contour_produces_no_segment():
    triangle = (
        (0.0, 0.0, 1.20),
        (10.0, 0.0, 1.30),
        (0.0, 10.0, 1.40),
    )

    assert (
        AtlasTerrainContourTerraceBuilder
        .extract_triangle_contour_segment(
            triangle=triangle,
            contour_z=1.10,
        )
        is None
    )


def test_flat_triangle_does_not_create_artificial_contour():
    triangle = (
        (0.0, 0.0, 1.10),
        (10.0, 0.0, 1.10),
        (0.0, 10.0, 1.10),
    )

    assert (
        AtlasTerrainContourTerraceBuilder
        .extract_triangle_contour_segment(
            triangle=triangle,
            contour_z=1.10,
        )
        is None
    )


def test_contour_through_single_triangle_vertex_is_deterministic():
    triangle = (
        (0.0, 0.0, 1.10),
        (10.0, 0.0, 1.40),
        (0.0, 10.0, 0.80),
    )

    segment = (
        AtlasTerrainContourTerraceBuilder
        .extract_triangle_contour_segment(
            triangle=triangle,
            contour_z=1.10,
        )
    )

    assert segment is not None
    assert segment[0] == pytest.approx(
        (0.0, 0.0, 1.10),
        abs=1e-12,
    )
    assert segment[1] == pytest.approx(
        (5.0, 5.0, 1.10),
        abs=1e-12,
    )


def test_grid_contour_segments_connect_across_cell_diagonal():
    top_points = [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 1.40),
        ],
        [
            (0.0, 10.0, 0.80),
            (10.0, 10.0, 1.40),
        ],
    ]

    segments = (
        AtlasTerrainContourTerraceBuilder
        .extract_grid_contour_segments(
            top_points=top_points,
            contour_z=1.10,
        )
    )

    assert len(segments) == 2

    vertices = {
        tuple(round(value, 12) for value in point)
        for segment in segments
        for point in segment
    }

    assert vertices == {
        (5.0, 0.0, 1.10),
        (5.0, 5.0, 1.10),
        (5.0, 10.0, 1.10),
    }


def test_flat_grid_produces_no_contour_segments():
    top_points = [
        [
            (0.0, 0.0, 1.10),
            (10.0, 0.0, 1.10),
            (20.0, 0.0, 1.10),
        ],
        [
            (0.0, 10.0, 1.10),
            (10.0, 10.0, 1.10),
            (20.0, 10.0, 1.10),
        ],
        [
            (0.0, 20.0, 1.10),
            (10.0, 20.0, 1.10),
            (20.0, 20.0, 1.10),
        ],
    ]

    segments = (
        AtlasTerrainContourTerraceBuilder
        .extract_grid_contour_segments(
            top_points=top_points,
            contour_z=1.10,
        )
    )

    assert segments == []


def test_grid_contour_extraction_is_deterministic():
    top_points = [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 1.40),
        ],
        [
            (0.0, 10.0, 0.80),
            (10.0, 10.0, 1.40),
        ],
    ]

    first = (
        AtlasTerrainContourTerraceBuilder
        .extract_grid_contour_segments(
            top_points=top_points,
            contour_z=1.10,
        )
    )

    second = (
        AtlasTerrainContourTerraceBuilder
        .extract_grid_contour_segments(
            top_points=top_points,
            contour_z=1.10,
        )
    )

    assert first == second


def test_grid_contour_extraction_rejects_ragged_rows():
    top_points = [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 1.40),
        ],
        [
            (0.0, 10.0, 0.80),
        ],
    ]

    with pytest.raises(
        ValueError,
        match="rectangular",
    ):
        (
            AtlasTerrainContourTerraceBuilder
            .extract_grid_contour_segments(
                top_points=top_points,
                contour_z=1.10,
            )
        )


def test_connected_segments_form_single_open_polyline():
    segments = [
        (
            (0.0, 0.0, 1.10),
            (5.0, 2.0, 1.10),
        ),
        (
            (5.0, 2.0, 1.10),
            (10.0, 5.0, 1.10),
        ),
        (
            (10.0, 5.0, 1.10),
            (15.0, 9.0, 1.10),
        ),
    ]

    lines = (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=segments,
        )
    )

    assert len(lines) == 1
    assert lines[0]["closed"] is False
    assert lines[0]["points"] == [
        (0.0, 0.0, 1.10),
        (5.0, 2.0, 1.10),
        (10.0, 5.0, 1.10),
        (15.0, 9.0, 1.10),
    ]


def test_reversed_segments_connect_deterministically():
    segments = [
        (
            (10.0, 5.0, 1.10),
            (5.0, 2.0, 1.10),
        ),
        (
            (15.0, 9.0, 1.10),
            (10.0, 5.0, 1.10),
        ),
        (
            (5.0, 2.0, 1.10),
            (0.0, 0.0, 1.10),
        ),
    ]

    lines = (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=segments,
        )
    )

    assert len(lines) == 1
    assert lines[0]["points"] == [
        (0.0, 0.0, 1.10),
        (5.0, 2.0, 1.10),
        (10.0, 5.0, 1.10),
        (15.0, 9.0, 1.10),
    ]


def test_closed_segments_form_contour_loop():
    segments = [
        (
            (0.0, 0.0, 1.40),
            (10.0, 0.0, 1.40),
        ),
        (
            (10.0, 0.0, 1.40),
            (10.0, 10.0, 1.40),
        ),
        (
            (10.0, 10.0, 1.40),
            (0.0, 10.0, 1.40),
        ),
        (
            (0.0, 10.0, 1.40),
            (0.0, 0.0, 1.40),
        ),
    ]

    lines = (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=segments,
        )
    )

    assert len(lines) == 1
    assert lines[0]["closed"] is True

    assert lines[0]["points"][0] == lines[0]["points"][-1]

    assert set(lines[0]["points"][:-1]) == {
        (0.0, 0.0, 1.40),
        (10.0, 0.0, 1.40),
        (10.0, 10.0, 1.40),
        (0.0, 10.0, 1.40),
    }


def test_disconnected_segments_form_multiple_lines():
    segments = [
        (
            (0.0, 0.0, 1.10),
            (5.0, 0.0, 1.10),
        ),
        (
            (5.0, 0.0, 1.10),
            (10.0, 0.0, 1.10),
        ),
        (
            (20.0, 0.0, 1.10),
            (25.0, 5.0, 1.10),
        ),
    ]

    lines = (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=segments,
        )
    )

    assert len(lines) == 2


def test_duplicate_segments_are_removed():
    segment = (
        (0.0, 0.0, 1.10),
        (10.0, 0.0, 1.10),
    )

    lines = (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=[
                segment,
                segment,
                tuple(reversed(segment)),
            ],
        )
    )

    assert len(lines) == 1
    assert lines[0]["points"] == [
        (0.0, 0.0, 1.10),
        (10.0, 0.0, 1.10),
    ]


def test_empty_segment_list_produces_no_contour_lines():
    assert (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=[],
        )
        == []
    )


def test_connected_contours_are_deterministic():
    segments = [
        (
            (10.0, 0.0, 1.10),
            (20.0, 5.0, 1.10),
        ),
        (
            (0.0, 0.0, 1.10),
            (10.0, 0.0, 1.10),
        ),
    ]

    first = (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=segments,
        )
    )

    second = (
        AtlasTerrainContourTerraceBuilder
        .connect_contour_segments(
            segments=list(reversed(segments)),
        )
    )

    assert first == second


def test_build_contour_levels_returns_internal_levels_only():
    levels = (
        AtlasTerrainContourTerraceBuilder
        .build_contour_levels(
            top_points=[
                [
                    (0.0, 0.0, 0.80),
                    (10.0, 0.0, 1.70),
                ],
                [
                    (0.0, 10.0, 0.80),
                    (10.0, 10.0, 1.70),
                ],
            ],
            base_z=0.80,
            contour_step_mm=0.30,
        )
    )

    assert levels == pytest.approx(
        [
            1.10,
            1.40,
        ],
        abs=1e-12,
    )


def test_flat_terrain_has_no_contour_levels():
    levels = (
        AtlasTerrainContourTerraceBuilder
        .build_contour_levels(
            top_points=[
                [
                    (0.0, 0.0, 1.10),
                    (10.0, 0.0, 1.10),
                ],
                [
                    (0.0, 10.0, 1.10),
                    (10.0, 10.0, 1.10),
                ],
            ],
            base_z=0.80,
            contour_step_mm=0.12,
        )
    )

    assert levels == []


def test_build_contour_levels_rejects_non_positive_step():
    with pytest.raises(
        ValueError,
        match="contour_step_mm",
    ):
        (
            AtlasTerrainContourTerraceBuilder
            .build_contour_levels(
                top_points=[
                    [
                        (0.0, 0.0, 0.80),
                        (10.0, 0.0, 1.40),
                    ],
                    [
                        (0.0, 10.0, 0.80),
                        (10.0, 10.0, 1.40),
                    ],
                ],
                base_z=0.80,
                contour_step_mm=0.0,
            )
        )


def _synthetic_hill_top_points():
    return [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 1.10),
            (20.0, 0.0, 0.80),
        ],
        [
            (0.0, 10.0, 1.10),
            (10.0, 10.0, 1.70),
            (20.0, 10.0, 1.10),
        ],
        [
            (0.0, 20.0, 0.80),
            (10.0, 20.0, 1.10),
            (20.0, 20.0, 0.80),
        ],
    ]


def test_extract_contours_builds_closed_hill_loop():
    contours = (
        AtlasTerrainContourTerraceBuilder
        .extract_contours(
            top_points=_synthetic_hill_top_points(),
            base_z=0.80,
            contour_step_mm=0.30,
        )
    )

    contour_110 = next(
        contour
        for contour in contours
        if contour["contour_z"]
        == pytest.approx(1.10)
    )

    assert len(contour_110["lines"]) == 1
    assert contour_110["lines"][0]["closed"] is True
    assert (
        contour_110["lines"][0]["points"][0]
        == contour_110["lines"][0]["points"][-1]
    )


def test_hill_contours_shrink_toward_summit():
    contours = (
        AtlasTerrainContourTerraceBuilder
        .extract_contours(
            top_points=_synthetic_hill_top_points(),
            base_z=0.80,
            contour_step_mm=0.30,
        )
    )

    closed_lines = {}

    for contour in contours:
        lines = [
            line
            for line in contour["lines"]
            if line["closed"]
        ]

        if lines:
            closed_lines[
                round(contour["contour_z"], 12)
            ] = lines[0]

    assert set(closed_lines) == {
        1.10,
        1.40,
    }

    def bounds_area(line):
        points = line["points"][:-1]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        return (
            (max(xs) - min(xs))
            * (max(ys) - min(ys))
        )

    assert (
        bounds_area(closed_lines[1.40])
        < bounds_area(closed_lines[1.10])
    )


def test_flat_terrain_extracts_no_contours():
    flat = [
        [
            (0.0, 0.0, 1.10),
            (10.0, 0.0, 1.10),
            (20.0, 0.0, 1.10),
        ],
        [
            (0.0, 10.0, 1.10),
            (10.0, 10.0, 1.10),
            (20.0, 10.0, 1.10),
        ],
        [
            (0.0, 20.0, 1.10),
            (10.0, 20.0, 1.10),
            (20.0, 20.0, 1.10),
        ],
    ]

    contours = (
        AtlasTerrainContourTerraceBuilder
        .extract_contours(
            top_points=flat,
            base_z=0.80,
            contour_step_mm=0.12,
        )
    )

    assert contours == []


def test_extract_contours_is_deterministic():
    first = (
        AtlasTerrainContourTerraceBuilder
        .extract_contours(
            top_points=_synthetic_hill_top_points(),
            base_z=0.80,
            contour_step_mm=0.30,
        )
    )

    second = (
        AtlasTerrainContourTerraceBuilder
        .extract_contours(
            top_points=_synthetic_hill_top_points(),
            base_z=0.80,
            contour_step_mm=0.30,
        )
    )

    assert first == second
