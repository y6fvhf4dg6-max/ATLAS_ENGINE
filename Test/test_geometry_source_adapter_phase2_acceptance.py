import pytest

from CORE.atlas_geometry_source_adapter import (
    AtlasGeometrySourceAdapter,
)
from CORE.atlas_height_map_geometry_source_adapter import (
    AtlasHeightMapGeometrySourceAdapter,
)
from CORE.atlas_parametric_primitive_geometry_source_adapter import (
    AtlasParametricPrimitiveGeometrySourceAdapter,
)
from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)
from CORE.atlas_semantic_relief_scene import (
    AtlasSemanticReliefScene,
)


def _scene():
    return AtlasSemanticReliefScene(
        scene_id="Phase 2 Adapter Acceptance",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Primary Form",
                semantic_class="Architecture",
                geometry_source_kind="External Adapter",
                provenance="phase2 acceptance fixture",
            ),
        ),
    )


def test_same_semantic_scene_can_use_different_geometry_source_adapters():
    scene = _scene()

    component = scene.component_for_id(
        "Primary Form"
    )

    height_map_result = (
        AtlasHeightMapGeometrySourceAdapter()
        .adapt(
            {
                "height_map": (
                    (0.0, 0.5),
                    (0.5, 1.0),
                ),
                "width_mm": 20.0,
                "depth_mm": 10.0,
                "relief_height_mm": 3.0,
                "confidence": 1.0,
                "provenance": "height-map fixture",
            }
        )
    )

    primitive_result = (
        AtlasParametricPrimitiveGeometrySourceAdapter()
        .adapt(
            {
                "primitive_type": "closed_cylinder",
                "parameters": {
                    "center_x": 0.0,
                    "center_y": 0.0,
                    "base_z": 0.0,
                    "radius": 5.0,
                    "height": 12.0,
                    "segments": 12,
                },
                "confidence": 1.0,
                "provenance": "primitive fixture",
                "supported_projection_modes": (
                    "flat_plane",
                ),
            }
        )
    )

    assert component.component_id == "primary_form"

    assert height_map_result.normalized_geometry[
        "geometry_kind"
    ] == "height_map_relief"

    assert primitive_result.normalized_geometry[
        "geometry_kind"
    ] == "parametric_primitive"

    assert height_map_result is not primitive_result


def test_adapter_boundary_accepts_only_canonical_result_objects():
    adapter = AtlasHeightMapGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="AtlasGeometrySourceResult",
    ):
        adapter.validate_result(
            {
                "geometry_kind": "provider_payload",
            }
        )


def test_unsupported_projection_mode_fails_at_adapter_boundary():
    result = (
        AtlasParametricPrimitiveGeometrySourceAdapter()
        .adapt(
            {
                "primitive_type": "closed_cylinder",
                "parameters": {
                    "center_x": 0.0,
                    "center_y": 0.0,
                    "base_z": 0.0,
                    "radius": 5.0,
                    "height": 12.0,
                    "segments": 12,
                },
                "confidence": 1.0,
                "provenance": "primitive fixture",
                "supported_projection_modes": (
                    "flat_plane",
                ),
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="projection mode",
    ):
        AtlasGeometrySourceAdapter.validate_projection_mode(
            result,
            "surface_wrap",
        )
