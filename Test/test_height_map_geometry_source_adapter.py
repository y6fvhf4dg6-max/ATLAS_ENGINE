import numpy as np
import pytest

from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_height_map_geometry_source_adapter import (
    AtlasHeightMapGeometrySourceAdapter,
)


def test_height_map_adapter_returns_canonical_geometry_source_result():
    height_map = np.array(
        [
            [0.0, 0.5, 1.0],
            [0.25, 0.75, 0.5],
        ],
        dtype=np.float64,
    )

    source = {
        "height_map": height_map,
        "width_mm": 8.0,
        "depth_mm": 4.0,
        "relief_height_mm": 2.4,
        "confidence": 0.95,
        "provenance": " Synthetic Height Fixture ",
    }

    result = AtlasHeightMapGeometrySourceAdapter().adapt(
        source
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )

    assert result.normalized_geometry == {
        "geometry_kind": "height_map_relief",
        "height_map": (
            (0.0, 0.5, 1.0),
            (0.25, 0.75, 0.5),
        ),
        "row_count": 2,
        "column_count": 3,
        "width_mm": 8.0,
        "depth_mm": 4.0,
        "relief_height_mm": 2.4,
    }

    assert result.local_bounds == (
        (0.0, 0.0, 0.0),
        (8.0, 4.0, 2.4),
    )

    assert dict(result.anchors) == {
        "origin": (0.0, 0.0, 0.0),
    }

    assert result.confidence == 0.95
    assert result.provenance == (
        "Synthetic Height Fixture"
    )
    assert result.supported_projection_modes == (
        "flat_plane",
    )

    assert "mesh" not in result.normalized_geometry
    assert "triangles" not in result.normalized_geometry


def test_height_map_adapter_isolates_mutable_height_map_input():
    height_map = np.array(
        [
            [0.0, 0.5],
            [1.0, 0.25],
        ],
        dtype=np.float64,
    )

    source = {
        "height_map": height_map,
        "width_mm": 4.0,
        "depth_mm": 4.0,
        "relief_height_mm": 2.0,
        "confidence": 1.0,
        "provenance": "fixture",
    }

    result = AtlasHeightMapGeometrySourceAdapter().adapt(
        source
    )

    height_map[0, 0] = 99.0
    source["width_mm"] = 99.0

    assert result.normalized_geometry["height_map"] == (
        (0.0, 0.5),
        (1.0, 0.25),
    )
    assert result.normalized_geometry["width_mm"] == 4.0


@pytest.mark.parametrize(
    "height_map",
    (
        [0.0, 1.0],
        [[0.0]],
        np.zeros((2, 2, 2), dtype=np.float64),
        [
            [0.0, float("nan")],
            [0.5, 1.0],
        ],
        [
            [-0.01, 0.0],
            [0.5, 1.0],
        ],
        [
            [0.0, 1.01],
            [0.5, 1.0],
        ],
    ),
)
def test_height_map_adapter_rejects_invalid_height_map(
    height_map,
):
    source = {
        "height_map": height_map,
        "width_mm": 4.0,
        "depth_mm": 4.0,
        "relief_height_mm": 2.0,
        "confidence": 1.0,
        "provenance": "fixture",
    }

    with pytest.raises(
        ValueError,
        match="height_map",
    ):
        AtlasHeightMapGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("width_mm", 0.0),
        ("width_mm", -1.0),
        ("width_mm", float("nan")),
        ("depth_mm", 0.0),
        ("depth_mm", -1.0),
        ("depth_mm", float("inf")),
        ("relief_height_mm", -0.1),
        ("relief_height_mm", float("nan")),
    ),
)
def test_height_map_adapter_rejects_invalid_physical_dimensions(
    field_name,
    value,
):
    source = {
        "height_map": np.zeros(
            (2, 2),
            dtype=np.float64,
        ),
        "width_mm": 4.0,
        "depth_mm": 4.0,
        "relief_height_mm": 2.0,
        "confidence": 1.0,
        "provenance": "fixture",
    }
    source[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasHeightMapGeometrySourceAdapter().adapt(
            source
        )


def test_height_map_adapter_requires_complete_mapping_source():
    adapter = AtlasHeightMapGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="source must be a mapping",
    ):
        adapter.adapt(
            np.zeros((2, 2))
        )

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        adapter.adapt(
            {
                "height_map": np.zeros(
                    (2, 2),
                    dtype=np.float64,
                ),
            }
        )
