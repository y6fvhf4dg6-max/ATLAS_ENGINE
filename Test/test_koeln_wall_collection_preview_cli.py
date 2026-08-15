import pytest

from Test.preview_koeln_paedagogische_fakultaet_wall_collection import (
    CITY_SIZE_MM,
    FRAME_WIDTH_MM,
    HIGHLIGHTED_BUILDING_SOURCE_IDS,
    PRODUCT_OUTER_SIZE_MM,
    SCALE_RATIO,
    build_parser,
)


def test_preview_allows_product_without_label():
    parser = build_parser()

    arguments = parser.parse_args([])

    assert arguments.primary_text == ""
    assert arguments.secondary_text == ""


def test_preview_accepts_customer_label_text():
    parser = build_parser()

    arguments = parser.parse_args(
        [
            "--primary-text",
            "MEIN STUDIENORT",
            "--secondary-text",
            "KÖLN · 1998–2002",
        ]
    )

    assert arguments.primary_text == "MEIN STUDIENORT"
    assert arguments.secondary_text == "KÖLN · 1998–2002"


def test_preview_secondary_text_is_optional():
    parser = build_parser()

    arguments = parser.parse_args(
        [
            "--primary-text",
            "UNIVERSITÄT ZU KÖLN",
        ]
    )

    assert arguments.primary_text == "UNIVERSITÄT ZU KÖLN"
    assert arguments.secondary_text == ""


def test_preview_rejects_secondary_text_without_primary_text():
    parser = build_parser()

    arguments = parser.parse_args(
        [
            "--secondary-text",
            "KÖLN",
        ]
    )

    with pytest.raises(
        ValueError,
        match="secondary text requires primary text",
    ):
        arguments.validate_label_text()


def test_koeln_production_uses_current_physical_contract():
    assert PRODUCT_OUTER_SIZE_MM == 170.0
    assert CITY_SIZE_MM == 150.0
    assert FRAME_WIDTH_MM == 10.0
    assert SCALE_RATIO == 3000.0


def test_koeln_production_does_not_color_entire_faculty_building_red():
    assert HIGHLIGHTED_BUILDING_SOURCE_IDS == frozenset()
