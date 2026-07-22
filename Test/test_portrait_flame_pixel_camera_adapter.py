from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_pixel_camera_adapter import (
    AtlasPortraitFlamePixelCameraAdapter,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _camera(
    **overrides,
) -> AtlasPortraitWeakPerspectiveCamera:
    values = {
        "scale": 2.5,
        "translation_x": 0.40,
        "translation_y": 0.55,
        "projected_points_2d": np.array(
            [
                [0.20, 0.30],
                [0.50, 0.60],
                [0.75, 0.90],
            ],
            dtype=np.float64,
        ),
        "weighted_root_mean_square_error": 0.012,
        "metadata": {
            "camera_model": "weak_perspective",
            "coordinate_space": "normalized",
            "synthetic": True,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitWeakPerspectiveCamera(
        **values,
    )


def test_adapter_returns_weak_perspective_camera():
    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=1024,
        image_height=1024,
    )

    assert isinstance(
        result,
        AtlasPortraitWeakPerspectiveCamera,
    )


def test_adapter_uses_largest_image_extent():
    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=800,
        image_height=1200,
    )

    assert result.metadata[
        "pixel_scale"
    ] == pytest.approx(
        1199.0,
    )


def test_adapter_scales_camera_parameters():
    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=1024,
        image_height=1024,
    )

    assert result.scale == pytest.approx(
        2.5 * 1023.0,
    )
    assert result.translation_x == pytest.approx(
        0.40 * 1023.0,
    )
    assert result.translation_y == pytest.approx(
        0.55 * 1023.0,
    )


def test_adapter_scales_projected_points():
    camera = _camera()

    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        camera,
        image_width=1024,
        image_height=1024,
    )

    np.testing.assert_allclose(
        result.projected_points_2d,
        camera.projected_points_2d * 1023.0,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_adapter_scales_weighted_error():
    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=1024,
        image_height=1024,
    )

    assert (
        result.weighted_root_mean_square_error
        == pytest.approx(
            0.012 * 1023.0,
        )
    )


def test_adapter_preserves_projected_point_count():
    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=1024,
        image_height=1024,
    )

    assert result.projected_point_count == 3


def test_adapter_adds_coordinate_metadata():
    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=800,
        image_height=1200,
    )

    assert result.metadata == {
        "camera_model": "weak_perspective",
        "coordinate_space": "pixel",
        "image_height": 1200,
        "image_width": 800,
        "pixel_scale": 1199.0,
        "source_coordinate_space": "normalized",
        "synthetic": True,
    }


def test_adapter_does_not_modify_source_camera():
    camera = _camera()
    before = camera.to_dict()

    AtlasPortraitFlamePixelCameraAdapter.adapt(
        camera,
        image_width=1024,
        image_height=1024,
    )

    assert camera.to_dict() == before


def test_adapter_returns_independent_projected_points():
    camera = _camera()

    result = AtlasPortraitFlamePixelCameraAdapter.adapt(
        camera,
        image_width=1024,
        image_height=1024,
    )

    assert not np.shares_memory(
        result.projected_points_2d,
        camera.projected_points_2d,
    )
    assert result.projected_points_2d.flags.writeable is False


def test_adapter_is_deterministic():
    first = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=1024,
        image_height=1024,
    )
    second = AtlasPortraitFlamePixelCameraAdapter.adapt(
        _camera(),
        image_width=1024,
        image_height=1024,
    )

    assert first.to_dict() == second.to_dict()


def test_adapter_rejects_wrong_camera_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitWeakPerspectiveCamera",
    ):
        AtlasPortraitFlamePixelCameraAdapter.adapt(
            object(),
            image_width=1024,
            image_height=1024,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "image_width",
            0,
        ),
        (
            "image_width",
            -1,
        ),
        (
            "image_width",
            1024.5,
        ),
        (
            "image_width",
            True,
        ),
        (
            "image_width",
            None,
        ),
        (
            "image_height",
            0,
        ),
        (
            "image_height",
            -1,
        ),
        (
            "image_height",
            1024.5,
        ),
        (
            "image_height",
            False,
        ),
        (
            "image_height",
            None,
        ),
    ],
)
def test_adapter_rejects_invalid_image_dimensions(
    field_name,
    value,
):
    arguments = {
        "image_width": 1024,
        "image_height": 1024,
    }
    arguments[
        field_name
    ] = value

    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field_name,
    ):
        AtlasPortraitFlamePixelCameraAdapter.adapt(
            _camera(),
            **arguments,
        )
