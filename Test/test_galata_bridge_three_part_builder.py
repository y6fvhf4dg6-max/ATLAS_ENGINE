import pytest

from CORE.atlas_galata_bridge_three_part_builder import (
    AtlasGalataBridgeThreePartBuilder,
)


def _build():
    return AtlasGalataBridgeThreePartBuilder.build(
        center=(0.0, 0.0),
        axis=(1.0, 0.0),
        total_span_mm=153.524,
        deck_width_mm=14.350,
        center_section_ratio=0.30,
        foundation_z=0.0,
        center_deck_bottom_z=3.0,
        deck_thickness_mm=0.80,
    )


def test_bridge_contains_left_center_and_right_sections():
    result = _build()

    assert tuple(result["sections"]) == (
        "left",
        "center",
        "right",
    )

    assert result["left"]["storey_count"] == 2
    assert result["center"]["storey_count"] == 1
    assert result["right"]["storey_count"] == 2


def test_center_section_remains_open_below_deck():
    result = _build()

    center = result["center"]

    assert center["has_lower_storey"] is False
    assert center["clearance_height_mm"] == pytest.approx(3.0)
    assert len(center["supports"]) == 2


def test_left_and_right_sections_have_lower_storeys():
    result = _build()

    for side in ("left", "right"):
        section = result[side]

        assert section["has_lower_storey"] is True
        assert section["storey_count"] == 2
        assert "lower_storey" in section
        assert "upper_deck" in section


def test_side_inner_edges_connect_to_center_deck():
    result = _build()

    center_top_z = result["center"]["deck"]["top_z"]

    assert result["left"]["inner_top_z"] == pytest.approx(
        center_top_z
    )
    assert result["right"]["inner_top_z"] == pytest.approx(
        center_top_z
    )


def test_side_outer_ends_touch_foundation():
    result = _build()

    assert result["left"]["outer_bottom_z"] == pytest.approx(0.0)
    assert result["right"]["outer_bottom_z"] == pytest.approx(0.0)

    assert result["left"]["outer_touches_foundation"] is True
    assert result["right"]["outer_touches_foundation"] is True


def test_side_decks_rise_toward_center():
    result = _build()

    for side in ("left", "right"):
        section = result[side]

        assert section["inner_top_z"] > section["outer_top_z"]
        assert section["inner_bottom_z"] > section["outer_bottom_z"]


def test_full_bridge_preserves_requested_span():
    result = _build()

    assert result["total_span_mm"] == pytest.approx(153.524)

    section_length_sum = (
        result["left"]["length_mm"]
        + result["center"]["length_mm"]
        + result["right"]["length_mm"]
    )

    assert section_length_sum == pytest.approx(153.524)


def test_full_bridge_exposes_printable_meshes():
    result = _build()

    meshes = result["meshes"]

    assert meshes
    assert all(
        len(mesh["triangles"]) > 0
        for mesh in meshes
    )


def test_side_upper_decks_do_not_overlap_lower_storeys():
    result = _build()

    for side in ("left", "right"):
        section = result[side]
        lower_storey = section["lower_storey"]
        upper_deck = section["upper_deck"]

        lower_outer_top_z = {
            round(point[2], 9)
            for point in (
                lower_storey["top"][0],
                lower_storey["top"][3],
            )
        }
        upper_outer_bottom_z = {
            round(point[2], 9)
            for point in (
                upper_deck["bottom"][0],
                upper_deck["bottom"][3],
            )
        }

        assert len(lower_outer_top_z) == 1
        assert len(upper_outer_bottom_z) == 1

        assert next(iter(upper_outer_bottom_z)) == pytest.approx(
            next(iter(lower_outer_top_z))
        )

        lower_inner_top_z = {
            round(point[2], 9)
            for point in (
                lower_storey["top"][1],
                lower_storey["top"][2],
            )
        }
        upper_inner_bottom_z = {
            round(point[2], 9)
            for point in (
                upper_deck["bottom"][1],
                upper_deck["bottom"][2],
            )
        }

        assert max(lower_inner_top_z) < min(
            upper_inner_bottom_z
        )


def test_bridge_can_extend_only_left_side_without_moving_center():
    base = AtlasGalataBridgeThreePartBuilder.build(
        center=(0.0, 0.0),
        axis=(1.0, 0.0),
        total_span_mm=83.740309,
        deck_width_mm=7.827,
        center_section_ratio=0.30,
        foundation_z=0.0,
        center_deck_bottom_z=3.0,
        deck_thickness_mm=0.80,
    )

    extended = AtlasGalataBridgeThreePartBuilder.build(
        center=(0.0, 0.0),
        axis=(1.0, 0.0),
        total_span_mm=83.740309,
        deck_width_mm=7.827,
        center_section_ratio=0.30,
        foundation_z=0.0,
        center_deck_bottom_z=3.0,
        deck_thickness_mm=0.80,
        left_extension_mm=3.561365,
        right_extension_mm=0.0,
    )

    assert extended["left"]["length_mm"] == pytest.approx(
        base["left"]["length_mm"] + 3.561365
    )
    assert extended["right"]["length_mm"] == pytest.approx(
        base["right"]["length_mm"]
    )

    assert extended["center"]["center"] == pytest.approx(
        base["center"]["center"]
    )

    assert extended["center"]["length_mm"] == pytest.approx(
        base["center"]["length_mm"]
    )

    assert extended["total_span_mm"] == pytest.approx(
        83.740309 + 3.561365
    )
