from CORE.atlas_terrain_contour_terrace_builder import (
    AtlasTerrainContourTerraceBuilder,
)
from CORE.atlas_terrain_contour_band_builder import (
    AtlasTerrainContourBandBuilder,
)
from CORE.atlas_terrain_contour_mesh_builder import (
    AtlasTerrainContourMeshBuilder,
)


class AtlasTerrainContourBuilder:

    @staticmethod
    def build(
        top_points,
        base_z,
        contour_step_mm,
        band_half_width_mm,
    ):
        contours = []

        if top_points:
            contours = (
                AtlasTerrainContourTerraceBuilder
                .extract_contours(
                    top_points=top_points,
                    contour_step_mm=contour_step_mm,
                )
            )

        contour_bands = []

        for contour in contours:
            contour_bands.append(
                AtlasTerrainContourBandBuilder.build_band(
                    polyline=contour,
                    half_width_mm=band_half_width_mm,
                )
            )

        triangles = (
            AtlasTerrainContourMeshBuilder.build(
                contour_bands=contour_bands,
            )
        )

        return {
            "triangles": triangles,
            "metadata": {
                "contour_step_mm": float(contour_step_mm),
                "band_half_width_mm": float(
                    band_half_width_mm
                ),
                "contour_count": len(contours),
                "band_count": len(contour_bands),
            },
        }
