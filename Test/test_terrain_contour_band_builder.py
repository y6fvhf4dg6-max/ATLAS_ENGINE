import pytest

from CORE.atlas_terrain_contour_band_builder import (
    AtlasTerrainContourBandBuilder,
)


def test_empty_polyline_returns_empty_band():
    assert (
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[],
            half_width_mm=0.20,
        )
        == []
    )


def test_single_point_returns_empty_band():
    assert (
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[
                (0.0, 0.0),
            ],
            half_width_mm=0.20,
        )
        == []
    )


def test_straight_line_creates_parallel_band():
    band = (
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[
                (0.0, 0.0),
                (10.0, 0.0),
            ],
            half_width_mm=1.0,
        )
    )

    assert len(band) == 4

    ys = sorted(
        point[1]
        for point in band
    )

    assert ys == pytest.approx(
        [-1.0, -1.0, 1.0, 1.0]
    )


def test_band_width_is_constant():
    band = (
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[
                (0.0, 0.0),
                (20.0, 0.0),
            ],
            half_width_mm=0.75,
        )
    )

    top = max(
        point[1]
        for point in band
    )

    bottom = min(
        point[1]
        for point in band
    )

    assert (
        top - bottom
    ) == pytest.approx(
        1.5
    )


def test_non_positive_width_is_rejected():
    with pytest.raises(
        ValueError,
        match="half_width_mm",
    ):
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[
                (0.0, 0.0),
                (10.0, 0.0),
            ],
            half_width_mm=0.0,
        )

def test_l_shaped_polyline_creates_band():
    band = (
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[
                (0.0, 0.0),
                (10.0, 0.0),
                (10.0, 10.0),
            ],
            half_width_mm=1.0,
        )
    )

    assert len(band) >= 6


def test_closed_square_creates_closed_band():
    band = (
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[
                (0.0, 0.0),
                (10.0, 0.0),
                (10.0, 10.0),
                (0.0, 10.0),
                (0.0, 0.0),
            ],
            half_width_mm=1.0,
        )
    )

    assert len(band) >= 10


def test_duplicate_points_are_ignored():
    band = (
        AtlasTerrainContourBandBuilder.build_band(
            polyline=[
                (0.0, 0.0),
                (10.0, 0.0),
                (10.0, 0.0),
                (20.0, 0.0),
            ],
            half_width_mm=1.0,
        )
    )

    assert len(band) >= 4


def test_polyline_is_not_modified():
    polyline = [
        (0.0, 0.0),
        (10.0, 0.0),
        (20.0, 5.0),
    ]

    original = list(polyline)

    AtlasTerrainContourBandBuilder.build_band(
        polyline,
        1.0,
    )

    assert polyline == original

