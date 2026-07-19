from pathlib import Path

import numpy as np
import pytest
from CORE.atlas_relief_pipeline import (
    AtlasReliefPipeline,
)
from Test.fixtures.relief.relief_synthetic_portrait_fixture import (
    write_synthetic_portrait_fixture,
)


def _build_fixture_result(
    tmp_path: Path,
) -> dict:
    fixture_paths = (
        write_synthetic_portrait_fixture(
            tmp_path,
        )
    )

    image_path = fixture_paths[
        "image_path"
    ]
    mask_path = fixture_paths[
        "mask_path"
    ]

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
