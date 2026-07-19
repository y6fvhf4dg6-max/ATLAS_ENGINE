from __future__ import annotations

from typing import Any

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)
from CORE.atlas_relief_depth_composer import (
    AtlasReliefDepthComposer,
)
from CORE.atlas_relief_image_input import (
    AtlasReliefImageInput,
)
from CORE.atlas_relief_multiscale_decomposer import (
    AtlasReliefMultiscaleDecomposer,
)
from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
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
        form_sigma: float,
        detail_sigma: float,
        form_weight: float = 1.0,
        detail_weight: float = 0.35,
        micro_detail_weight: float = 0.10,
        micro_detail_limit: float = 0.05,
        alpha_background_luminance: float = 1.0,
        **pipeline_arguments: Any,
    ) -> dict:
        image_input = AtlasReliefImageInput.load(
            image_path,
            alpha_background_luminance=(
                alpha_background_luminance
            ),
        )

        multiscale = (
            AtlasReliefMultiscaleDecomposer
            .decompose(
                image_input["luminance"],
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

        relief_result = AtlasReliefPipeline.build(
            depth_composition["depth_candidate"],
            width_mm=width_mm,
            depth_mm=depth_mm,
            **pipeline_arguments,
        )

        return {
            "type": "relief_image_pipeline_result",
            "image_input": image_input,
            "multiscale": multiscale,
            "depth_composition": depth_composition,
            "relief_result": relief_result,
            "image_settings": {
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
