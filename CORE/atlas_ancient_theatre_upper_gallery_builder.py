"""
ATLAS Ancient Theatre Upper Gallery Builder v0.1

Antik tiyatro cavea meshinin yatay dış terası üzerinde
kavisli sütun dizisi ve kapalı üst saçak üretir.

Bu builder:
- belirli bir tiyatro adına bağlı değildir,
- OSM kimliği veya koordinat hard-code etmez,
- genel klasik sütun ve ribbon-prism bileşenlerini kullanır.

Üretilen her component ayrı, kapalı ve manifold mesh olarak
korunur. Boolean union uygulanmaz.
"""

from CORE.atlas_classical_colonnade_builder import (
    AtlasClassicalColonnadeBuilder,
)
from CORE.atlas_polyline_ribbon_prism_builder import (
    AtlasPolylineRibbonPrismBuilder,
)


class AtlasAncientTheatreUpperGalleryBuilder:
    DEFAULT_COLUMN_RADIUS_MM = 0.28
    DEFAULT_COLUMN_HEIGHT_MM = 2.40
    DEFAULT_COLUMN_SPACING_MM = 2.20
    DEFAULT_COLUMN_SEGMENTS = 10
    DEFAULT_CAP_HEIGHT_MM = 0.55

    @staticmethod
    def build(
        cavea_mesh,
        column_radius_mm=None,
        column_height_mm=None,
        column_spacing_mm=None,
        column_segments=None,
        cap_height_mm=None,
    ):
        if not cavea_mesh:
            return None

        placed_bowl_grid = cavea_mesh.get(
            "placed_bowl_grid",
            {},
        )

        top_rings = placed_bowl_grid.get(
            "top_rings",
            [],
        )

        if len(top_rings) < 2:
            return None

        terrace_inner_ring = top_rings[-2]
        terrace_outer_ring = top_rings[-1]

        if (
            len(terrace_inner_ring) < 2
            or len(terrace_inner_ring)
            != len(terrace_outer_ring)
        ):
            return None

        inner_z_values = {
            round(point[2], 9)
            for point in terrace_inner_ring
        }

        outer_z_values = {
            round(point[2], 9)
            for point in terrace_outer_ring
        }

        if (
            len(inner_z_values) != 1
            or len(outer_z_values) != 1
            or inner_z_values != outer_z_values
        ):
            return None

        if column_radius_mm is None:
            column_radius_mm = (
                AtlasAncientTheatreUpperGalleryBuilder
                .DEFAULT_COLUMN_RADIUS_MM
            )

        if column_height_mm is None:
            column_height_mm = (
                AtlasAncientTheatreUpperGalleryBuilder
                .DEFAULT_COLUMN_HEIGHT_MM
            )

        if column_spacing_mm is None:
            column_spacing_mm = (
                AtlasAncientTheatreUpperGalleryBuilder
                .DEFAULT_COLUMN_SPACING_MM
            )

        if column_segments is None:
            column_segments = (
                AtlasAncientTheatreUpperGalleryBuilder
                .DEFAULT_COLUMN_SEGMENTS
            )

        if cap_height_mm is None:
            cap_height_mm = (
                AtlasAncientTheatreUpperGalleryBuilder
                .DEFAULT_CAP_HEIGHT_MM
            )

        inner_path = [
            (
                point[0],
                point[1],
            )
            for point in terrace_inner_ring
        ]

        outer_path = [
            (
                point[0],
                point[1],
            )
            for point in terrace_outer_ring
        ]

        column_path = [
            (
                (
                    inner_point[0]
                    + outer_point[0]
                )
                * 0.5,
                (
                    inner_point[1]
                    + outer_point[1]
                )
                * 0.5,
            )
            for inner_point, outer_point in zip(
                terrace_inner_ring,
                terrace_outer_ring,
            )
        ]

        terrace_z = terrace_outer_ring[0][2]

        colonnade = (
            AtlasClassicalColonnadeBuilder
            .build_along_polyline(
                path_points=column_path,
                base_z=terrace_z,
                column_radius_mm=(
                    column_radius_mm
                ),
                column_height_mm=(
                    column_height_mm
                ),
                target_spacing_mm=(
                    column_spacing_mm
                ),
                column_segments=(
                    column_segments
                ),
                include_endpoints=True,
                metadata={
                    "architectural_role": (
                        "ancient_theatre_upper_gallery"
                    ),
                },
            )
        )

        cap = (
            AtlasPolylineRibbonPrismBuilder
            .build(
                inner_path=inner_path,
                outer_path=outer_path,
                base_z=colonnade["top_z"],
                height=cap_height_mm,
                metadata={
                    "architectural_role": (
                        "ancient_theatre_gallery_cap"
                    ),
                },
            )
        )

        triangles = [
            *colonnade["triangles"],
            *cap["triangles"],
        ]

        return {
            "triangles": triangles,
            "colonnade": colonnade,
            "cap": cap,
            "component_meshes": [
                *colonnade[
                    "component_meshes"
                ],
                cap,
            ],
            "column_count": colonnade[
                "column_count"
            ],
            "column_radius_mm": (
                colonnade["column_radius_mm"]
            ),
            "column_height_mm": (
                colonnade["column_height_mm"]
            ),
            "column_spacing_min_mm": (
                colonnade[
                    "actual_spacing_min_mm"
                ]
            ),
            "column_spacing_max_mm": (
                colonnade[
                    "actual_spacing_max_mm"
                ]
            ),
            "terrace_z": terrace_z,
            "cap_base_z": cap["base_z"],
            "cap_top_z": cap["top_z"],
            "cap_height_mm": cap["height"],
            "geometry_type": (
                "ancient_theatre_upper_gallery"
            ),
        }
