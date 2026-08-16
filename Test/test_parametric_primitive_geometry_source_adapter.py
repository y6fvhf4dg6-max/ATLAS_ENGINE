from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_parametric_primitive_geometry_source_adapter import (
    AtlasParametricPrimitiveGeometrySourceAdapter,
)


def test_parametric_primitive_adapter_normalizes_closed_cylinder_descriptor():
    source = {
        "primitive_type": " Closed Cylinder ",
        "parameters": {
            "center_x": 2,
            "center_y": 3,
            "base_z": 1,
            "radius": 1.5,
            "height": 4,
            "segments": 12,
        },
        "confidence": 0.98,
        "provenance": " Synthetic Primitive Fixture ",
        "supported_projection_modes": (
            " Flat Plane ",
        ),
    }

    result = (
        AtlasParametricPrimitiveGeometrySourceAdapter()
        .adapt(source)
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )

    assert result.normalized_geometry == {
        "geometry_kind": "parametric_primitive",
        "primitive_type": "closed_cylinder",
        "parameters": {
            "center_x": 2.0,
            "center_y": 3.0,
            "base_z": 1.0,
            "radius": 1.5,
            "height": 4.0,
            "segments": 12,
        },
    }

    assert result.local_bounds == (
        (0.5, 1.5, 1.0),
        (3.5, 4.5, 5.0),
    )

    assert dict(result.anchors) == {
        "base_center": (2.0, 3.0, 1.0),
        "top_center": (2.0, 3.0, 5.0),
    }

    assert result.confidence == 0.98
    assert result.provenance == (
        "Synthetic Primitive Fixture"
    )
    assert result.supported_projection_modes == (
        "flat_plane",
    )

    assert (
        "triangles"
        not in result.normalized_geometry
    )
    assert (
        "mesh"
        not in result.normalized_geometry
    )

import pytest


def _valid_source():
    return {
        "primitive_type": "closed_cylinder",
        "parameters": {
            "center_x": 0.0,
            "center_y": 0.0,
            "base_z": 0.0,
            "radius": 1.5,
            "height": 4.0,
            "segments": 12,
        },
        "confidence": 1.0,
        "provenance": "fixture",
        "supported_projection_modes": (
            "flat_plane",
        ),
    }


def test_parametric_primitive_adapter_rejects_unsupported_primitive():
    source = _valid_source()
    source["primitive_type"] = "sphere"

    with pytest.raises(
        ValueError,
        match="unsupported primitive_type",
    ):
        AtlasParametricPrimitiveGeometrySourceAdapter().adapt(
            source
        )


def test_parametric_primitive_adapter_requires_complete_mapping_source():
    adapter = AtlasParametricPrimitiveGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="source must be a mapping",
    ):
        adapter.adapt("closed_cylinder")

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        adapter.adapt(
            {
                "primitive_type": "closed_cylinder",
            }
        )


def test_parametric_primitive_adapter_requires_complete_parameter_mapping():
    source = _valid_source()
    del source["parameters"]["radius"]

    with pytest.raises(
        ValueError,
        match="parameters missing required fields",
    ):
        AtlasParametricPrimitiveGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("center_x", float("nan")),
        ("center_y", float("inf")),
        ("base_z", float("-inf")),
        ("radius", 0.0),
        ("radius", -1.0),
        ("radius", float("nan")),
        ("height", 0.0),
        ("height", -1.0),
        ("height", float("inf")),
    ),
)
def test_parametric_primitive_adapter_rejects_invalid_numeric_parameters(
    field_name,
    value,
):
    source = _valid_source()
    source["parameters"][field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasParametricPrimitiveGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    "segments",
    (
        5,
        0,
        -1,
        6.5,
        True,
    ),
)
def test_parametric_primitive_adapter_rejects_invalid_segments(
    segments,
):
    source = _valid_source()
    source["parameters"]["segments"] = segments

    with pytest.raises(
        ValueError,
        match="segments",
    ):
        AtlasParametricPrimitiveGeometrySourceAdapter().adapt(
            source
        )


def test_parametric_primitive_adapter_accepts_negative_origin_coordinates():
    source = _valid_source()
    source["parameters"].update(
        {
            "center_x": -3.0,
            "center_y": -5.0,
            "base_z": -2.0,
            "radius": 2.0,
            "height": 6.0,
        }
    )

    result = AtlasParametricPrimitiveGeometrySourceAdapter().adapt(
        source
    )

    assert result.local_bounds == (
        (-5.0, -7.0, -2.0),
        (-1.0, -3.0, 4.0),
    )

    assert dict(result.anchors) == {
        "base_center": (-3.0, -5.0, -2.0),
        "top_center": (-3.0, -5.0, 4.0),
    }
