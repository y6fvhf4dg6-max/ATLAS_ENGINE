from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_semantic_relief_transform import (
    AtlasSemanticReliefTransform,
)


def test_semantic_relief_transform_normalizes_physical_values():
    transform = AtlasSemanticReliefTransform(
        translation_mm=(1, 2.5, -3),
        rotation_degrees_xyz=(0, 90, 180),
        dimensions_mm=(12, 24.5, 3),
    )

    assert transform.translation_mm == (1.0, 2.5, -3.0)
    assert transform.rotation_degrees_xyz == (0.0, 90.0, 180.0)
    assert transform.dimensions_mm == (12.0, 24.5, 3.0)

    with pytest.raises(FrozenInstanceError):
        transform.translation_mm = (0.0, 0.0, 0.0)

@pytest.mark.parametrize(
    "dimensions_mm",
    (
        (0.0, 10.0, 2.0),
        (10.0, -1.0, 2.0),
    ),
)
def test_semantic_relief_transform_rejects_nonpositive_dimensions(
    dimensions_mm,
):
    with pytest.raises(ValueError, match="dimensions_mm"):
        AtlasSemanticReliefTransform(
            translation_mm=(0.0, 0.0, 0.0),
            rotation_degrees_xyz=(0.0, 0.0, 0.0),
            dimensions_mm=dimensions_mm,
        )

def test_semantic_relief_transform_normalizes_coordinate_space():
    surface_transform = AtlasSemanticReliefTransform(
        translation_mm=(4.0, 12.0, 1.2),
        rotation_degrees_xyz=(0.0, 0.0, 15.0),
        dimensions_mm=(12.0, 24.5, 3.0),
        coordinate_space=" Target Surface Local ",
    )
    default_transform = AtlasSemanticReliefTransform(
        translation_mm=(0.0, 0.0, 0.0),
        rotation_degrees_xyz=(0.0, 0.0, 0.0),
        dimensions_mm=(1.0, 1.0, 1.0),
    )

    assert surface_transform.coordinate_space == "target_surface_local"
    assert default_transform.coordinate_space == "component_local"

@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("translation_mm", (0.0, 0.0)),
        ("rotation_degrees_xyz", (0.0, float("nan"), 0.0)),
        ("dimensions_mm", "12,24,3"),
    ),
)
def test_semantic_relief_transform_rejects_malformed_physical_triplets(
    field_name,
    invalid_value,
):
    kwargs = {
        "translation_mm": (0.0, 0.0, 0.0),
        "rotation_degrees_xyz": (0.0, 0.0, 0.0),
        "dimensions_mm": (12.0, 24.0, 3.0),
    }
    kwargs[field_name] = invalid_value

    with pytest.raises(ValueError, match=field_name):
        AtlasSemanticReliefTransform(**kwargs)
