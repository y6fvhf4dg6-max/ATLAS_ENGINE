from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_catalog_component_geometry_source_adapter import (
    AtlasCatalogComponentGeometrySourceAdapter,
)


def test_catalog_component_adapter_normalizes_master_catalog_component_reference():
    source = {
        "wikidata_id": " q81523 ",
        "component_role": " Supports ",
        "component_geometry_kind": " Parametric Primitive ",
        "instance_index": 0,
        "local_bounds": (
            (-2.0, -1.0, 0.0),
            (2.0, 1.0, 6.0),
        ),
        "anchors": {
            " Base Center ": (0.0, 0.0, 0.0),
            " Top Center ": (0.0, 0.0, 6.0),
        },
        "confidence": 0.97,
        "provenance": " Master Landmark Catalog Fixture ",
        "supported_projection_modes": (
            " Flat Plane ",
        ),
    }

    result = (
        AtlasCatalogComponentGeometrySourceAdapter()
        .adapt(source)
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )

    assert result.normalized_geometry == {
        "geometry_kind": "catalog_component",
        "catalog_key": "galata-bridge",
        "landmark_family": "bridge",
        "wikidata_id": "Q81523",
        "osm_ids": (),
        "grammar_name": None,
        "profile_name": "galata",
        "component_flags": (
            "supports",
            "parapets",
        ),
        "geometry_overrides": (),
        "component_role": "supports",
        "component_geometry_kind": (
            "parametric_primitive"
        ),
        "instance_index": 0,
    }

    assert result.local_bounds == (
        (-2.0, -1.0, 0.0),
        (2.0, 1.0, 6.0),
    )

    assert dict(result.anchors) == {
        "base_center": (0.0, 0.0, 0.0),
        "top_center": (0.0, 0.0, 6.0),
    }

    assert result.confidence == 0.97
    assert result.provenance == (
        "Master Landmark Catalog Fixture"
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


def _valid_catalog_component_source():
    return {
        "wikidata_id": "Q81523",
        "component_role": "supports",
        "component_geometry_kind": "parametric_primitive",
        "instance_index": 0,
        "local_bounds": (
            (-2.0, -1.0, 0.0),
            (2.0, 1.0, 6.0),
        ),
        "anchors": {
            "base_center": (0.0, 0.0, 0.0),
            "top_center": (0.0, 0.0, 6.0),
        },
        "confidence": 1.0,
        "provenance": "fixture",
        "supported_projection_modes": (
            "flat_plane",
        ),
    }


def test_catalog_component_adapter_requires_complete_mapping_source():
    adapter = AtlasCatalogComponentGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="source must be a mapping",
    ):
        adapter.adapt("Q81523")

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        adapter.adapt(
            {
                "wikidata_id": "Q81523",
            }
        )


def test_catalog_component_adapter_rejects_unresolved_catalog_entry():
    source = _valid_catalog_component_source()
    source["wikidata_id"] = "Q999999999999"

    with pytest.raises(
        ValueError,
        match="catalog entry could not be resolved",
    ):
        AtlasCatalogComponentGeometrySourceAdapter().adapt(
            source
        )


def test_catalog_component_adapter_can_resolve_by_osm_id():
    source = _valid_catalog_component_source()
    del source["wikidata_id"]
    source["osm_id"] = 165574748
    source["component_role"] = "main_dome"

    result = AtlasCatalogComponentGeometrySourceAdapter().adapt(
        source
    )

    assert result.normalized_geometry[
        "catalog_key"
    ] == "kilic-ali-pasha-mosque"

    assert result.normalized_geometry[
        "landmark_family"
    ] == "mosque"

    assert result.normalized_geometry[
        "grammar_name"
    ] == "single_dome_single_minaret"


def test_catalog_component_adapter_rejects_role_not_declared_by_flagged_entry():
    source = _valid_catalog_component_source()
    source["component_role"] = "tower"

    with pytest.raises(
        ValueError,
        match="component_role is not declared",
    ):
        AtlasCatalogComponentGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    "instance_index",
    (
        -1,
        1.5,
        True,
        "1",
    ),
)
def test_catalog_component_adapter_rejects_invalid_instance_index(
    instance_index,
):
    source = _valid_catalog_component_source()
    source["instance_index"] = instance_index

    with pytest.raises(
        ValueError,
        match="instance_index",
    ):
        AtlasCatalogComponentGeometrySourceAdapter().adapt(
            source
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("component_role", ""),
        ("component_role", "   "),
        ("component_geometry_kind", ""),
        ("component_geometry_kind", "   "),
    ),
)
def test_catalog_component_adapter_rejects_blank_identifiers(
    field_name,
    value,
):
    source = _valid_catalog_component_source()
    source[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasCatalogComponentGeometrySourceAdapter().adapt(
            source
        )


def test_catalog_component_adapter_keeps_explicit_geometry_metadata_separate_from_catalog_metadata():
    source = _valid_catalog_component_source()

    result = AtlasCatalogComponentGeometrySourceAdapter().adapt(
        source
    )

    assert result.local_bounds == (
        (-2.0, -1.0, 0.0),
        (2.0, 1.0, 6.0),
    )
    assert "local_bounds" not in result.normalized_geometry
    assert "anchors" not in result.normalized_geometry
