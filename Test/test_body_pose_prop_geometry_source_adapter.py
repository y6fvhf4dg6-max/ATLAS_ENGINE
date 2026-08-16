from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)
from CORE.atlas_body_pose_prop_geometry_source_adapter import (
    AtlasBodyPosePropGeometrySourceAdapter,
)


def test_body_pose_prop_adapter_normalizes_existing_figurative_semantic_reference():
    component = AtlasSemanticReliefComponent(
        component_id="Guardian Figure",
        semantic_class="Figurative Sculpture",
        geometry_source_kind="Catalog Component",
        source_reference="guardian-figure-fixture",
        output_modes=(
            "Relief",
            "Assembled Landmark",
        ),
        provenance="synthetic figurative fixture",
        confidence=0.92,
    )

    source = {
        "component": component,
        "local_bounds": (
            (-10.0, -3.0, 0.0),
            (10.0, 3.0, 42.0),
        ),
        "anchors": {
            "Root": (0.0, 0.0, 0.0),
            "Head": (0.0, 0.0, 38.0),
        },
        "supported_projection_modes": (
            "Flat Plane",
        ),
    }

    result = (
        AtlasBodyPosePropGeometrySourceAdapter()
        .adapt(source)
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )

    assert result.normalized_geometry == {
        "geometry_kind": (
            "body_pose_prop_semantic_reference"
        ),
        "descriptor_status": (
            "semantic_reference_only"
        ),
        "component_id": "guardian_figure",
        "semantic_class": (
            "figurative_sculpture"
        ),
        "declared_geometry_source_kind": (
            "catalog_component"
        ),
        "source_reference": (
            "guardian-figure-fixture"
        ),
        "output_modes": (
            "relief",
            "assembled_landmark",
        ),
        "material_role": "unassigned",
        "physical_feature_policy": "preserve",
    }

    assert result.local_bounds == (
        (-10.0, -3.0, 0.0),
        (10.0, 3.0, 42.0),
    )

    assert dict(result.anchors) == {
        "root": (0.0, 0.0, 0.0),
        "head": (0.0, 0.0, 38.0),
    }

    assert result.confidence == 0.92
    assert result.provenance == (
        "synthetic figurative fixture"
    )

    assert result.supported_projection_modes == (
        "flat_plane",
    )

    geometry = result.normalized_geometry

    assert "skeleton" not in geometry
    assert "joints" not in geometry
    assert "pose" not in geometry
    assert "props" not in geometry
    assert "mesh" not in geometry
    assert "triangles" not in geometry

import pytest


def _figurative_component(
    *,
    semantic_class="Figurative Sculpture",
    confidence=0.88,
    provenance="figurative fixture",
):
    return AtlasSemanticReliefComponent(
        component_id="Guardian Figure",
        semantic_class=semantic_class,
        geometry_source_kind="Catalog Component",
        source_reference="guardian-figure-fixture",
        output_modes=(
            "Relief",
            "Assembled Landmark",
        ),
        provenance=provenance,
        confidence=confidence,
    )


def _valid_source():
    return {
        "component": _figurative_component(),
        "local_bounds": (
            (-8.0, -2.0, 0.0),
            (8.0, 2.0, 36.0),
        ),
        "anchors": {
            "root": (0.0, 0.0, 0.0),
            "head": (0.0, 0.0, 32.0),
        },
        "supported_projection_modes": (
            "flat_plane",
        ),
    }


def test_body_pose_prop_adapter_requires_mapping_source():
    with pytest.raises(
        TypeError,
        match="source must be a mapping",
    ):
        AtlasBodyPosePropGeometrySourceAdapter().adapt(
            _figurative_component()
        )


def test_body_pose_prop_adapter_requires_complete_source():
    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        AtlasBodyPosePropGeometrySourceAdapter().adapt(
            {
                "component": _figurative_component(),
            }
        )


def test_body_pose_prop_adapter_requires_semantic_relief_component():
    source = _valid_source()
    source["component"] = {
        "semantic_class": "figurative_sculpture",
    }

    with pytest.raises(
        TypeError,
        match="AtlasSemanticReliefComponent",
    ):
        AtlasBodyPosePropGeometrySourceAdapter().adapt(
            source
        )


def test_body_pose_prop_adapter_rejects_non_figurative_component():
    source = _valid_source()
    source["component"] = _figurative_component(
        semantic_class="Architecture",
    )

    with pytest.raises(
        ValueError,
        match="semantic_class must be figurative",
    ):
        AtlasBodyPosePropGeometrySourceAdapter().adapt(
            source
        )


def test_body_pose_prop_adapter_accepts_figurative_ornament():
    source = _valid_source()
    source["component"] = _figurative_component(
        semantic_class="Figurative Ornament",
    )

    result = AtlasBodyPosePropGeometrySourceAdapter().adapt(
        source
    )

    assert result.normalized_geometry[
        "semantic_class"
    ] == "figurative_ornament"


def test_body_pose_prop_adapter_preserves_explicit_geometry_metadata():
    result = AtlasBodyPosePropGeometrySourceAdapter().adapt(
        _valid_source()
    )

    assert result.local_bounds == (
        (-8.0, -2.0, 0.0),
        (8.0, 2.0, 36.0),
    )

    assert dict(result.anchors) == {
        "root": (0.0, 0.0, 0.0),
        "head": (0.0, 0.0, 32.0),
    }


def test_body_pose_prop_adapter_preserves_component_confidence_and_provenance():
    source = _valid_source()
    source["component"] = _figurative_component(
        confidence=0.73,
        provenance="catalog figurative fixture",
    )

    result = AtlasBodyPosePropGeometrySourceAdapter().adapt(
        source
    )

    assert result.confidence == 0.73
    assert result.provenance == (
        "catalog figurative fixture"
    )


def test_body_pose_prop_adapter_projection_mode_fails_early_when_unsupported():
    result = AtlasBodyPosePropGeometrySourceAdapter().adapt(
        _valid_source()
    )

    assert (
        result.require_projection_mode(
            "Flat Plane"
        )
        == "flat_plane"
    )

    with pytest.raises(
        ValueError,
        match="projection mode",
    ):
        result.require_projection_mode(
            "surface_wrap"
        )


def test_body_pose_prop_adapter_does_not_invent_future_body_geometry():
    result = AtlasBodyPosePropGeometrySourceAdapter().adapt(
        _valid_source()
    )

    geometry = result.normalized_geometry

    assert geometry[
        "descriptor_status"
    ] == "semantic_reference_only"

    for field_name in (
        "skeleton",
        "joints",
        "bones",
        "pose",
        "props",
        "vertices",
        "faces",
        "triangles",
        "mesh",
    ):
        assert field_name not in geometry
