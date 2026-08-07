import pytest

from CORE.atlas_linear_infrastructure_geometry_builder import (
    AtlasLinearInfrastructureGeometryBuilder,
)


def test_linear_strip_builds_product_width_band():
    footprint = (
        AtlasLinearInfrastructureGeometryBuilder
        .build_linear_strip(
            points=[
                (0.0, 0.0),
                (10.0, 0.0),
            ],
            physical_width_mm=2.0,
        )
    )

    assert len(footprint) == 4

    ys = sorted(
        point[1]
        for point in footprint
    )

    assert ys == pytest.approx(
        [-1.0, -1.0, 1.0, 1.0]
    )


def test_linear_strip_preserves_input_points():
    points = [
        (0.0, 0.0),
        (10.0, 0.0),
        (15.0, 5.0),
    ]
    original = list(points)

    AtlasLinearInfrastructureGeometryBuilder.build_linear_strip(
        points=points,
        physical_width_mm=1.2,
    )

    assert points == original


@pytest.mark.parametrize(
    "physical_width_mm",
    [
        0.0,
        -0.1,
    ],
)
def test_linear_strip_rejects_non_positive_width(
    physical_width_mm,
):
    with pytest.raises(ValueError):
        AtlasLinearInfrastructureGeometryBuilder.build_linear_strip(
            points=[
                (0.0, 0.0),
                (10.0, 0.0),
            ],
            physical_width_mm=physical_width_mm,
        )


def test_linear_strip_rejects_insufficient_geometry():
    assert (
        AtlasLinearInfrastructureGeometryBuilder.build_linear_strip(
            points=[(0.0, 0.0)],
            physical_width_mm=1.0,
        )
        == []
    )


def test_area_strip_preserves_closed_polygon_footprint():
    points = [
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 5.0),
        (0.0, 5.0),
        (0.0, 0.0),
    ]

    footprint = (
        AtlasLinearInfrastructureGeometryBuilder
        .build_area_strip(
            points=points,
        )
    )

    assert footprint == points
    assert footprint is not points


def test_area_strip_rejects_open_polygon():
    assert (
        AtlasLinearInfrastructureGeometryBuilder
        .build_area_strip(
            points=[
                (0.0, 0.0),
                (10.0, 0.0),
                (10.0, 5.0),
                (0.0, 5.0),
            ],
        )
        == []
    )


def test_area_strip_rejects_insufficient_geometry():
    assert (
        AtlasLinearInfrastructureGeometryBuilder
        .build_area_strip(
            points=[
                (0.0, 0.0),
                (1.0, 0.0),
            ],
        )
        == []
    )


def test_build_from_source_uses_linear_strip_for_tram():
    result = AtlasLinearInfrastructureGeometryBuilder.build_from_source(
        tags={"railway": "tram"},
        points=[
            (0.0, 0.0),
            (10.0, 0.0),
        ],
        physical_width_mm=2.0,
    )

    assert len(result) == 4


def test_build_from_source_uses_area_strip_for_railway_landuse():
    points = [
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 5.0),
        (0.0, 5.0),
        (0.0, 0.0),
    ]

    result = AtlasLinearInfrastructureGeometryBuilder.build_from_source(
        tags={"landuse": "railway"},
        points=points,
        physical_width_mm=1.0,
    )

    assert result == points


def test_build_from_source_rejects_unsupported_geometry_kind():
    assert (
        AtlasLinearInfrastructureGeometryBuilder.build_from_source(
            tags={"railway": "platform"},
            points=[
                (0.0, 0.0),
                (10.0, 0.0),
            ],
            physical_width_mm=1.0,
        )
        == []
    )


class _CoordinateEngine:
    def geometry_to_stl_mm(self, geometry):
        return [
            (lon * 10.0, lat * 10.0)
            for lat, lon in geometry
        ]


class _Profile:
    physical_width_mm = 2.0


def test_build_product_footprint_converts_source_geometry_to_product_xy():
    item = {
        "geometry": [
            (1.0, 2.0),
            (1.0, 3.0),
        ],
        "tags": {
            "railway": "tram",
        },
    }

    footprint = (
        AtlasLinearInfrastructureGeometryBuilder
        .build_product_footprint(
            item=item,
            coordinate_engine=_CoordinateEngine(),
            profile=_Profile(),
        )
    )

    xs = sorted(
        point[0]
        for point in footprint
    )

    assert min(xs) == pytest.approx(20.0)
    assert max(xs) == pytest.approx(30.0)


def test_build_product_footprint_uses_profile_physical_width():
    item = {
        "geometry": [
            (1.0, 2.0),
            (1.0, 3.0),
        ],
        "tags": {
            "railway": "tram",
        },
    }

    footprint = (
        AtlasLinearInfrastructureGeometryBuilder
        .build_product_footprint(
            item=item,
            coordinate_engine=_CoordinateEngine(),
            profile=_Profile(),
        )
    )

    ys = sorted(
        point[1]
        for point in footprint
    )

    assert min(ys) == pytest.approx(9.0)
    assert max(ys) == pytest.approx(11.0)


def test_build_product_footprint_rejects_missing_source_geometry():
    assert (
        AtlasLinearInfrastructureGeometryBuilder
        .build_product_footprint(
            item={
                "geometry": [],
                "tags": {
                    "railway": "tram",
                },
            },
            coordinate_engine=_CoordinateEngine(),
            profile=_Profile(),
        )
        == []
    )
