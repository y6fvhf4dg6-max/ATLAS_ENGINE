import pytest

from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec


def test_default_label_plate_defines_integrated_personalization_surface():
    spec = AtlasLabelPlateSpec()

    assert spec.width_mm == pytest.approx(118.0)
    assert spec.height_mm == pytest.approx(14.0)
    assert spec.depth_mm == pytest.approx(1.2)


@pytest.mark.parametrize(
    "field_name",
    (
        "width_mm",
        "height_mm",
        "depth_mm",
    ),
)
def test_label_plate_rejects_non_positive_dimensions(field_name):
    values = {
        "width_mm": 118.0,
        "height_mm": 14.0,
        "depth_mm": 1.2,
    }
    values[field_name] = 0.0

    with pytest.raises(ValueError):
        AtlasLabelPlateSpec(**values)
