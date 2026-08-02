import pytest

from CORE.atlas_label_text_spec import AtlasLabelTextSpec


def test_label_text_spec_defines_two_line_koeln_graduation_label():
    spec = AtlasLabelTextSpec(
        primary_text="KÖLN ÜNİVERSİTESİ",
        secondary_text="MEZUNİYET",
    )

    assert spec.primary_text == "KÖLN ÜNİVERSİTESİ"
    assert spec.secondary_text == "MEZUNİYET"
    assert spec.primary_height_mm == pytest.approx(4.2)
    assert spec.secondary_height_mm == pytest.approx(2.8)
    assert spec.depth_mm == pytest.approx(0.6)
    assert spec.max_width_mm == pytest.approx(108.0)


@pytest.mark.parametrize(
    "field_name",
    (
        "primary_height_mm",
        "secondary_height_mm",
        "depth_mm",
        "max_width_mm",
    ),
)
def test_label_text_spec_rejects_non_positive_dimensions(field_name):
    values = {
        "primary_text": "KÖLN ÜNİVERSİTESİ",
        "secondary_text": "MEZUNİYET",
        "primary_height_mm": 4.2,
        "secondary_height_mm": 2.8,
        "depth_mm": 0.6,
        "max_width_mm": 108.0,
    }
    values[field_name] = 0.0

    with pytest.raises(ValueError):
        AtlasLabelTextSpec(**values)


def test_label_text_spec_rejects_empty_primary_text():
    with pytest.raises(ValueError):
        AtlasLabelTextSpec(
            primary_text="   ",
            secondary_text="MEZUNİYET",
        )



def test_label_text_spec_disables_graduation_cap_by_default():
    spec = AtlasLabelTextSpec(
        primary_text="KÖLN",
        secondary_text="2001",
    )

    assert spec.graduation_cap is False


def test_label_text_spec_can_enable_graduation_cap():
    spec = AtlasLabelTextSpec(
        primary_text="KÖLN ÜNİVERSİTESİ",
        secondary_text="MEZUNİYET",
        graduation_cap=True,
    )

    assert spec.graduation_cap is True


def test_label_text_spec_disables_birthday_cake_by_default():
    spec = AtlasLabelTextSpec(
        primary_text="BONN",
    )

    assert spec.birthday_cake is False


def test_label_text_spec_can_enable_birthday_cake():
    spec = AtlasLabelTextSpec(
        primary_text="BONN",
        secondary_text="GEBURTSORT",
        birthday_cake=True,
    )

    assert spec.birthday_cake is True


def test_label_text_spec_can_enable_home_symbol():
    spec = AtlasLabelTextSpec(
        primary_text="ERKELENZ",
        secondary_text="ZUHAUSE",
        home=True,
    )

    assert spec.home is True
    assert spec.graduation_cap is False
    assert spec.birthday_cake is False
