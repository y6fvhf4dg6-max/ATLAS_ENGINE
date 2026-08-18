from __future__ import annotations

import pytest

from CORE.atlas_surface_projection_engine import (
    AtlasSurfaceProjectionEngine,
)
from CORE.atlas_surface_target import AtlasSurfaceTarget


def _flat_target():
    return AtlasSurfaceTarget.flat_plane(
        surface_id="acceptance_wall",
        source_component_id="relief_component",
        target_component_id="wall_component",
        origin=(10.0, 20.0, 5.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 0.0, 1.0),
        clipping_boundary_uv=(
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )


def test_flat_projection_preserves_triangle_count_order_and_metadata():
    source = {
        "type": "synthetic_relief",
        "semantic_id": "portal_relief",
        "triangles": [
            (
                (1.0, 1.0, 0.0),
                (3.0, 1.0, 0.0),
                (1.0, 3.0, 1.0),
            ),
            (
                (3.0, 1.0, 0.0),
                (3.0, 3.0, 0.5),
                (1.0, 3.0, 1.0),
            ),
        ],
    }

    result = AtlasSurfaceProjectionEngine.project(
        mesh=source,
        target=_flat_target(),
    )

    assert result["mesh"]["type"] == "synthetic_relief"
    assert result["mesh"]["semantic_id"] == "portal_relief"
    assert len(result["mesh"]["triangles"]) == 2
    assert result["winding_preserved"] is True
    assert result["clipped_triangle_count"] == 0
    assert result["depth_envelope_violation_count"] == 0


def test_projection_is_deterministic():
    source = {
        "type": "synthetic_relief",
        "triangles": [
            (
                (1.0, 1.0, 0.0),
                (3.0, 1.0, 0.0),
                (1.0, 3.0, 1.0),
            ),
        ],
    }

    first = AtlasSurfaceProjectionEngine.project(
        mesh=source,
        target=_flat_target(),
    )
    second = AtlasSurfaceProjectionEngine.project(
        mesh=source,
        target=_flat_target(),
    )

    assert first == second


def test_projection_result_keeps_surface_component_identity():
    source = {
        "type": "synthetic_relief",
        "triangles": [
            (
                (1.0, 1.0, 0.0),
                (3.0, 1.0, 0.0),
                (1.0, 3.0, 1.0),
            ),
        ],
    }

    result = AtlasSurfaceProjectionEngine.project(
        mesh=source,
        target=_flat_target(),
    )

    assert result["surface_id"] == "acceptance_wall"
    assert result["source_component_id"] == "relief_component"
    assert result["target_component_id"] == "wall_component"
    assert result["projection_mode"] == "flat_plane"


def test_valid_attached_flat_relief_remains_inside_target_envelope():
    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (2.0, 2.0, 0.0),
                    (4.0, 2.0, 0.0),
                    (2.0, 4.0, 1.5),
                ),
            ],
        },
        target=_flat_target(),
    )

    triangle = result["mesh"]["triangles"][0]

    assert triangle[0] == pytest.approx((12.0, 20.0, 7.0))
    assert triangle[1] == pytest.approx((14.0, 20.0, 7.0))
    assert triangle[2] == pytest.approx((12.0, 18.5, 9.0))
