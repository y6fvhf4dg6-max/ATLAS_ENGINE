from pathlib import Path

import numpy as np
import pytest

from CORE.atlas_architectural_relief_depth_composer import (
    AtlasArchitecturalReliefDepthComposer,
    AtlasArchitecturalReliefDepthProfile,
)
from CORE.atlas_architectural_relief_detail_scale_filter import (
    AtlasArchitecturalReliefDetailScaleFilter,
    AtlasArchitecturalReliefDetailScaleProfile,
)
from CORE.atlas_architectural_relief_input import (
    AtlasArchitecturalReliefInput,
    AtlasArchitecturalReliefSemanticMaskSpec,
)
from CORE.atlas_architectural_relief_mesh_producer import (
    AtlasArchitecturalReliefMeshProducer,
)
from CORE.atlas_architectural_relief_physical_profile import (
    AtlasArchitecturalReliefPhysicalProfile,
)
from CORE.atlas_architectural_relief_quality_report import (
    AtlasArchitecturalReliefQualityReport,
)
from CORE.atlas_architectural_relief_region_analyzer import (
    AtlasArchitecturalReliefRegionAnalyzer,
)
from CORE.atlas_architectural_relief_structure_preserver import (
    AtlasArchitecturalReliefStructurePreserver,
    AtlasArchitecturalReliefStructureProfile,
)
from CORE.atlas_dalyan_relief_semantic_masks import (
    AtlasDalyanReliefSemanticMasks,
)
from CORE.atlas_relief_depth_compressor import (
    AtlasReliefDepthCompressor,
)
from CORE.atlas_relief_product_profile_catalog import (
    ROCK_CARVED_LANDMARK,
)
from CORE.atlas_relief_semantic_mask_set import (
    AtlasReliefSemanticMaskSet,
)
from CORE.atlas_rock_relief_production_preset import (
    DALYAN_ROCK_TOMBS_PRODUCTION_PRESET,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_PATH = (
    PROJECT_ROOT
    / "Data"
    / "RELIEF"
    / "dalyan_rock_tombs"
    / "rock_tombs_relief_working_240px.png"
)

WIDTH_MM = 80.0
DEPTH_MM = 50.0
BASE_THICKNESS_MM = 0.8

REFERENCE_ROWS = 99
REFERENCE_COLUMNS = 240

REFERENCE_MAXIMUM_SAMPLE_SPACING_MM = max(
    WIDTH_MM / (REFERENCE_COLUMNS - 1),
    DEPTH_MM / (REFERENCE_ROWS - 1),
)


@pytest.fixture(scope="module")
def dalyan_architectural_result():
    semantic_contract = (
        AtlasDalyanReliefSemanticMasks.build(
            project_root=PROJECT_ROOT
        )
    )

    semantic_spec = (
        AtlasArchitecturalReliefSemanticMaskSpec(
            expected_shape=(
                semantic_contract["shape"]
            ),
            default_material=(
                semantic_contract[
                    "default_material"
                ]
            ),
            mask_paths=(
                semantic_contract[
                    "mask_paths"
                ]
            ),
            threshold=128,
        )
    )

    architectural_input = (
        AtlasArchitecturalReliefInput(
            image_path=SOURCE_PATH,
            width_mm=WIDTH_MM,
            depth_mm=DEPTH_MM,
            architectural_kind=(
                "rock_carved_landmark"
            ),
            product_profile=(
                ROCK_CARVED_LANDMARK
            ),
            preprocessors=(
                DALYAN_ROCK_TOMBS_PRODUCTION_PRESET
                .preprocessors
            ),
            semantic_masks=semantic_spec,
        )
    )

    request = (
        architectural_input
        .to_pipeline_request()
    )

    legacy_reference = (
        DALYAN_ROCK_TOMBS_PRODUCTION_PRESET
        .build_from_image(
            request["image_path"],
            width_mm=(
                request[
                    "pipeline_kwargs"
                ]["width_mm"]
            ),
            depth_mm=(
                request[
                    "pipeline_kwargs"
                ]["depth_mm"]
            ),
        )
    )

    semantic_set = (
        AtlasReliefSemanticMaskSet.load(
            **request[
                "semantic_mask_kwargs"
            ]
        )
    )

    region_analysis = (
        AtlasArchitecturalReliefRegionAnalyzer
        .analyze(
            material_id_map=(
                semantic_set[
                    "material_id_map"
                ]
            ),
            material_names=(
                semantic_set[
                    "material_names"
                ]
            ),
        )
    )

    profile_arguments = (
        ROCK_CARVED_LANDMARK
        .to_pipeline_kwargs()
    )

    detail_filter = (
        AtlasArchitecturalReliefDetailScaleFilter
        .filter(
            detail_map=(
                legacy_reference[
                    "multiscale"
                ]["detail"]
            ),
            width_mm=WIDTH_MM,
            depth_mm=DEPTH_MM,
            profile=(
                AtlasArchitecturalReliefDetailScaleProfile()
            ),
        )
    )

    depth_profile = (
        AtlasArchitecturalReliefDepthProfile(
            form_weight=(
                profile_arguments[
                    "form_weight"
                ]
            ),
            detail_weight=(
                profile_arguments[
                    "detail_weight"
                ]
            ),
            micro_detail_weight=(
                profile_arguments[
                    "micro_detail_weight"
                ]
            ),
            micro_detail_limit=(
                profile_arguments[
                    "micro_detail_limit"
                ]
            ),
        )
    )

    depth_composition = (
        AtlasArchitecturalReliefDepthComposer
        .compose(
            form=(
                legacy_reference[
                    "multiscale"
                ]["form"]
            ),
            detail=(
                detail_filter[
                    "filtered_detail"
                ]
            ),
            micro_detail=(
                legacy_reference[
                    "multiscale"
                ]["micro_detail"]
            ),
            material_id_map=(
                semantic_set[
                    "material_id_map"
                ]
            ),
            material_names=(
                semantic_set[
                    "material_names"
                ]
            ),
            default_profile=depth_profile,
            material_profiles={},
        )
    )

    depth_compression = (
        AtlasReliefDepthCompressor.compress(
            depth_composition[
                "depth_candidate"
            ],
            lower_percentile=(
                profile_arguments[
                    "depth_lower_percentile"
                ]
            ),
            upper_percentile=(
                profile_arguments[
                    "depth_upper_percentile"
                ]
            ),
            gamma=(
                profile_arguments[
                    "depth_gamma"
                ]
            ),
        )
    )

    protection_map = (
        AtlasArchitecturalReliefStructurePreserver
        .build_protection_map(
            feature_masks={
                "tomb_facade": (
                    semantic_set[
                        "region_masks"
                    ]["tomb_facade"]
                ),
            },
            feature_weights={
                "tomb_facade": 1.0,
            },
        )
    )

    structure_preservation = (
        AtlasArchitecturalReliefStructurePreserver
        .preserve(
            depth_candidate=(
                depth_compression[
                    "compressed_depth"
                ]
            ),
            structure_reference=(
                legacy_reference[
                    "depth_compression"
                ]["compressed_depth"]
            ),
            protection_map=(
                protection_map
            ),
            profile=(
                AtlasArchitecturalReliefStructureProfile()
            ),
            clamp_output=True,
        )
    )

    physical_profile = (
        AtlasArchitecturalReliefPhysicalProfile(
            name=(
                "dalyan-architectural-reference-v1"
            ),
            base_thickness_mm=(
                BASE_THICKNESS_MM
            ),
            relief_height_mm=(
                profile_arguments[
                    "relief_height_mm"
                ]
            ),
            target_sample_spacing_mm=(
                REFERENCE_MAXIMUM_SAMPLE_SPACING_MM
            ),
        )
    )

    mesh_production = (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=(
                structure_preservation[
                    "preserved_depth"
                ]
            ),
            width_mm=WIDTH_MM,
            depth_mm=DEPTH_MM,
            physical_profile=(
                physical_profile
            ),
        )
    )

    quality_report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            mesh_production
        )
    )

    return {
        "request": request,
        "legacy_reference": (
            legacy_reference
        ),
        "semantic_set": semantic_set,
        "region_analysis": region_analysis,
        "detail_filter": detail_filter,
        "depth_composition": depth_composition,
        "depth_compression": depth_compression,
        "structure_preservation": (
            structure_preservation
        ),
        "mesh_production": (
            mesh_production
        ),
        "quality_report": quality_report,
    }


def test_dalyan_reference_uses_locked_real_assets(
    dalyan_architectural_result,
):
    result = dalyan_architectural_result
    request = result["request"]

    assert SOURCE_PATH.is_file()
    assert request[
        "architectural_kind"
    ] == "rock_carved_landmark"

    assert request["pipeline_kwargs"][
        "product_profile"
    ] is ROCK_CARVED_LANDMARK

    assert request["pipeline_kwargs"][
        "preprocessors"
    ] == (
        DALYAN_ROCK_TOMBS_PRODUCTION_PRESET
        .preprocessors
    )

    assert result["legacy_reference"][
        "image_input"
    ]["luminance"].shape == (
        REFERENCE_ROWS,
        REFERENCE_COLUMNS,
    )


def test_dalyan_real_semantic_regions_are_complete(
    dalyan_architectural_result,
):
    semantic_set = (
        dalyan_architectural_result[
            "semantic_set"
        ]
    )
    analysis = (
        dalyan_architectural_result[
            "region_analysis"
        ]
    )

    assert semantic_set[
        "material_names"
    ] == (
        "rock",
        "vegetation",
        "tomb_facade",
    )

    assert analysis.shape == (
        REFERENCE_ROWS,
        REFERENCE_COLUMNS,
    )
    assert analysis.total_pixel_count == 23760

    assert analysis.region_for_material(
        "rock"
    ).pixel_count == 12125

    assert analysis.region_for_material(
        "vegetation"
    ).pixel_count == 3006

    assert analysis.region_for_material(
        "tomb_facade"
    ).pixel_count == 8629

    assert sum(
        region.pixel_count
        for region in analysis.regions
    ) == analysis.total_pixel_count


def test_dalyan_architectural_depth_chain_is_normalized(
    dalyan_architectural_result,
):
    result = dalyan_architectural_result

    assert result["depth_composition"][
        "depth_candidate"
    ].shape == (
        REFERENCE_ROWS,
        REFERENCE_COLUMNS,
    )

    preserved = result[
        "structure_preservation"
    ]["preserved_depth"]

    assert preserved.dtype == np.float64
    assert preserved.shape == (
        REFERENCE_ROWS,
        REFERENCE_COLUMNS,
    )
    assert float(
        preserved.min()
    ) >= 0.0
    assert float(
        preserved.max()
    ) <= 1.0

    assert result["detail_filter"][
        "component_count"
    ] >= result["detail_filter"][
        "retained_component_count"
    ]


def test_dalyan_architectural_mesh_uses_reference_spacing_limit(
    dalyan_architectural_result,
):
    production = (
        dalyan_architectural_result[
            "mesh_production"
        ]
    )

    mesh = production["mesh"]
    plan = production[
        "physical_plan"
    ]

    assert plan[
        "target_sample_spacing_mm"
    ] == pytest.approx(
        REFERENCE_MAXIMUM_SAMPLE_SPACING_MM
    )

    assert mesh["row_count"] == 99
    assert mesh["column_count"] == 158
    assert production[
        "triangle_count"
    ] == 62564
    assert production[
        "expected_triangle_count"
    ] == 62564

    assert mesh["width_mm"] == pytest.approx(
        80.0
    )
    assert mesh["depth_mm"] == pytest.approx(
        50.0
    )
    assert mesh[
        "base_thickness_mm"
    ] == pytest.approx(0.8)
    assert mesh[
        "relief_height_mm"
    ] == pytest.approx(1.8)


def test_dalyan_architectural_mesh_has_printable_topology(
    dalyan_architectural_result,
):
    production = (
        dalyan_architectural_result[
            "mesh_production"
        ]
    )
    quality = (
        dalyan_architectural_result[
            "quality_report"
        ]
    )
    general = quality[
        "general_quality_report"
    ]

    assert production[
        "is_printable_topology"
    ] is True
    assert general[
        "open_edge_count"
    ] == 0
    assert general[
        "non_manifold_edge_count"
    ] == 0

    assert quality[
        "physical_dimensions_match"
    ] is True
    assert quality[
        "total_height_matches"
    ] is True
    assert quality[
        "triangle_count_matches"
    ] is True

    assert quality["status"] in {
        "PASS",
        "WARN",
    }
    assert quality[
        "is_print_ready"
    ] is (
        quality["status"] == "PASS"
    )

    assert not any(
        issue["severity"] == "FAIL"
        for issue in quality["issues"]
    )
