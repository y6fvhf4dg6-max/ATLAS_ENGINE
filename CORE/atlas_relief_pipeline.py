from __future__ import annotations

from typing import Any

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)
from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
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
    ) -> dict:
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
                "origin": (
                    float(origin_x),
                    float(origin_y),
                    float(origin_z),
                ),
            },
        }
