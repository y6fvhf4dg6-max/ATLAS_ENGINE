import numpy as np
import pytest

from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_portrait_contact_plane_projector import (
    AtlasPortraitContactPlaneProjector,
)
from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


def _surface():
    return AtlasParametricFaceSurface(
        x_coordinates=[
            [-1.0, 0.0, 1.0],
            [-1.0, 0.0, 1.0],
        ],
        y_coordinates=[
            [-0.5, -0.5, -0.5],
            [0.5, 0.5, 0.5],
        ],
        z_coordinates=[
            [0.0, 0.4, 0.0],
            [0.1, 0.8, 0.1],
        ],
    )


def test_projector_returns_projection_result():
    result = AtlasPortraitContactPlaneProjector.project(
        _surface(),
    )

    assert isinstance(
        result,
        AtlasPortraitContactPlaneProjectionResult,
    )


def test_projector_uses_surface_maximum_as_contact_plane():
    result = AtlasPortraitContactPlaneProjector.project(
        _surface(),
    )

    assert result.contact_plane_z == pytest.approx(
        0.8,
    )


def test_projector_calculates_distance_to_contact_plane():
    result = AtlasPortraitContactPlaneProjector.project(
        _surface(),
    )

    expected = np.array(
        [
            [0.8, 0.4, 0.8],
            [0.7, 0.0, 0.7],
        ],
        dtype=np.float64,
    )

    assert result.distance_to_plane == pytest.approx(
        expected,
    )


def test_projector_reports_contact_location():
    result = AtlasPortraitContactPlaneProjector.project(
        _surface(),
    )

    assert result.contact_index == (
        1,
        1,
    )


def test_projector_reports_maximum_distance():
    result = AtlasPortraitContactPlaneProjector.project(
        _surface(),
    )

    assert result.maximum_distance == pytest.approx(
        0.8,
    )


def test_projector_preserves_source_shape():
    result = AtlasPortraitContactPlaneProjector.project(
        _surface(),
    )

    assert result.source_shape == (
        2,
        3,
    )


def test_projector_adds_deterministic_metadata():
    result = AtlasPortraitContactPlaneProjector.project(
        _surface(),
    )

    assert result.metadata == {
        "projection_mode": "frontal_contact_plane",
        "contact_policy": "first_maximum_z_row_major",
        "distance_direction": "contact_plane_z_minus_surface_z",
    }


def test_projector_does_not_modify_source_surface():
    surface = _surface()

    original_x = surface.x_coordinates.copy()
    original_y = surface.y_coordinates.copy()
    original_z = surface.z_coordinates.copy()

    AtlasPortraitContactPlaneProjector.project(
        surface,
    )

    assert surface.x_coordinates == pytest.approx(
        original_x,
    )
    assert surface.y_coordinates == pytest.approx(
        original_y,
    )
    assert surface.z_coordinates == pytest.approx(
        original_z,
    )


def test_projector_is_deterministic():
    surface = _surface()

    first = AtlasPortraitContactPlaneProjector.project(
        surface,
    )
    second = AtlasPortraitContactPlaneProjector.project(
        surface,
    )

    assert first.contact_plane_z == pytest.approx(
        second.contact_plane_z,
    )
    assert first.contact_index == second.contact_index
    assert first.maximum_distance == pytest.approx(
        second.maximum_distance,
    )
    assert first.distance_to_plane == pytest.approx(
        second.distance_to_plane,
    )
    assert first.metadata == second.metadata


def test_projector_uses_first_maximum_in_row_major_order():
    surface = AtlasParametricFaceSurface(
        x_coordinates=[
            [-1.0, 0.0, 1.0],
            [-1.0, 0.0, 1.0],
        ],
        y_coordinates=[
            [-0.5, -0.5, -0.5],
            [0.5, 0.5, 0.5],
        ],
        z_coordinates=[
            [0.0, 0.8, 0.0],
            [0.1, 0.8, 0.1],
        ],
    )

    result = AtlasPortraitContactPlaneProjector.project(
        surface,
    )

    assert result.contact_index == (
        0,
        1,
    )


def test_projector_handles_constant_depth_surface():
    surface = AtlasParametricFaceSurface(
        x_coordinates=[
            [-1.0, 1.0],
            [-1.0, 1.0],
        ],
        y_coordinates=[
            [-1.0, -1.0],
            [1.0, 1.0],
        ],
        z_coordinates=[
            [0.5, 0.5],
            [0.5, 0.5],
        ],
    )

    result = AtlasPortraitContactPlaneProjector.project(
        surface,
    )

    assert result.contact_plane_z == pytest.approx(
        0.5,
    )
    assert result.contact_index == (
        0,
        0,
    )
    assert result.maximum_distance == pytest.approx(
        0.0,
    )
    assert result.distance_to_plane == pytest.approx(
        np.zeros(
            (
                2,
                2,
            ),
            dtype=np.float64,
        )
    )


def test_projector_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="surface",
    ):
        AtlasPortraitContactPlaneProjector.project(
            object(),
        )
