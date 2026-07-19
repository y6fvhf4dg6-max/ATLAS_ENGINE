from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from CORE.atlas_relief_pipeline import (
    AtlasReliefPipeline,
)


def _create_portrait_fixture(
    fixture_dir: Path,
) -> tuple[Path, Path]:
    fixture_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path = (
        fixture_dir / "synthetic_portrait.png"
    )
    mask_path = (
        fixture_dir / "synthetic_portrait_mask.png"
    )

    height = 48
    width = 40

    y, x = np.mgrid[
        0:height,
        0:width,
    ].astype(np.float64)

    face = np.exp(
        -(
            ((x - 20.0) / 10.0) ** 2
            + ((y - 22.0) / 15.0) ** 2
        )
    )

    nose = np.exp(
        -(
            ((x - 20.0) / 2.8) ** 2
            + ((y - 23.0) / 5.0) ** 2
        )
    )

    eyes = (
        np.exp(
            -(
                ((x - 15.5) / 2.0) ** 2
                + ((y - 18.0) / 1.2) ** 2
            )
        )
        + np.exp(
            -(
                ((x - 24.5) / 2.0) ** 2
                + ((y - 18.0) / 1.2) ** 2
            )
        )
    )

    luminance = np.clip(
        0.18
        + 0.62 * face
        + 0.18 * nose
        - 0.12 * eyes,
        0.0,
        1.0,
    )

    mask = np.clip(
        (face - 0.12) / 0.55,
        0.0,
        1.0,
    )

    Image.fromarray(
        np.rint(
            luminance * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(image_path)

    Image.fromarray(
        np.rint(
            mask * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(mask_path)

    return image_path, mask_path


def _build_fixture_result(
    tmp_path: Path,
) -> dict:
    image_path, mask_path = (
        _create_portrait_fixture(tmp_path)
    )

    return AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=80.0,
        depth_mm=96.0,
        form_sigma=3.0,
        detail_sigma=1.0,
        detail_weight=0.30,
        micro_detail_weight=0.05,
        mask_path=mask_path,
        mask_threshold=0.20,
        mask_feather_sigma=1.0,
        mask_morphology_operation="close",
        mask_morphology_radius=1,
    )


def test_image_pipeline_fixture_builds_printable_mesh(
    tmp_path,
):
    result = _build_fixture_result(tmp_path)

    mesh = result["relief_result"]["mesh"]
    report = result["relief_result"][
        "quality_report"
    ]

    assert mesh["row_count"] == 48
    assert mesh["column_count"] == 40
    assert len(mesh["triangles"]) == 7676
    assert mesh["minimum_z"] == pytest.approx(0.0)
    assert mesh["maximum_z"] == pytest.approx(2.8)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
    assert report["is_closed"] is True
    assert report["is_manifold"] is True
    assert report[
        "is_printable_topology"
    ] is True
    assert report["print_risk_status"] == "PASS"


def test_image_pipeline_fixture_preserves_soft_mask(
    tmp_path,
):
    result = _build_fixture_result(tmp_path)

    final_mask = result["layer_separation"][
        "subject_mask"
    ]

    assert np.any(
        (final_mask > 0.0)
        & (final_mask < 1.0)
    )
    assert final_mask[22, 20] > final_mask[0, 0]


def test_image_pipeline_fixture_separates_subject_depth(
    tmp_path,
):
    result = _build_fixture_result(tmp_path)

    separated = result["layer_separation"][
        "separated_depth"
    ]

    subject_depth = separated[22, 20]
    background_depth = separated[0, 0]

    assert subject_depth > background_depth
    assert subject_depth >= 0.60
    assert background_depth <= 0.40


def test_image_pipeline_fixture_stays_within_slope_budget(
    tmp_path,
):
    result = _build_fixture_result(tmp_path)

    report = result["relief_result"][
        "quality_report"
    ]

    assert (
        report["maximum_slope_degrees"]
        < report["warning_slope_degrees"]
    )
    assert (
        report["warning_slope_sample_count"]
        == 0
    )
    assert (
        report["critical_slope_sample_count"]
        == 0
    )


def test_image_pipeline_fixture_is_deterministic(
    tmp_path,
):
    first = _build_fixture_result(
        tmp_path / "first"
    )
    second = _build_fixture_result(
        tmp_path / "second"
    )

    np.testing.assert_allclose(
        first["layer_separation"][
            "separated_depth"
        ],
        second["layer_separation"][
            "separated_depth"
        ],
    )

    np.testing.assert_allclose(
        first["relief_result"][
            "processed_height_map"
        ],
        second["relief_result"][
            "processed_height_map"
        ],
    )

    assert (
        first["relief_result"]["mesh"][
            "triangles"
        ]
        == second["relief_result"]["mesh"][
            "triangles"
        ]
    )
