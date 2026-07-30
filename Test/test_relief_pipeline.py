import numpy as np
import pytest

from CORE.atlas_relief_pipeline import (
    AtlasReliefPipeline,
)


def _values():
    return np.array(
        [
            [10.0, 20.0, 30.0],
            [40.0, 50.0, 60.0],
            [70.0, 80.0, 90.0],
        ],
        dtype=np.float64,
    )


def test_pipeline_builds_complete_result():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
    )

    assert result["type"] == (
        "relief_pipeline_result"
    )
    assert result["mesh"]["type"] == (
        "relief_mesh"
    )
    assert result[
        "quality_report"
    ]["is_printable_topology"] is True


def test_pipeline_normalizes_input():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
    )

    normalized = result[
        "normalized_height_map"
    ]

    assert normalized.min() == pytest.approx(
        0.0
    )
    assert normalized.max() == pytest.approx(
        1.0
    )


def test_pipeline_supports_resampling():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
        target_rows=7,
        target_columns=9,
    )

    assert result[
        "processed_height_map"
    ].shape == (7, 9)

    assert result["mesh"]["row_count"] == 7
    assert result["mesh"]["column_count"] == 9


def test_pipeline_supports_smoothing():
    values = np.zeros(
        (7, 7),
        dtype=np.float64,
    )
    values[3, 3] = 1.0

    result = AtlasReliefPipeline.build(
        values,
        width_mm=20.0,
        depth_mm=20.0,
        smoothing_sigma=1.0,
        smoothing_radius=3,
    )

    processed = result[
        "processed_height_map"
    ]

    assert 0.0 < processed[3, 3] < 1.0
    assert processed[3, 2] > 0.0


def test_pipeline_supports_inversion():
    normal = AtlasReliefPipeline.build(
        _values(),
        width_mm=10.0,
        depth_mm=10.0,
    )

    inverted = AtlasReliefPipeline.build(
        _values(),
        width_mm=10.0,
        depth_mm=10.0,
        invert=True,
    )

    assert np.allclose(
        inverted["normalized_height_map"],
        1.0 - normal[
            "normalized_height_map"
        ],
    )


def test_pipeline_preserves_physical_dimensions():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=42.0,
        depth_mm=27.0,
        base_thickness_mm=1.2,
        relief_height_mm=3.5,
        origin_x=4.0,
        origin_y=6.0,
        origin_z=2.0,
    )

    report = result["quality_report"]

    assert report["width_mm"] == pytest.approx(
        42.0
    )
    assert report["depth_mm"] == pytest.approx(
        27.0
    )
    assert report[
        "total_height_mm"
    ] == pytest.approx(4.7)


def test_pipeline_is_deterministic():
    arguments = {
        "values": _values(),
        "width_mm": 30.0,
        "depth_mm": 20.0,
        "target_rows": 8,
        "target_columns": 10,
        "smoothing_sigma": 0.8,
        "smoothing_radius": 2,
    }

    first = AtlasReliefPipeline.build(
        **arguments
    )
    second = AtlasReliefPipeline.build(
        **arguments
    )

    assert np.array_equal(
        first["processed_height_map"],
        second["processed_height_map"],
    )

    assert (
        first["mesh"]["triangles"]
        == second["mesh"]["triangles"]
    )

    assert (
        first["quality_report"]
        == second["quality_report"]
    )


@pytest.mark.parametrize(
    "target_rows,target_columns",
    [
        (5, None),
        (None, 5),
    ],
)
def test_pipeline_requires_complete_target_size(
    target_rows,
    target_columns,
):
    with pytest.raises(ValueError):
        AtlasReliefPipeline.build(
            _values(),
            width_mm=10.0,
            depth_mm=10.0,
            target_rows=target_rows,
            target_columns=target_columns,
        )


def test_pipeline_rejects_radius_without_sigma():
    with pytest.raises(ValueError):
        AtlasReliefPipeline.build(
            _values(),
            width_mm=10.0,
            depth_mm=10.0,
            smoothing_radius=2,
        )


def test_pipeline_supports_contrast_remapping():
    values = np.array(
        [
            [0.0, 0.25, 0.50],
            [0.75, 0.90, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build(
        values,
        width_mm=20.0,
        depth_mm=10.0,
        black_point=0.25,
        white_point=0.75,
        gamma=1.0,
    )

    contrast = result[
        "contrast_height_map"
    ]

    assert contrast[0, 0] == pytest.approx(0.0)
    assert contrast[0, 1] == pytest.approx(0.0)
    assert contrast[0, 2] == pytest.approx(0.5)
    assert contrast[1, 0] == pytest.approx(1.0)
    assert contrast[1, 2] == pytest.approx(1.0)


def test_pipeline_gamma_changes_processed_relief():
    values = [
        [0.0, 0.5, 1.0],
        [0.0, 0.5, 1.0],
    ]

    normal = AtlasReliefPipeline.build(
        values,
        width_mm=10.0,
        depth_mm=5.0,
        gamma=1.0,
    )

    shaped = AtlasReliefPipeline.build(
        values,
        width_mm=10.0,
        depth_mm=5.0,
        gamma=2.0,
    )

    assert shaped[
        "contrast_height_map"
    ][0, 1] == pytest.approx(0.25)

    assert not np.array_equal(
        normal["processed_height_map"],
        shaped["processed_height_map"],
    )


def test_pipeline_records_contrast_settings():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=10.0,
        depth_mm=10.0,
        black_point=0.10,
        white_point=0.90,
        gamma=0.75,
    )

    settings = result["settings"]

    assert settings["black_point"] == pytest.approx(
        0.10
    )
    assert settings["white_point"] == pytest.approx(
        0.90
    )
    assert settings["gamma"] == pytest.approx(
        0.75
    )


@pytest.mark.parametrize(
    "black_point,white_point,gamma",
    [
        (-0.1, 1.0, 1.0),
        (0.0, 1.1, 1.0),
        (0.8, 0.2, 1.0),
        (0.0, 1.0, 0.0),
    ],
)
def test_pipeline_rejects_invalid_contrast_settings(
    black_point,
    white_point,
    gamma,
):
    with pytest.raises(ValueError):
        AtlasReliefPipeline.build(
            _values(),
            width_mm=10.0,
            depth_mm=10.0,
            black_point=black_point,
            white_point=white_point,
            gamma=gamma,
        )


def test_pipeline_forwards_slope_risk_thresholds():
    result = AtlasReliefPipeline.build(
        [
            [0.5, 1.0],
            [0.0, 0.5],
        ],
        width_mm=1.0,
        depth_mm=1.0,
        relief_height_mm=2.0,
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
        warning_slope_area_percent=100.0,
        critical_slope_area_percent=100.0,
    )

    report = result["quality_report"]

    assert report["warning_slope_area_percent"] == 100.0
    assert report["critical_slope_area_percent"] == 100.0
    assert report["print_risk_status"] == "WARN"


def test_pipeline_records_slope_risk_settings():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
        warning_slope_degrees=48.0,
        critical_slope_degrees=72.0,
        warning_slope_area_percent=3.0,
        critical_slope_area_percent=1.0,
    )

    settings = result["settings"]

    assert settings["warning_slope_degrees"] == 48.0
    assert settings["critical_slope_degrees"] == 72.0
    assert settings["warning_slope_area_percent"] == 3.0
    assert settings["critical_slope_area_percent"] == 1.0


def test_pipeline_preserves_default_slope_risk_settings():
    result = AtlasReliefPipeline.build(
        _values(),
        width_mm=30.0,
        depth_mm=20.0,
    )

    settings = result["settings"]

    assert settings["warning_slope_degrees"] == 55.0
    assert settings["critical_slope_degrees"] == 75.0
    assert settings["warning_slope_area_percent"] == 0.0
    assert settings["critical_slope_area_percent"] == 0.0


def test_pipeline_accepts_relief_risk_profile():
    from CORE.atlas_relief_risk_profile import (
        AtlasReliefRiskProfile,
    )

    profile = AtlasReliefRiskProfile(
        warning_slope_degrees=47.0,
        critical_slope_degrees=71.0,
        warning_slope_area_percent=4.0,
        critical_slope_area_percent=2.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
        risk_profile=profile,
    )

    assert result["settings"]["warning_slope_degrees"] == 47.0
    assert result["settings"]["critical_slope_degrees"] == 71.0
    assert (
        result["settings"]["warning_slope_area_percent"]
        == 4.0
    )
    assert (
        result["settings"]["critical_slope_area_percent"]
        == 2.0
    )


def test_pipeline_risk_profile_overrides_scalar_risk_arguments():
    from CORE.atlas_relief_risk_profile import (
        AtlasReliefRiskProfile,
    )

    profile = AtlasReliefRiskProfile(
        warning_slope_degrees=46.0,
        critical_slope_degrees=70.0,
        warning_slope_area_percent=5.0,
        critical_slope_area_percent=3.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
        warning_slope_degrees=55.0,
        critical_slope_degrees=75.0,
        warning_slope_area_percent=0.0,
        critical_slope_area_percent=0.0,
        risk_profile=profile,
    )

    assert result["settings"]["warning_slope_degrees"] == 46.0
    assert result["settings"]["critical_slope_degrees"] == 70.0
    assert (
        result["settings"]["warning_slope_area_percent"]
        == 5.0
    )
    assert (
        result["settings"]["critical_slope_area_percent"]
        == 3.0
    )


def test_pipeline_records_risk_profile_name():
    from CORE.atlas_relief_risk_profile import (
        AtlasReliefRiskProfile,
    )

    profile = AtlasReliefRiskProfile(
        name="prototype-safe",
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
        risk_profile=profile,
    )

    assert (
        result["settings"]["risk_profile_name"]
        == "prototype-safe"
    )


def test_pipeline_records_no_profile_name_by_default():
    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=40.0,
    )

    assert result["settings"]["risk_profile_name"] is None


def test_pipeline_accepts_physical_sampling_plan():
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=30.0,
        sampling_plan=plan,
    )

    assert result["processed_height_map"].shape == (
        4,
        5,
    )
    assert result["mesh"]["row_count"] == 4
    assert result["mesh"]["column_count"] == 5


def test_pipeline_records_sampling_plan_metadata():
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=41.0,
        depth_mm=31.0,
        target_sample_spacing_mm=10.0,
    )

    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=41.0,
        depth_mm=31.0,
        sampling_plan=plan,
    )

    settings = result["settings"]

    assert settings[
        "target_sample_spacing_mm"
    ] == 10.0
    assert settings[
        "effective_spacing_x_mm"
    ] == pytest.approx(8.2)
    assert settings[
        "effective_spacing_y_mm"
    ] == pytest.approx(7.75)
    assert settings["sample_count"] == 30
    assert (
        settings["expected_triangle_count"]
        == plan.total_triangle_count
    )


def test_pipeline_sampling_metadata_is_none_by_default():
    result = AtlasReliefPipeline.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=40.0,
        depth_mm=30.0,
    )

    settings = result["settings"]

    assert settings[
        "target_sample_spacing_mm"
    ] is None
    assert settings[
        "effective_spacing_x_mm"
    ] is None
    assert settings[
        "effective_spacing_y_mm"
    ] is None
    assert settings["sample_count"] is None
    assert settings[
        "expected_triangle_count"
    ] is None


def test_pipeline_rejects_sampling_plan_with_explicit_target_size():
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "sampling_plan cannot be combined with "
            "target_rows or target_columns"
        ),
    ):
        AtlasReliefPipeline.build(
            [
                [0.0, 0.5],
                [0.5, 1.0],
            ],
            width_mm=40.0,
            depth_mm=30.0,
            target_rows=4,
            target_columns=5,
            sampling_plan=plan,
        )


@pytest.mark.parametrize(
    "width_mm,depth_mm",
    [
        (41.0, 30.0),
        (40.0, 31.0),
    ],
)
def test_pipeline_rejects_sampling_plan_dimension_mismatch(
    width_mm,
    depth_mm,
):
    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "sampling_plan dimensions must match "
            "pipeline dimensions"
        ),
    ):
        AtlasReliefPipeline.build(
            [
                [0.0, 0.5],
                [0.5, 1.0],
            ],
            width_mm=width_mm,
            depth_mm=depth_mm,
            sampling_plan=plan,
        )


def test_pipeline_build_from_image_runs_real_image_chain(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "relief-input.png"

    image = Image.new(
        "RGB",
        (4, 3),
    )
    image.putdata(
        [
            (0, 0, 0),
            (64, 64, 64),
            (128, 128, 128),
            (255, 255, 255),
            (32, 32, 32),
            (96, 96, 96),
            (160, 160, 160),
            (224, 224, 224),
            (16, 16, 16),
            (80, 80, 80),
            (144, 144, 144),
            (208, 208, 208),
        ]
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=40.0,
        depth_mm=30.0,
        form_sigma=1.5,
        detail_sigma=0.6,
    )

    assert result["type"] == (
        "relief_image_pipeline_result"
    )
    assert result["image_input"]["type"] == (
        "relief_image_input"
    )
    assert result["multiscale"]["type"] == (
        "relief_multiscale_decomposition"
    )
    assert result["depth_composition"]["type"] == (
        "relief_depth_candidate"
    )
    assert result["relief_result"]["type"] == (
        "relief_pipeline_result"
    )
    assert result["relief_result"][
        "quality_report"
    ]["is_printable_topology"] is True


def test_pipeline_build_from_image_preserves_source_shape(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "shape.png"

    image = Image.new(
        "L",
        (5, 3),
    )
    image.putdata(
        list(range(15))
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=50.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
    )

    assert result["image_input"]["luminance"].shape == (
        3,
        5,
    )
    assert result["multiscale"]["form"].shape == (
        3,
        5,
    )
    assert result["depth_composition"][
        "depth_candidate"
    ].shape == (3, 5)


def test_pipeline_build_from_image_forwards_sampling(
    tmp_path,
):
    from PIL import Image

    from CORE.atlas_relief_sampling_plan import (
        AtlasReliefSamplingPlan,
    )

    path = tmp_path / "sampling.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    plan = AtlasReliefSamplingPlan(
        width_mm=40.0,
        depth_mm=30.0,
        target_sample_spacing_mm=10.0,
    )

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=40.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        sampling_plan=plan,
    )

    relief_result = result["relief_result"]

    assert relief_result[
        "processed_height_map"
    ].shape == (4, 5)
    assert relief_result["settings"][
        "sample_count"
    ] == 20


def test_pipeline_build_from_image_records_settings(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "settings.png"

    image = Image.new(
        "RGBA",
        (3, 3),
        (255, 255, 255, 128),
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=2.0,
        detail_sigma=0.7,
        form_weight=1.1,
        detail_weight=0.4,
        micro_detail_weight=0.08,
        micro_detail_limit=0.03,
        alpha_background_luminance=0.2,
    )

    settings = result["image_settings"]

    assert settings["form_sigma"] == pytest.approx(
        2.0
    )
    assert settings["detail_sigma"] == pytest.approx(
        0.7
    )
    assert settings["form_weight"] == pytest.approx(
        1.1
    )
    assert settings["detail_weight"] == pytest.approx(
        0.4
    )
    assert settings[
        "micro_detail_weight"
    ] == pytest.approx(0.08)
    assert settings[
        "micro_detail_limit"
    ] == pytest.approx(0.03)
    assert settings[
        "alpha_background_luminance"
    ] == pytest.approx(0.2)


def test_pipeline_build_from_image_is_deterministic(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "deterministic-image.png"

    image = Image.new(
        "RGB",
        (4, 4),
    )
    image.putdata(
        [
            (
                index * 11,
                index * 7,
                index * 3,
            )
            for index in range(16)
        ]
    )
    image.save(path)

    arguments = {
        "image_path": path,
        "width_mm": 40.0,
        "depth_mm": 40.0,
        "form_sigma": 1.5,
        "detail_sigma": 0.6,
    }

    first = AtlasReliefPipeline.build_from_image(
        **arguments
    )
    second = AtlasReliefPipeline.build_from_image(
        **arguments
    )

    assert np.array_equal(
        first["depth_composition"][
            "depth_candidate"
        ],
        second["depth_composition"][
            "depth_candidate"
        ],
    )
    assert (
        first["relief_result"]["mesh"]["triangles"]
        == second["relief_result"]["mesh"]["triangles"]
    )


def test_pipeline_build_from_image_applies_depth_compression(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "compressed-image.png"

    image = Image.new(
        "L",
        (5, 2),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            255,
            0,
            32,
            64,
            96,
            255,
        ]
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=50.0,
        depth_mm=10.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        depth_lower_percentile=0.0,
        depth_upper_percentile=80.0,
        depth_gamma=1.0,
    )

    compression = result["depth_compression"]

    assert compression["type"] == (
        "relief_depth_compression"
    )
    assert compression["compressed_depth"].min() == (
        pytest.approx(0.0)
    )
    assert compression["compressed_depth"].max() == (
        pytest.approx(1.0)
    )


def test_pipeline_build_from_image_uses_compressed_depth(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "compressed-source.png"

    image = Image.new(
        "L",
        (4, 3),
    )
    image.putdata(
        [
            0,
            20,
            40,
            255,
            10,
            30,
            50,
            70,
            15,
            35,
            55,
            75,
        ]
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=40.0,
        depth_mm=30.0,
        form_sigma=1.5,
        detail_sigma=0.6,
        depth_lower_percentile=5.0,
        depth_upper_percentile=90.0,
        depth_gamma=0.9,
    )

    compressed = result[
        "depth_compression"
    ]["compressed_depth"]

    assert np.allclose(
        result["relief_result"][
            "normalized_height_map"
        ],
        compressed,
    )


def test_pipeline_build_from_image_records_compression_settings(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "compression-settings.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        depth_lower_percentile=2.5,
        depth_upper_percentile=97.5,
        depth_gamma=0.85,
    )

    settings = result["image_settings"]

    assert settings[
        "depth_lower_percentile"
    ] == pytest.approx(2.5)
    assert settings[
        "depth_upper_percentile"
    ] == pytest.approx(97.5)
    assert settings["depth_gamma"] == pytest.approx(
        0.85
    )


def test_pipeline_build_from_image_default_compression_policy(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "default-compression.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
    )

    compression = result["depth_compression"]

    assert compression["lower_percentile"] == (
        pytest.approx(1.0)
    )
    assert compression["upper_percentile"] == (
        pytest.approx(99.0)
    )
    assert compression["gamma"] == pytest.approx(
        1.0
    )


def test_pipeline_build_from_image_applies_subject_mask_layers(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "masked-relief.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    subject_mask = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
        background_depth_range=(0.0, 0.30),
        foreground_depth_range=(0.60, 1.0),
    )

    separation = result["layer_separation"]

    assert separation["type"] == (
        "relief_layer_separation"
    )
    assert separation["subject_mask"].shape == (
        3,
        3,
    )

    separated = separation["separated_depth"]

    assert separated[0, 0] <= 0.30
    assert separated[2, 2] >= 0.60


def test_pipeline_build_from_image_uses_separated_depth(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "layered-source.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    subject_mask = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
    )

    assert np.allclose(
        result["relief_result"][
            "normalized_height_map"
        ],
        result["layer_separation"][
            "separated_depth"
        ],
    )


def test_pipeline_build_from_image_without_mask_skips_layers(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "unmasked-source.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
    )

    assert result["layer_separation"] is None

    assert np.allclose(
        result["relief_result"][
            "normalized_height_map"
        ],
        result["depth_compression"][
            "compressed_depth"
        ],
    )


def test_pipeline_build_from_image_records_layer_settings(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "layer-settings.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    subject_mask = np.zeros(
        (3, 3),
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
        background_depth_range=(0.05, 0.35),
        foreground_depth_range=(0.65, 0.95),
    )

    settings = result["image_settings"]

    assert settings["has_subject_mask"] is True
    assert settings[
        "background_depth_range"
    ] == (0.05, 0.35)
    assert settings[
        "foreground_depth_range"
    ] == (0.65, 0.95)


def test_pipeline_build_from_image_rejects_mask_shape_mismatch(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "mask-mismatch.png"

    image = Image.new(
        "L",
        (3, 3),
        128,
    )
    image.save(path)

    subject_mask = np.zeros(
        (2, 2),
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        AtlasReliefPipeline.build_from_image(
            path,
            width_mm=30.0,
            depth_mm=30.0,
            form_sigma=1.2,
            detail_sigma=0.5,
            subject_mask=subject_mask,
        )


def test_pipeline_build_from_image_loads_mask_path(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source.png"
    mask_path = tmp_path / "subject-mask.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(image_path)

    mask_image = Image.new(
        "L",
        (3, 3),
    )
    mask_image.putdata(
        [
            0,
            0,
            0,
            0,
            255,
            255,
            0,
            255,
            255,
        ]
    )
    mask_image.save(mask_path)

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        mask_path=mask_path,
    )

    assert result["mask_input"]["type"] == (
        "relief_mask_input"
    )
    assert result["layer_separation"][
        "subject_mask"
    ].shape == (3, 3)
    assert result["image_settings"][
        "mask_source"
    ] == "file"


def test_pipeline_build_from_image_supports_alpha_mask_path(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-alpha.png"
    mask_path = tmp_path / "alpha-mask.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(image_path)

    mask_image = Image.new(
        "RGBA",
        (3, 3),
    )
    mask_image.putdata(
        [
            (255, 255, 255, 0),
            (255, 255, 255, 0),
            (255, 255, 255, 0),
            (255, 255, 255, 0),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
            (255, 255, 255, 0),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
        ]
    )
    mask_image.save(mask_path)

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        mask_path=mask_path,
        mask_use_alpha=True,
    )

    assert result["mask_input"]["use_alpha"] is True
    assert result["layer_separation"][
        "subject_mask"
    ][0, 0] == pytest.approx(0.0)
    assert result["layer_separation"][
        "subject_mask"
    ][2, 2] == pytest.approx(1.0)


def test_pipeline_build_from_image_rejects_mask_and_mask_path(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-conflict.png"
    mask_path = tmp_path / "mask-conflict.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(image_path)

    Image.new(
        "L",
        (3, 3),
        255,
    ).save(mask_path)

    subject_mask = np.ones(
        (3, 3),
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        AtlasReliefPipeline.build_from_image(
            image_path,
            width_mm=30.0,
            depth_mm=30.0,
            form_sigma=1.2,
            detail_sigma=0.5,
            subject_mask=subject_mask,
            mask_path=mask_path,
        )


def test_pipeline_build_from_image_records_array_mask_source(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-array-mask.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(image_path)

    subject_mask = np.ones(
        (3, 3),
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
    )

    assert result["mask_input"] is None
    assert result["image_settings"][
        "mask_source"
    ] == "array"


def test_pipeline_build_from_image_records_no_mask_source(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-no-mask.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(image_path)

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
    )

    assert result["mask_input"] is None
    assert result["image_settings"][
        "mask_source"
    ] is None


def test_pipeline_build_from_image_processes_mask_path(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-mask-process.png"
    mask_path = tmp_path / "mask-process.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(image_path)

    mask_image = Image.new(
        "L",
        (3, 3),
    )
    mask_image.putdata(
        [
            0,
            100,
            0,
            100,
            200,
            100,
            0,
            100,
            0,
        ]
    )
    mask_image.save(mask_path)

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        mask_path=mask_path,
        mask_threshold=0.5,
    )

    assert result["mask_processing"]["type"] == (
        "relief_mask_processing_result"
    )
    np.testing.assert_allclose(
        result["mask_processing"][
            "processed_mask"
        ],
        np.array(
            [
                [0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )
    np.testing.assert_allclose(
        result["layer_separation"][
            "subject_mask"
        ],
        result["mask_processing"][
            "processed_mask"
        ],
    )


def test_pipeline_build_from_image_feathers_mask_path(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-mask-feather.png"
    mask_path = tmp_path / "mask-feather.png"

    Image.new(
        "L",
        (5, 5),
        128,
    ).save(image_path)

    mask_image = Image.new(
        "L",
        (5, 5),
        0,
    )
    mask_image.putpixel(
        (2, 2),
        255,
    )
    mask_image.save(mask_path)

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=50.0,
        depth_mm=50.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        mask_path=mask_path,
        mask_feather_sigma=1.0,
    )

    processed = result["mask_processing"][
        "processed_mask"
    ]

    assert processed[2, 2] < 1.0
    assert processed[2, 1] > 0.0
    assert result["image_settings"][
        "mask_feather_sigma"
    ] == pytest.approx(1.0)


def test_pipeline_build_from_image_processes_array_mask(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-array-process.png"

    Image.new(
        "L",
        (2, 2),
        128,
    ).save(image_path)

    subject_mask = np.array(
        [
            [-1.0, 0.25],
            [0.75, 2.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=20.0,
        depth_mm=20.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
    )

    np.testing.assert_allclose(
        result["mask_processing"][
            "processed_mask"
        ],
        np.array(
            [
                [0.0, 0.25],
                [0.75, 1.0],
            ],
            dtype=np.float64,
        ),
    )


def test_pipeline_build_from_image_records_mask_processing_settings(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-mask-settings.png"

    Image.new(
        "L",
        (2, 2),
        128,
    ).save(image_path)

    subject_mask = np.ones(
        (2, 2),
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=20.0,
        depth_mm=20.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
        mask_threshold=0.4,
        mask_feather_sigma=0.8,
    )

    assert result["image_settings"][
        "mask_threshold"
    ] == pytest.approx(0.4)
    assert result["image_settings"][
        "mask_feather_sigma"
    ] == pytest.approx(0.8)


def test_pipeline_build_from_image_has_no_mask_processing_without_mask(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-no-mask-processing.png"

    Image.new(
        "L",
        (2, 2),
        128,
    ).save(image_path)

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=20.0,
        depth_mm=20.0,
        form_sigma=1.2,
        detail_sigma=0.5,
    )

    assert result["mask_processing"] is None
    assert result["image_settings"][
        "mask_threshold"
    ] is None
    assert result["image_settings"][
        "mask_feather_sigma"
    ] == pytest.approx(0.0)


def test_pipeline_build_from_image_applies_mask_morphology(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-morphology.png"

    Image.new(
        "L",
        (5, 5),
        128,
    ).save(image_path)

    subject_mask = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    subject_mask[2, 2] = 1.0

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=50.0,
        depth_mm=50.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
        mask_morphology_operation="dilate",
        mask_morphology_radius=1,
    )

    expected = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    expected[1:4, 1:4] = 1.0

    assert result["mask_morphology"]["type"] == (
        "relief_mask_morphology_result"
    )
    np.testing.assert_array_equal(
        result["mask_morphology"][
            "processed_mask"
        ],
        expected,
    )
    np.testing.assert_array_equal(
        result["layer_separation"][
            "subject_mask"
        ],
        expected,
    )


def test_pipeline_build_from_image_applies_morphology_after_preprocessing(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-morphology-order.png"

    Image.new(
        "L",
        (5, 5),
        128,
    ).save(image_path)

    subject_mask = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    subject_mask[2, 2] = 0.75

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=50.0,
        depth_mm=50.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
        mask_threshold=0.5,
        mask_morphology_operation="dilate",
        mask_morphology_radius=1,
    )

    assert result["mask_processing"][
        "processed_mask"
    ][2, 2] == pytest.approx(1.0)

    assert result["mask_morphology"][
        "processed_mask"
    ][1, 1] == pytest.approx(1.0)


def test_pipeline_build_from_image_records_mask_morphology_settings(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-morphology-settings.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(image_path)

    subject_mask = np.ones(
        (3, 3),
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
        mask_morphology_operation="close",
        mask_morphology_radius=1,
        mask_morphology_threshold=0.6,
    )

    settings = result["image_settings"]

    assert settings[
        "mask_morphology_operation"
    ] == "close"
    assert settings[
        "mask_morphology_radius"
    ] == 1
    assert settings[
        "mask_morphology_threshold"
    ] == pytest.approx(0.6)


def test_pipeline_build_from_image_skips_mask_morphology_by_default(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-no-morphology.png"

    Image.new(
        "L",
        (2, 2),
        128,
    ).save(image_path)

    subject_mask = np.ones(
        (2, 2),
        dtype=np.float64,
    )

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=20.0,
        depth_mm=20.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
    )

    assert result["mask_morphology"] is None
    assert result["image_settings"][
        "mask_morphology_operation"
    ] is None
    assert result["image_settings"][
        "mask_morphology_radius"
    ] == 0


def test_pipeline_build_from_image_rejects_morphology_without_mask(
    tmp_path,
):
    from PIL import Image

    image_path = tmp_path / "source-morphology-no-mask.png"

    Image.new(
        "L",
        (2, 2),
        128,
    ).save(image_path)

    with pytest.raises(ValueError):
        AtlasReliefPipeline.build_from_image(
            image_path,
            width_mm=20.0,
            depth_mm=20.0,
            form_sigma=1.2,
            detail_sigma=0.5,
            mask_morphology_operation="dilate",
            mask_morphology_radius=1,
        )


def test_pipeline_build_from_image_feathers_after_morphology(
    tmp_path,
):
    from PIL import Image

    image_path = (
        tmp_path
        / "source-morphology-feather-order.png"
    )

    Image.new(
        "L",
        (7, 7),
        128,
    ).save(image_path)

    subject_mask = np.zeros(
        (7, 7),
        dtype=np.float64,
    )
    subject_mask[3, 3] = 1.0

    result = AtlasReliefPipeline.build_from_image(
        image_path,
        width_mm=70.0,
        depth_mm=70.0,
        form_sigma=1.2,
        detail_sigma=0.5,
        subject_mask=subject_mask,
        mask_morphology_operation="dilate",
        mask_morphology_radius=1,
        mask_feather_sigma=1.0,
    )

    final_mask = result["layer_separation"][
        "subject_mask"
    ]

    assert np.any(
        (final_mask > 0.0)
        & (final_mask < 1.0)
    )
    assert final_mask[3, 3] > final_mask[0, 0]
    assert final_mask.min() >= 0.0
    assert final_mask.max() <= 1.0


def test_pipeline_build_from_image_accepts_product_profile(
    tmp_path,
):
    from PIL import Image

    from CORE.atlas_relief_product_profile import (
        AtlasReliefProductProfile,
    )

    path = tmp_path / "product-profile.png"

    image = Image.new(
        "L",
        (4, 4),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            32,
            64,
            96,
            128,
            64,
            96,
            128,
            192,
            96,
            128,
            192,
            255,
        ]
    )
    image.save(path)

    profile = AtlasReliefProductProfile(
        name="memorial-soft",
        form_sigma=2.5,
        detail_sigma=0.8,
        form_weight=1.10,
        detail_weight=0.25,
        micro_detail_weight=0.04,
        micro_detail_limit=0.02,
        depth_lower_percentile=2.0,
        depth_upper_percentile=98.0,
        depth_gamma=1.15,
        background_depth_range=(0.0, 0.35),
        foreground_depth_range=(0.65, 1.0),
        relief_height_mm=1.80,
        smoothing_sigma=0.50,
        smoothing_radius=2,
    )

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=40.0,
        depth_mm=40.0,
        product_profile=profile,
    )

    image_settings = result["image_settings"]
    relief_settings = result[
        "relief_result"
    ]["settings"]

    assert image_settings[
        "product_profile_name"
    ] == "memorial-soft"
    assert image_settings["form_sigma"] == 2.5
    assert image_settings["detail_sigma"] == 0.8
    assert image_settings["form_weight"] == 1.10
    assert image_settings["detail_weight"] == 0.25
    assert image_settings[
        "micro_detail_weight"
    ] == 0.04
    assert image_settings[
        "micro_detail_limit"
    ] == 0.02
    assert image_settings[
        "depth_lower_percentile"
    ] == 2.0
    assert image_settings[
        "depth_upper_percentile"
    ] == 98.0
    assert image_settings["depth_gamma"] == 1.15

    assert relief_settings[
        "relief_height_mm"
    ] == 1.80
    assert relief_settings[
        "smoothing_sigma"
    ] == 0.50
    assert relief_settings[
        "smoothing_radius"
    ] == 2


def test_pipeline_product_profile_overrides_scalar_settings(
    tmp_path,
):
    from PIL import Image

    from CORE.atlas_relief_product_profile import (
        AtlasReliefProductProfile,
    )

    path = tmp_path / "profile-override.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(path)

    profile = AtlasReliefProductProfile(
        name="caricature",
        form_sigma=3.0,
        detail_sigma=0.9,
        form_weight=1.20,
        detail_weight=0.45,
        relief_height_mm=2.40,
        smoothing_sigma=0.30,
        smoothing_radius=1,
    )

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=9.0,
        detail_sigma=4.0,
        form_weight=0.20,
        detail_weight=0.10,
        relief_height_mm=1.00,
        smoothing_sigma=1.50,
        smoothing_radius=4,
        product_profile=profile,
    )

    image_settings = result["image_settings"]
    relief_settings = result[
        "relief_result"
    ]["settings"]

    assert image_settings["form_sigma"] == 3.0
    assert image_settings["detail_sigma"] == 0.9
    assert image_settings["form_weight"] == 1.20
    assert image_settings["detail_weight"] == 0.45
    assert relief_settings[
        "relief_height_mm"
    ] == 2.40
    assert relief_settings[
        "smoothing_sigma"
    ] == 0.30
    assert relief_settings[
        "smoothing_radius"
    ] == 1


def test_pipeline_records_no_product_profile_by_default(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "no-product-profile.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(path)

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=2.0,
        detail_sigma=0.7,
    )

    assert result["image_settings"][
        "product_profile_name"
    ] is None


def test_pipeline_rejects_invalid_product_profile(
    tmp_path,
):
    from PIL import Image

    path = tmp_path / "invalid-product-profile.png"

    Image.new(
        "L",
        (3, 3),
        128,
    ).save(path)

    with pytest.raises(
        ValueError,
        match=(
            "product_profile must be an "
            "AtlasReliefProductProfile or None"
        ),
    ):
        AtlasReliefPipeline.build_from_image(
            path,
            width_mm=30.0,
            depth_mm=30.0,
            product_profile="caricature",
        )


def test_pipeline_product_profile_applies_layer_ranges(
    tmp_path,
):
    import numpy as np
    from PIL import Image

    from CORE.atlas_relief_product_profile import (
        AtlasReliefProductProfile,
    )

    path = tmp_path / "profile-layer-ranges.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    subject_mask = np.zeros(
        (3, 3),
        dtype=np.float64,
    )
    subject_mask[1, 1] = 1.0

    profile = AtlasReliefProductProfile(
        name="memorial-soft",
        form_sigma=2.0,
        detail_sigma=0.7,
        background_depth_range=(0.05, 0.25),
        foreground_depth_range=(0.75, 0.95),
    )

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        subject_mask=subject_mask,
        product_profile=profile,
    )

    separation = result["layer_separation"]

    assert separation["background_range"] == (
        0.05,
        0.25,
    )
    assert separation["foreground_range"] == (
        0.75,
        0.95,
    )


def test_pipeline_build_from_image_applies_preprocessors(
    tmp_path,
):
    import numpy as np
    from PIL import Image

    path = tmp_path / "preprocessor-chain.png"

    image = Image.new(
        "L",
        (3, 3),
    )
    image.putdata(
        [
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            255,
        ]
    )
    image.save(path)

    seen = {}

    def invert(values):
        seen["input"] = values.copy()
        result = 1.0 - values
        seen["output"] = result.copy()
        return result

    result = AtlasReliefPipeline.build_from_image(
        path,
        width_mm=30.0,
        depth_mm=30.0,
        form_sigma=2.0,
        detail_sigma=0.7,
        preprocessors=(invert,),
    )

    assert np.allclose(
        result["preprocessed_luminance"],
        seen["output"],
    )
    reconstructed_source = (
        result["multiscale"]["form"]
        + result["multiscale"]["detail"]
        + result["multiscale"]["micro_detail"]
    )

    assert np.allclose(
        reconstructed_source,
        seen["output"],
    )
    assert result["image_settings"][
        "preprocessor_count"
    ] == 1
