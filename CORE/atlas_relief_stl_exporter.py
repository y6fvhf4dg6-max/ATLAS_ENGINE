from __future__ import annotations

from pathlib import Path
from typing import Any

from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasReliefSTLExporter:
    """
    Exports the closed relief mesh contained in an
    AtlasReliefPipeline image result.
    """

    DEFAULT_SOLID_NAME = "ATLAS_RELIEF"

    @classmethod
    def export_pipeline_result(
        cls,
        *,
        pipeline_result: dict[str, Any],
        output_path,
        solid_name: str = DEFAULT_SOLID_NAME,
    ):
        resolved_solid_name = str(solid_name).strip()

        if not resolved_solid_name:
            raise ValueError(
                "solid_name must not be empty."
            )

        mesh = cls._extract_relief_mesh(
            pipeline_result
        )

        resolved_output_path = Path(output_path)
        resolved_output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return AtlasSTLWriter.write(
            meshes=[mesh],
            output_path=resolved_output_path,
            solid_name=resolved_solid_name,
        )

    @staticmethod
    def _extract_relief_mesh(
        pipeline_result: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(pipeline_result, dict):
            raise ValueError(
                "pipeline_result must contain a "
                "relief mesh."
            )

        relief_result = pipeline_result.get(
            "relief_result"
        )

        if not isinstance(relief_result, dict):
            raise ValueError(
                "pipeline_result must contain a "
                "relief mesh."
            )

        mesh = relief_result.get("mesh")

        if not isinstance(mesh, dict):
            raise ValueError(
                "pipeline_result must contain a "
                "relief mesh."
            )

        triangles = mesh.get("triangles")

        if triangles is None:
            raise ValueError(
                "pipeline_result must contain a "
                "relief mesh."
            )

        return mesh
