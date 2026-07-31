import math

import pytest

from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)


def _rotate(point, angle_radians):
    x, y = point

    return (
        x * math.cos(angle_radians)
        - y * math.sin(angle_radians),
        x * math.sin(angle_radians)
        + y * math.cos(angle_radians),
    )


def _rotated_rectangle(
    *,
    center=(12.0, -4.0),
    width=20.0,
    depth=50.0,
    angle_degrees=32.0,
):
    half_width = width / 2.0
    half_depth = depth / 2.0
    angle = math.radians(angle_degrees)

    local_points = (
        (-half_width, -half_depth),
        (half_width, -half_depth),
        (half_width, half_depth),
        (-half_width, half_depth),
    )

    return tuple(
        (
            center[0] + _rotate(point, angle)[0],
            center[1] + _rotate(point, angle)[1],
        )
        for point in local_points
    )


def test_resolver_preserves_rotated_footprint_center_and_dimensions():
    footprint = _rotated_rectangle()

    frame = AtlasChurchFootprintResolver.resolve(
        footprint
    )

    assert frame.center_x == pytest.approx(
        12.0,
        abs=1e-8,
    )
    assert frame.center_y == pytest.approx(
        -4.0,
        abs=1e-8,
    )

    assert frame.longitudinal_span == pytest.approx(
        50.0,
        abs=1e-8,
    )
    assert frame.lateral_span == pytest.approx(
        20.0,
        abs=1e-8,
    )


def test_resolver_longitudinal_axis_follows_long_side():
    footprint = _rotated_rectangle(
        angle_degrees=32.0,
    )

    frame = AtlasChurchFootprintResolver.resolve(
        footprint
    )

    expected_axis = (
        -math.sin(math.radians(32.0)),
        math.cos(math.radians(32.0)),
    )

    alignment = abs(
        frame.axis_x * expected_axis[0]
        + frame.axis_y * expected_axis[1]
    )

    assert alignment == pytest.approx(
        1.0,
        abs=1e-8,
    )


def test_local_and_world_coordinate_transforms_are_inverse():
    frame = AtlasChurchFootprintResolver.resolve(
        _rotated_rectangle()
    )

    world_point = frame.to_world(
        longitudinal=11.5,
        lateral=-3.25,
    )

    longitudinal, lateral = frame.to_local(
        world_point
    )

    assert longitudinal == pytest.approx(
        11.5,
        abs=1e-8,
    )
    assert lateral == pytest.approx(
        -3.25,
        abs=1e-8,
    )


def test_resolver_returns_oriented_rectangle_corners():
    frame = AtlasChurchFootprintResolver.resolve(
        _rotated_rectangle()
    )

    assert len(frame.oriented_rectangle) == 4

    local_corners = tuple(
        frame.to_local(point)
        for point in frame.oriented_rectangle
    )

    longitudinal_values = tuple(
        point[0]
        for point in local_corners
    )
    lateral_values = tuple(
        point[1]
        for point in local_corners
    )

    assert min(longitudinal_values) == pytest.approx(
        -25.0,
        abs=1e-8,
    )
    assert max(longitudinal_values) == pytest.approx(
        25.0,
        abs=1e-8,
    )
    assert min(lateral_values) == pytest.approx(
        -10.0,
        abs=1e-8,
    )
    assert max(lateral_values) == pytest.approx(
        10.0,
        abs=1e-8,
    )


@pytest.mark.parametrize(
    "footprint",
    [
        (),
        ((0.0, 0.0),),
        (
            (0.0, 0.0),
            (1.0, 0.0),
        ),
        (
            (0.0, 0.0),
            (1.0, 0.0),
            (2.0, 0.0),
        ),
    ],
)
def test_resolver_rejects_invalid_or_degenerate_footprint(
    footprint,
):
    with pytest.raises(ValueError):
        AtlasChurchFootprintResolver.resolve(
            footprint
        )
