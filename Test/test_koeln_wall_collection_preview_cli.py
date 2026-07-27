import pytest

from Test.preview_koeln_paedagogische_fakultaet_wall_collection import (
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
