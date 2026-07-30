from __future__ import annotations

from typing import Any

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)
from CORE.atlas_relief_depth_composer import (
    AtlasReliefDepthComposer,
)
from CORE.atlas_relief_depth_compressor import (
    AtlasReliefDepthCompressor,
)
from CORE.atlas_relief_image_input import (
    AtlasReliefImageInput,
)
from CORE.atlas_relief_layer_separator import (
    AtlasReliefLayerSeparator,
)
from CORE.atlas_relief_mask_input import (
    AtlasReliefMaskInput,
)
from CORE.atlas_relief_mask_morphology import (
    AtlasReliefMaskMorphology,
)
from CORE.atlas_relief_mask_processor import (
    AtlasReliefMaskProcessor,
)
from CORE.atlas_relief_multiscale_decomposer import (
    AtlasReliefMultiscaleDecomposer,
)
from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)
from CORE.atlas_relief_preprocessor_chain import (
    AtlasReliefPreprocessorChain,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)
from CORE.atlas_relief_risk_profile import (
    AtlasReliefRiskProfile,
)
from CORE.atlas_relief_sampling_plan import (
    AtlasReliefSamplingPlan,
)


class AtlasReliefPipeline:
    """
    ATLAS Relief Pipeline v0.1

    Deterministic end-to-end relief production:

    numeric image data
    -> normalization
    -> optional bilinear resampling
    -> optional Gaussian smoothing
    -> closed relief mesh
    -> structural quality report
    """

    @staticmethod
    def build_from_image(
        image_path: Any,
        *,
        width_mm: float,
        depth_mm: float,
        form_sigma: float | None = None,
        detail_sigma: float | None = None,
        form_weight: float = 1.0,
        detail_weight: float = 0.35,
        micro_detail_weight: float = 0.10,
        micro_detail_limit: float = 0.05,
        depth_lower_percentile: float = 1.0,
        depth_upper_percentile: float = 99.0,
        depth_gamma: float = 1.0,
        subject_mask: Any | None = None,
        mask_path: Any | None = None,
        mask_use_alpha: bool = False,
        mask_threshold: float | None = None,
        mask_feather_sigma: float = 0.0,
        mask_morphology_operation: str | None = None,
        mask_morphology_radius: int = 0,
        mask_morphology_threshold: float = 0.5,
        background_depth_range: Any = (0.0, 0.40),
        foreground_depth_range: Any = (0.60, 1.0),
        alpha_background_luminance: float = 1.0,
        product_profile: (
            AtlasReliefProductProfile | None
        ) = None,
        preprocessors: Any = (),
        **pipeline_arguments: Any,
    ) -> dict:
        product_profile_name = None

        if product_profile is not None:
            if not isinstance(
                product_profile,
                AtlasReliefProductProfile,
            ):
                raise ValueError(
                    "product_profile must be an "
                    "AtlasReliefProductProfile or None."
                )

            profile_arguments = (
                product_profile.to_pipeline_kwargs()
            )
            product_profile_name = (
                product_profile.name
            )

            form_sigma = profile_arguments[
                "form_sigma"
            ]
            detail_sigma = profile_arguments[
                "detail_sigma"
            ]
            form_weight = profile_arguments[
                "form_weight"
            ]
            detail_weight = profile_arguments[
                "detail_weight"
            ]
            micro_detail_weight = (
                profile_arguments[
                    "micro_detail_weight"
                ]
            )
            micro_detail_limit = (
                profile_arguments[
                    "micro_detail_limit"
                ]
            )
            depth_lower_percentile = (
                profile_arguments[
                    "depth_lower_percentile"
                ]
            )
            depth_upper_percentile = (
                profile_arguments[
                    "depth_upper_percentile"
                ]
            )
            depth_gamma = profile_arguments[
                "depth_gamma"
            ]
            background_depth_range = (
                profile_arguments[
                    "background_depth_range"
                ]
            )
            foreground_depth_range = (
                profile_arguments[
                    "foreground_depth_range"
                ]
            )

            pipeline_arguments[
                "relief_height_mm"
            ] = profile_arguments[
                "relief_height_mm"
            ]
            pipeline_arguments[
                "smoothing_sigma"
            ] = profile_arguments[
                "smoothing_sigma"
            ]
            pipeline_arguments[
                "smoothing_radius"
            ] = profile_arguments[
                "smoothing_radius"
            ]

        if (
            form_sigma is None
            or detail_sigma is None
        ):
            raise ValueError(
                "form_sigma and detail_sigma are "
                "required when product_profile is "
                "not provided."
            )

        image_input = AtlasReliefImageInput.load(
            image_path,
            alpha_background_luminance=(
                alpha_background_luminance
            ),
        )

        preprocessor_sequence = tuple(
            preprocessors
        )

        preprocessed_luminance = (
            AtlasReliefPreprocessorChain.apply(
                image_input["luminance"],
                preprocessors=(
                    preprocessor_sequence
                ),
            )
        )

        multiscale = (
            AtlasReliefMultiscaleDecomposer
            .decompose(
                preprocessed_luminance,
                form_sigma=form_sigma,
                detail_sigma=detail_sigma,
            )
        )

        depth_composition = (
            AtlasReliefDepthComposer.compose(
                form=multiscale["form"],
                detail=multiscale["detail"],
                micro_detail=(
                    multiscale["micro_detail"]
                ),
                form_weight=form_weight,
                detail_weight=detail_weight,
                micro_detail_weight=(
                    micro_detail_weight
                ),
                micro_detail_limit=(
                    micro_detail_limit
                ),
            )
        )

        depth_compression = (
            AtlasReliefDepthCompressor.compress(
                depth_composition[
                    "depth_candidate"
                ],
                lower_percentile=(
                    depth_lower_percentile
                ),
                upper_percentile=(
                    depth_upper_percentile
                ),
                gamma=depth_gamma,
            )
        )

        if (
            subject_mask is not None
            and mask_path is not None
        ):
            raise ValueError(
                "subject_mask and mask_path cannot "
                "be used together."
            )

        mask_input = None
        effective_subject_mask = subject_mask
        mask_source = None

        if mask_path is not None:
            mask_input = AtlasReliefMaskInput.load(
                mask_path,
                use_alpha=mask_use_alpha,
            )
            effective_subject_mask = mask_input["mask"]
            mask_source = "file"
        elif subject_mask is not None:
            mask_source = "array"

        mask_processing = None
        mask_morphology = None
        mask_feathering = None

        if effective_subject_mask is not None:
            preprocessing_feather_sigma = (
                0.0
                if mask_morphology_operation
                is not None
                else mask_feather_sigma
            )

            mask_processing = (
                AtlasReliefMaskProcessor.process(
                    effective_subject_mask,
                    threshold=mask_threshold,
                    feather_sigma=(
                        preprocessing_feather_sigma
                    ),
                )
            )
            effective_subject_mask = (
                mask_processing[
                    "processed_mask"
                ]
            )

        if mask_morphology_operation is not None:
            if effective_subject_mask is None:
                raise ValueError(
                    "mask morphology requires a "
                    "subject mask."
                )

            mask_morphology = (
                AtlasReliefMaskMorphology.apply(
                    effective_subject_mask,
                    operation=(
                        mask_morphology_operation
                    ),
                    radius=(
                        mask_morphology_radius
                    ),
                    threshold=(
                        mask_morphology_threshold
                    ),
                )
            )
            effective_subject_mask = (
                mask_morphology[
                    "processed_mask"
                ]
            )

            if mask_feather_sigma > 0.0:
                mask_feathering = (
                    AtlasReliefMaskProcessor.process(
                        effective_subject_mask,
                        feather_sigma=(
                            mask_feather_sigma
                        ),
                    )
                )
                effective_subject_mask = (
                    mask_feathering[
                        "processed_mask"
                    ]
                )

        layer_separation = None
        relief_depth = depth_compression[
            "compressed_depth"
        ]

        if effective_subject_mask is not None:
            layer_separation = (
                AtlasReliefLayerSeparator.separate(
                    relief_depth,
                    effective_subject_mask,
                    background_range=(
                        background_depth_range
                    ),
                    foreground_range=(
                        foreground_depth_range
                    ),
                )
            )

            relief_depth = layer_separation[
                "separated_depth"
            ]

        relief_result = AtlasReliefPipeline.build(
            relief_depth,
            width_mm=width_mm,
            depth_mm=depth_mm,
            **pipeline_arguments,
        )

        return {
            "type": "relief_image_pipeline_result",
            "image_input": image_input,
            "preprocessed_luminance": (
                preprocessed_luminance
            ),
            "multiscale": multiscale,
            "depth_composition": depth_composition,
            "depth_compression": depth_compression,
            "mask_input": mask_input,
            "mask_processing": mask_processing,
            "mask_morphology": mask_morphology,
            "mask_feathering": mask_feathering,
            "layer_separation": layer_separation,
            "relief_result": relief_result,
            "image_settings": {
                "product_profile_name": (
                    product_profile_name
                ),
                "preprocessor_count": len(
                    preprocessor_sequence
                ),
                "form_sigma": multiscale[
                    "form_sigma"
                ],
                "detail_sigma": multiscale[
                    "detail_sigma"
                ],
                "form_weight": depth_composition[
                    "form_weight"
                ],
                "detail_weight": depth_composition[
                    "detail_weight"
                ],
                "micro_detail_weight": (
                    depth_composition[
                        "micro_detail_weight"
                    ]
                ),
                "micro_detail_limit": (
                    depth_composition[
                        "micro_detail_limit"
                    ]
                ),
                "depth_lower_percentile": (
                    depth_compression[
                        "lower_percentile"
                    ]
                ),
                "depth_upper_percentile": (
                    depth_compression[
                        "upper_percentile"
                    ]
                ),
                "depth_gamma": depth_compression[
                    "gamma"
                ],
                "has_subject_mask": (
                    effective_subject_mask is not None
                ),
                "mask_source": mask_source,
                "mask_use_alpha": (
                    mask_input["use_alpha"]
                    if mask_input is not None
                    else False
                ),
                "mask_threshold": (
                    None
                    if mask_processing is None
                    else mask_processing[
                        "threshold"
                    ]
                ),
                "mask_feather_sigma": (
                    0.0
                    if mask_processing is None
                    else float(
                        mask_feather_sigma
                    )
                ),
                "mask_morphology_operation": (
                    None
                    if mask_morphology is None
                    else mask_morphology[
                        "operation"
                    ]
                ),
                "mask_morphology_radius": (
                    0
                    if mask_morphology is None
                    else mask_morphology[
                        "radius"
                    ]
                ),
                "mask_morphology_threshold": (
                    None
                    if mask_morphology is None
                    else mask_morphology[
                        "threshold"
                    ]
                ),
                "background_depth_range": (
                    None
                    if layer_separation is None
                    else layer_separation[
                        "background_range"
                    ]
                ),
                "foreground_depth_range": (
                    None
                    if layer_separation is None
                    else layer_separation[
                        "foreground_range"
                    ]
                ),
                "alpha_background_luminance": (
                    image_input[
                        "alpha_background_luminance"
                    ]
                ),
            },
        }

    @staticmethod
    def build(
        values: Any,
        *,
        width_mm: float,
        depth_mm: float,
        base_thickness_mm: float = 0.80,
        relief_height_mm: float = 2.00,
        invert: bool = False,
        black_point: float = 0.0,
        white_point: float = 1.0,
        gamma: float = 1.0,
        target_rows: int | None = None,
        target_columns: int | None = None,
        smoothing_sigma: float | None = None,
        smoothing_radius: int | None = None,
        origin_x: float = 0.0,
        origin_y: float = 0.0,
        origin_z: float = 0.0,
        warning_slope_degrees: float = 55.0,
        critical_slope_degrees: float = 75.0,
        warning_slope_area_percent: float = 0.0,
        critical_slope_area_percent: float = 0.0,
        risk_profile: AtlasReliefRiskProfile | None = None,
        sampling_plan: AtlasReliefSamplingPlan | None = None,
    ) -> dict:
        if sampling_plan is not None:
            if (
                target_rows is not None
                or target_columns is not None
            ):
                raise ValueError(
                    "sampling_plan cannot be combined with "
                    "target_rows or target_columns."
                )

            if (
                sampling_plan.width_mm
                != float(width_mm)
                or sampling_plan.depth_mm
                != float(depth_mm)
            ):
                raise ValueError(
                    "sampling_plan dimensions must match "
                    "pipeline dimensions."
                )

            sampling_arguments = (
                sampling_plan.to_pipeline_kwargs()
            )
            target_rows = sampling_arguments[
                "target_rows"
            ]
            target_columns = sampling_arguments[
                "target_columns"
            ]

        if risk_profile is not None:
            risk_arguments = (
                risk_profile.to_pipeline_kwargs()
            )
            warning_slope_degrees = risk_arguments[
                "warning_slope_degrees"
            ]
            critical_slope_degrees = risk_arguments[
                "critical_slope_degrees"
            ]
            warning_slope_area_percent = risk_arguments[
                "warning_slope_area_percent"
            ]
            critical_slope_area_percent = risk_arguments[
                "critical_slope_area_percent"
            ]

        normalized = AtlasHeightMapEngine.normalize(
            values,
            invert=invert,
        )

        contrast_remapped = (
            AtlasHeightMapEngine
            .remap_contrast(
                normalized,
                black_point=black_point,
                white_point=white_point,
                gamma=gamma,
            )
        )

        if (
            target_rows is None
            and target_columns is None
        ):
            resampled = contrast_remapped.copy()
        elif (
            target_rows is not None
            and target_columns is not None
        ):
            resampled = (
                AtlasHeightMapEngine
                .resample_bilinear(
                    contrast_remapped,
                    target_rows=target_rows,
                    target_columns=target_columns,
                )
            )
        else:
            raise ValueError(
                "target_rows and target_columns "
                "must be provided together."
            )

        if smoothing_sigma is None:
            processed = resampled.copy()

            if smoothing_radius is not None:
                raise ValueError(
                    "smoothing_radius requires "
                    "smoothing_sigma."
                )
        else:
            processed = (
                AtlasHeightMapEngine
                .smooth_gaussian(
                    resampled,
                    sigma=smoothing_sigma,
                    radius=smoothing_radius,
                )
            )

        mesh = AtlasReliefMeshBuilder.build(
            processed,
            width_mm=width_mm,
            depth_mm=depth_mm,
            base_thickness_mm=(
                base_thickness_mm
            ),
            relief_height_mm=relief_height_mm,
            origin_x=origin_x,
            origin_y=origin_y,
            origin_z=origin_z,
        )

        quality_report = (
            AtlasReliefQualityReport.build(
                mesh,
                warning_slope_degrees=(
                    warning_slope_degrees
                ),
                critical_slope_degrees=(
                    critical_slope_degrees
                ),
                warning_slope_area_percent=(
                    warning_slope_area_percent
                ),
                critical_slope_area_percent=(
                    critical_slope_area_percent
                ),
            )
        )

        return {
            "type": "relief_pipeline_result",
            "normalized_height_map": normalized,
            "contrast_height_map": contrast_remapped,
            "resampled_height_map": resampled,
            "processed_height_map": processed,
            "mesh": mesh,
            "quality_report": quality_report,
            "settings": {
                "invert": bool(invert),
                "black_point": float(
                    black_point
                ),
                "white_point": float(
                    white_point
                ),
                "gamma": float(gamma),
                "target_rows": (
                    processed.shape[0]
                ),
                "target_columns": (
                    processed.shape[1]
                ),
                "target_sample_spacing_mm": (
                    None
                    if sampling_plan is None
                    else (
                        sampling_plan
                        .target_sample_spacing_mm
                    )
                ),
                "effective_spacing_x_mm": (
                    None
                    if sampling_plan is None
                    else (
                        sampling_plan
                        .effective_spacing_x_mm
                    )
                ),
                "effective_spacing_y_mm": (
                    None
                    if sampling_plan is None
                    else (
                        sampling_plan
                        .effective_spacing_y_mm
                    )
                ),
                "sample_count": (
                    None
                    if sampling_plan is None
                    else sampling_plan.sample_count
                ),
                "expected_triangle_count": (
                    None
                    if sampling_plan is None
                    else (
                        sampling_plan
                        .total_triangle_count
                    )
                ),
                "smoothing_sigma": (
                    smoothing_sigma
                ),
                "smoothing_radius": (
                    smoothing_radius
                ),
                "width_mm": float(width_mm),
                "depth_mm": float(depth_mm),
                "base_thickness_mm": float(
                    base_thickness_mm
                ),
                "relief_height_mm": float(
                    relief_height_mm
                ),
                "warning_slope_degrees": float(
                    warning_slope_degrees
                ),
                "critical_slope_degrees": float(
                    critical_slope_degrees
                ),
                "warning_slope_area_percent": float(
                    warning_slope_area_percent
                ),
                "critical_slope_area_percent": float(
                    critical_slope_area_percent
                ),
                "risk_profile_name": (
                    None
                    if risk_profile is None
                    else risk_profile.name
                ),
                "origin": (
                    float(origin_x),
                    float(origin_y),
                    float(origin_z),
                ),
            },
        }
