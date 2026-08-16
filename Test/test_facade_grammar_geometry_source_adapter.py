from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_facade_grammar_geometry_source_adapter import (
    AtlasFacadeGrammarGeometrySourceAdapter,
)


def test_facade_grammar_adapter_normalizes_uniform_opening_grammar():
    source = {
        "grammar_type": " Uniform Openings ",
        "facade_width_mm": 12.0,
        "facade_height_mm": 8.0,
        "level_count": 2,
        "bay_count": 3,
        "opening_kind": " Window ",
        "horizontal_margin_ratio": 0.20,
        "vertical_margin_ratio": 0.20,
        "confidence": 0.96,
        "provenance": " Synthetic Facade Fixture ",
        "supported_projection_modes": (
            " Flat Plane ",
        ),
    }

    result = (
        AtlasFacadeGrammarGeometrySourceAdapter()
        .adapt(source)
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )

    assert result.normalized_geometry == {
        "geometry_kind": "facade_grammar",
        "grammar_type": "uniform_openings",
        "facade_width_mm": 12.0,
        "facade_height_mm": 8.0,
        "level_count": 2,
        "bay_count": 3,
        "opening_kind": "window",
        "horizontal_margin_ratio": 0.20,
        "vertical_margin_ratio": 0.20,
        "opening_count": 6,
    }

    assert result.local_bounds == (
        (0.0, 0.0, 0.0),
        (12.0, 0.0, 8.0),
    )

    assert dict(result.anchors) == {
        "bottom_left": (0.0, 0.0, 0.0),
        "bottom_center": (6.0, 0.0, 0.0),
        "top_center": (6.0, 0.0, 8.0),
    }

    assert result.confidence == 0.96
    assert result.provenance == (
        "Synthetic Facade Fixture"
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


def _valid_facade_source():
    return {
        "grammar_type": "uniform_openings",
        "facade_width_mm": 12.0,
        "facade_height_mm": 8.0,
        "level_count": 2,
        "bay_count": 3,
        "opening_kind": "window",
        "horizontal_margin_ratio": 0.20,
        "vertical_margin_ratio": 0.20,
        "confidence": 1.0,
        "provenance": "fixture",
        "supported_projection_modes": (
            "flat_plane",
        ),
    }


def test_facade_grammar_adapter_rejects_unsupported_grammar():
    source = _valid_facade_source()
    source["grammar_type"] = "freeform_facade"

    with pytest.raises(
        ValueError,
        match="unsupported grammar_type",
    ):
        AtlasFacadeGrammarGeometrySourceAdapter().adapt(
            source
        )


def test_facade_grammar_adapter_requires_complete_mapping_source():
    adapter = AtlasFacadeGrammarGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="source must be a mapping",
    ):
        adapter.adapt("uniform_openings")

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        adapter.adapt(
            {
                "grammar_type": "uniform_openings",
            }
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("facade_width_mm", 0.0),
        ("facade_width_mm", -1.0),
        ("facade_width_mm", float("nan")),
        ("facade_height_mm", 0.0),
        ("facade_height_mm", -1.0),
        ("facade_height_mm", float("inf")),
    ),
)
def test_facade_grammar_adapter_rejects_invalid_facade_dimensions(
    field_name,
    value,
):
    source = _valid_facade_source()
    source[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasFacadeGrammarGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("level_count", 0),
        ("level_count", -1),
        ("level_count", 1.5),
        ("level_count", True),
        ("bay_count", 0),
        ("bay_count", -1),
        ("bay_count", 2.5),
        ("bay_count", False),
    ),
)
def test_facade_grammar_adapter_rejects_invalid_counts(
    field_name,
    value,
):
    source = _valid_facade_source()
    source[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasFacadeGrammarGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("horizontal_margin_ratio", -0.01),
        ("horizontal_margin_ratio", 0.50),
        ("horizontal_margin_ratio", float("nan")),
        ("vertical_margin_ratio", -0.01),
        ("vertical_margin_ratio", 0.50),
        ("vertical_margin_ratio", float("inf")),
    ),
)
def test_facade_grammar_adapter_rejects_invalid_margin_ratios(
    field_name,
    value,
):
    source = _valid_facade_source()
    source[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasFacadeGrammarGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("grammar_type", ""),
        ("grammar_type", "   "),
        ("opening_kind", ""),
        ("opening_kind", "   "),
    ),
)
def test_facade_grammar_adapter_rejects_blank_identifiers(
    field_name,
    value,
):
    source = _valid_facade_source()
    source[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasFacadeGrammarGeometrySourceAdapter().adapt(
            source
        )


def test_facade_grammar_adapter_opening_count_is_deterministic():
    source = _valid_facade_source()
    source["level_count"] = 4
    source["bay_count"] = 5

    result = AtlasFacadeGrammarGeometrySourceAdapter().adapt(
        source
    )

    assert result.normalized_geometry[
        "opening_count"
    ] == 20
