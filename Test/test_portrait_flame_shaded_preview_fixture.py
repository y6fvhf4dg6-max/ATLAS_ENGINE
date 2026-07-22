from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from CORE.atlas_portrait_flame_shaded_preview_pipeline import (
    AtlasPortraitFlameShadedPreviewPipeline,
)
from Test.fixtures.portrait.portrait_flame_synthetic_face_fixture import (
    build_synthetic_flame_face_fixture,
)


PROJECT_ROOT = Path(
    __file__,
).resolve().parents[1]

PREVIEW_DIRECTORY = (
    PROJECT_ROOT
    / "OUTPUT"
    / "PORTRAIT"
    / "flame_synthetic_face"
)

SHADED_PREVIEW_PATH = (
    PREVIEW_DIRECTORY
    / "flame_synthetic_face_shaded_preview.png"
)

COVERAGE_PREVIEW_PATH = (
    PREVIEW_DIRECTORY
    / "flame_synthetic_face_coverage.png"
)


def _build_result():
    fixture = build_synthetic_flame_face_fixture()

    result = (
        AtlasPortraitFlameShadedPreviewPipeline.run(
            fixture.model,
            skinned_vertices=(
                fixture.skinned_vertices
            ),
            camera=fixture.camera,
            image_width=fixture.image_width,
            image_height=fixture.image_height,
            light_direction=(
                0.35,
                -0.45,
                0.82,
            ),
            ambient_strength=0.24,
            diffuse_strength=0.76,
            background_intensity=0.06,
        )
    )

    return fixture, result


def test_fixture_generates_face_mesh():
    fixture = (
        build_synthetic_flame_face_fixture()
    )

    assert fixture.model.vertex_count == 1297
    assert fixture.model.triangle_count == 2520
    assert fixture.skinned_vertices.shape == (
        1297,
        3,
    )


def test_fixture_pipeline_generates_visible_preview():
    fixture, result = _build_result()

    assert result.image_width == (
        fixture.image_width
    )
    assert result.image_height == (
        fixture.image_height
    )
    assert result.visible_triangle_count == 2520
    assert result.covered_pixel_count > 20000
    assert result.preview.maximum_intensity > (
        result.preview.minimum_intensity
    )
    assert np.unique(
        result.preview.preview[
            result.preview.coverage_mask
        ],
    ).size > 40


def test_fixture_preview_is_horizontally_symmetric_in_coverage():
    _, result = _build_result()

    coverage = result.preview.coverage_mask

    mirrored = np.fliplr(
        coverage,
    )

    mismatch_count = int(
        np.count_nonzero(
            coverage
            != mirrored
        )
    )

    assert mismatch_count < 600


def main() -> None:
    fixture, result = _build_result()

    PREVIEW_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    Image.fromarray(
        result.preview.preview,
        mode="L",
    ).save(
        SHADED_PREVIEW_PATH,
    )

    Image.fromarray(
        np.where(
            result.preview.coverage_mask,
            255,
            0,
        ).astype(
            np.uint8,
        ),
        mode="L",
    ).save(
        COVERAGE_PREVIEW_PATH,
    )

    print("")
    print("=" * 68)
    print(
        "ATLAS FLAME SYNTHETIC FACE "
        "SHADED PREVIEW"
    )
    print("=" * 68)
    print(
        f"Vertices             : "
        f"{result.vertex_count}"
    )
    print(
        f"Triangles            : "
        f"{result.face_count}"
    )
    print(
        f"Visible triangles    : "
        f"{result.visible_triangle_count}"
    )
    print(
        f"Image size           : "
        f"{result.image_width} x "
        f"{result.image_height}"
    )
    print(
        f"Covered pixels       : "
        f"{result.covered_pixel_count}"
    )
    print(
        f"Background pixels    : "
        f"{result.background_pixel_count}"
    )
    print(
        f"Minimum intensity    : "
        f"{result.preview.minimum_intensity:.6f}"
    )
    print(
        f"Maximum intensity    : "
        f"{result.preview.maximum_intensity:.6f}"
    )
    print(
        f"Light direction      : "
        f"{result.preview.light_direction}"
    )
    print(
        f"Shaded preview       : "
        f"{SHADED_PREVIEW_PATH}"
    )
    print(
        f"Coverage preview     : "
        f"{COVERAGE_PREVIEW_PATH}"
    )
    print(
        f"Synthetic model      : "
        f"{fixture.model.metadata['model_version']}"
    )
    print("=" * 68)
    print("")


if __name__ == "__main__":
    main()
