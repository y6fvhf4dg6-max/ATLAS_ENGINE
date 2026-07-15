"""
ATLAS Ancient Theatre Stage Facade Builder v0.1

Antik tiyatro stage meshinin cavea'ya bakan ön cephesinde
tekrarlanan kemerli mimari panel ritmi üretir.

Bu builder:
- belirli bir tiyatro adına bağlı değildir,
- OSM kimliği veya koordinat hard-code etmez,
- cephe boyutlarından satır ve sütun sayısını türetir,
- genel AtlasFacadePanelBuilder bileşenini kullanır.

Gerçek boolean açıklık açılmaz.
Her kemer cepheye kısmen gömülen ayrı kapalı manifold
component mesh olarak korunur.
"""

from math import hypot

from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasAncientTheatreStageFacadeBuilder:
    DEFAULT_TARGET_COLUMN_SPACING_MM = 2.00
    DEFAULT_TARGET_ROW_HEIGHT_MM = 2.20

    DEFAULT_MIN_COLUMNS = 3
    DEFAULT_MAX_COLUMNS = 14

    DEFAULT_MIN_ROWS = 1
    DEFAULT_MAX_ROWS = 3

    DEFAULT_PANEL_WIDTH_RATIO = 0.58
    DEFAULT_PANEL_HEIGHT_RATIO = 0.66
    DEFAULT_ARCH_HEIGHT_RATIO = 0.42

    DEFAULT_HORIZONTAL_MARGIN_RATIO = 0.05
    DEFAULT_VERTICAL_MARGIN_RATIO = 0.08

    DEFAULT_DEPTH_MM = 0.28
    DEFAULT_EMBED_MM = 0.07
    DEFAULT_ARCH_SEGMENTS = 6

    @staticmethod
    def build(
        stage_mesh,
        target_column_spacing_mm=None,
        target_row_height_mm=None,
        min_columns=None,
        max_columns=None,
        min_rows=None,
        max_rows=None,
        panel_width_ratio=None,
        panel_height_ratio=None,
        arch_height_ratio=None,
        horizontal_margin_ratio=None,
        vertical_margin_ratio=None,
        depth_mm=None,
        embed_mm=None,
        arch_segments=None,
    ):
        if not stage_mesh:
            return None

        wall_quad = stage_mesh.get(
            "stage_front_wall_quad"
        )

        if (
            not wall_quad
            or len(wall_quad) != 4
        ):
            return None

        wall_width_mm = hypot(
            wall_quad[1][0]
            - wall_quad[0][0],
            wall_quad[1][1]
            - wall_quad[0][1],
        )

        left_height_mm = (
            (
                wall_quad[3][0]
                - wall_quad[0][0]
            )
            ** 2
            + (
                wall_quad[3][1]
                - wall_quad[0][1]
            )
            ** 2
            + (
                wall_quad[3][2]
                - wall_quad[0][2]
            )
            ** 2
        ) ** 0.5

        right_height_mm = (
            (
                wall_quad[2][0]
                - wall_quad[1][0]
            )
            ** 2
            + (
                wall_quad[2][1]
                - wall_quad[1][1]
            )
            ** 2
            + (
                wall_quad[2][2]
                - wall_quad[1][2]
            )
            ** 2
        ) ** 0.5

        wall_height_mm = (
            left_height_mm
            + right_height_mm
        ) * 0.5

        if (
            wall_width_mm <= 0.0
            or wall_height_mm <= 0.0
        ):
            return None

        if target_column_spacing_mm is None:
            target_column_spacing_mm = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_TARGET_COLUMN_SPACING_MM
            )

        if target_row_height_mm is None:
            target_row_height_mm = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_TARGET_ROW_HEIGHT_MM
            )

        if min_columns is None:
            min_columns = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_MIN_COLUMNS
            )

        if max_columns is None:
            max_columns = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_MAX_COLUMNS
            )

        if min_rows is None:
            min_rows = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_MIN_ROWS
            )

        if max_rows is None:
            max_rows = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_MAX_ROWS
            )

        target_column_spacing_mm = float(
            target_column_spacing_mm
        )

        target_row_height_mm = float(
            target_row_height_mm
        )

        if target_column_spacing_mm <= 0.0:
            raise ValueError(
                "target_column_spacing_mm must be "
                "greater than zero"
            )

        if target_row_height_mm <= 0.0:
            raise ValueError(
                "target_row_height_mm must be "
                "greater than zero"
            )

        min_columns = int(min_columns)
        max_columns = int(max_columns)
        min_rows = int(min_rows)
        max_rows = int(max_rows)

        if min_columns < 1:
            raise ValueError(
                "min_columns must be at least one"
            )

        if max_columns < min_columns:
            raise ValueError(
                "max_columns must be greater than "
                "or equal to min_columns"
            )

        if min_rows < 1:
            raise ValueError(
                "min_rows must be at least one"
            )

        if max_rows < min_rows:
            raise ValueError(
                "max_rows must be greater than or "
                "equal to min_rows"
            )

        column_count = max(
            min_columns,
            min(
                max_columns,
                int(
                    round(
                        wall_width_mm
                        / target_column_spacing_mm
                    )
                ),
            ),
        )

        row_count = max(
            min_rows,
            min(
                max_rows,
                int(
                    round(
                        wall_height_mm
                        / target_row_height_mm
                    )
                ),
            ),
        )

        if panel_width_ratio is None:
            panel_width_ratio = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_PANEL_WIDTH_RATIO
            )

        if panel_height_ratio is None:
            panel_height_ratio = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_PANEL_HEIGHT_RATIO
            )

        if arch_height_ratio is None:
            arch_height_ratio = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_ARCH_HEIGHT_RATIO
            )

        if horizontal_margin_ratio is None:
            horizontal_margin_ratio = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_HORIZONTAL_MARGIN_RATIO
            )

        if vertical_margin_ratio is None:
            vertical_margin_ratio = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_VERTICAL_MARGIN_RATIO
            )

        if depth_mm is None:
            depth_mm = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_DEPTH_MM
            )

        if embed_mm is None:
            embed_mm = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_EMBED_MM
            )

        if arch_segments is None:
            arch_segments = (
                AtlasAncientTheatreStageFacadeBuilder
                .DEFAULT_ARCH_SEGMENTS
            )

        facade = (
            AtlasFacadePanelBuilder
            .build_repeated_arches(
                wall_quad=wall_quad,
                column_count=column_count,
                row_count=row_count,
                panel_width_ratio=(
                    panel_width_ratio
                ),
                panel_height_ratio=(
                    panel_height_ratio
                ),
                arch_height_ratio=(
                    arch_height_ratio
                ),
                horizontal_margin_ratio=(
                    horizontal_margin_ratio
                ),
                vertical_margin_ratio=(
                    vertical_margin_ratio
                ),
                depth_mm=depth_mm,
                embed_mm=embed_mm,
                arch_segments=arch_segments,
                metadata={
                    "architectural_role": (
                        "ancient_theatre_stage_facade_arch"
                    ),
                },
            )
        )

        wall_top_z = max(
            point[2]
            for point in wall_quad
        )

        facade_top_z = max(
            point[2]
            for component in facade[
                "component_meshes"
            ]
            for point in component["front"]
        )

        facade.update(
            {
                "wall_width_mm": (
                    wall_width_mm
                ),
                "wall_height_mm": (
                    wall_height_mm
                ),
                "wall_top_z": wall_top_z,
                "facade_top_z": facade_top_z,
                "top_clearance_mm": (
                    wall_top_z
                    - facade_top_z
                ),
                "target_column_spacing_mm": (
                    target_column_spacing_mm
                ),
                "target_row_height_mm": (
                    target_row_height_mm
                ),
                "geometry_type": (
                    "ancient_theatre_stage_facade"
                ),
            }
        )

        return facade
