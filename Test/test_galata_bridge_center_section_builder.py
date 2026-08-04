import pytest

from CORE.atlas_galata_bridge_center_section_builder import (
    AtlasGalataBridgeCenterSectionBuilder,
)


def _build_center_section():
    return AtlasGalataBridgeCenterSectionBuilder.build(
        center=(206.698, 201.364),
        axis=(0.48342449, 0.87538607),
        total_span_mm=153.524,
        deck_width_mm=14.350,
        center_section_ratio=0.30,
        foundation_z=0.0,
        deck_bottom_z=3.0,
        deck_thickness_mm=0.80,
    )


def _vertices(mesh):
    return [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]


def test_center_section_is_single_level_bridge_deck():
    result = _build_center_section()

    deck = result["deck"]

    assert deck["type"] == (
        "galata_bridge_center_deck"
    )
    assert deck["length_mm"] == pytest.approx(
        153.524 * 0.30
    )
    assert deck["width_mm"] == pytest.approx(
        14.350
    )
    assert deck["bottom_z"] == pytest.approx(
        3.0
    )
    assert deck["top_z"] == pytest.approx(
        3.8
    )
    assert len(deck["triangles"]) == 12


def test_center_section_has_no_lower_storey():
    result = _build_center_section()

    assert result["storey_count"] == 1
    assert result["has_lower_storey"] is False
    assert "lower_storey" not in result
    assert "restaurant_level" not in result


def test_center_section_keeps_open_space_below_deck():
    result = _build_center_section()

    assert result["clearance_bottom_z"] == (
        pytest.approx(0.0)
    )
    assert result["clearance_top_z"] == (
        pytest.approx(3.0)
    )
    assert result["clearance_height_mm"] == (
        pytest.approx(3.0)
    )


def test_center_section_has_two_transverse_support_piers():
    result = _build_center_section()

    supports = result["supports"]

    assert len(supports) == 2

    positions = [
        support["longitudinal_position"]
        for support in supports
    ]

    assert positions == pytest.approx(
        [0.12, 0.88]
    )

    assert positions[1] - positions[0] >= 0.70

    for support in supports:
        assert support["type"] == (
            "galata_bridge_flared_support"
        )

        assert support["width_mm"] > (
            result["width_mm"]
        )

        assert support["width_mm"] == pytest.approx(
            result["width_mm"] * 1.35
        )

        assert support["length_mm"] == pytest.approx(
            4.0
        )

        assert support["lateral_offset_mm"] == (
            pytest.approx(0.0)
        )

        assert support["extends_beyond_deck"] is True
        assert support["footprint_shape"] == (
            "double_wedge_flared_platform"
        )

        assert len(support["footprint"]) == 6
        assert len(support["triangles"]) == 20


def test_supports_connect_foundation_to_deck_bottom():
    result = _build_center_section()

    for support in result["supports"]:
        assert support["bottom_z"] == (
            pytest.approx(0.0)
        )
        assert support["top_z"] == (
            pytest.approx(3.15)
        )
        assert len(
            support["triangles"]
        ) == 20


def test_supports_remain_below_deck_width():
    result = _build_center_section()

    deck_vertices = _vertices(
        result["deck"]
    )

    deck_min_x = min(
        point[0]
        for point in deck_vertices
    )
    deck_max_x = max(
        point[0]
        for point in deck_vertices
    )
    deck_min_y = min(
        point[1]
        for point in deck_vertices
    )
    deck_max_y = max(
        point[1]
        for point in deck_vertices
    )

    for support in result["supports"]:
        support_vertices = _vertices(
            support
        )

        assert min(
            point[0]
            for point in support_vertices
        ) >= deck_min_x - 1e-9

        assert max(
            point[0]
            for point in support_vertices
        ) <= deck_max_x + 1e-9

        assert min(
            point[1]
            for point in support_vertices
        ) >= deck_min_y - 1e-9

        assert max(
            point[1]
            for point in support_vertices
        ) <= deck_max_y + 1e-9


def test_center_section_exposes_left_and_right_connection_edges():
    result = _build_center_section()

    assert len(
        result["left_connection_edge"]
    ) == 2
    assert len(
        result["right_connection_edge"]
    ) == 2

    assert (
        result["left_connection_edge"]
        != result["right_connection_edge"]
    )


def test_center_section_rejects_zero_axis():
    with pytest.raises(ValueError):
        AtlasGalataBridgeCenterSectionBuilder.build(
            center=(0.0, 0.0),
            axis=(0.0, 0.0),
            total_span_mm=153.524,
            deck_width_mm=14.350,
            center_section_ratio=0.30,
            foundation_z=0.0,
            deck_bottom_z=3.0,
            deck_thickness_mm=0.80,
        )
