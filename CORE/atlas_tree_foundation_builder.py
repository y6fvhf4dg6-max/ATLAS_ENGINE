# CORE/atlas_tree_foundation_builder.py

"""
ATLAS Tree Foundation Builder v0.3

Tekil OSM ağaç noktalarını terrain üzerine oturan
çeşitli maket ağacı formlarında üretir.

Özellikler:
- yuvarlak taçlı ağaç
- çam / konik ağaç
- deterministik küçük rastgelelik
"""

import math
import random

from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_physical_cartographic_exaggeration_resolver import (
    AtlasPhysicalCartographicExaggerationResolver,
)


class AtlasTreeFoundationBuilder:
    TREE_SEGMENTS = 12

    CANONICAL_TREE_MIN_CROWN_DIAMETER_MM = 0.60

    PARK_TREE_SYMBOL_MIN_HEIGHT_MM = 1.0
    PARK_TREE_SYMBOL_MAX_HEIGHT_MM = 1.4
    PARK_TREE_SYMBOL_MIN_DIAMETER_MM = 0.60
    PARK_TREE_SYMBOL_MAX_DIAMETER_MM = 1.10

    @staticmethod
    def build_trees(
        trees,
        coordinate_engine,
        terrain_mesh,
        cartographic_product_size_mm=None,
        cartographic_nozzle_diameter_mm=None,
        cartographic_lod_level=None,
        debug=True,
    ):
        meshes = []
        accepted = 0
        skipped = 0

        for index, tree in enumerate(trees):
            mesh = AtlasTreeFoundationBuilder._build_tree_mesh(
                tree=tree,
                index=index,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
                cartographic_product_size_mm=(
                    cartographic_product_size_mm
                ),
                cartographic_nozzle_diameter_mm=(
                    cartographic_nozzle_diameter_mm
                ),
                cartographic_lod_level=(
                    cartographic_lod_level
                ),
            )

            if mesh:
                meshes.append(mesh)
                accepted += 1
            else:
                skipped += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS TREE FOUNDATION BUILDER REPORT")
            print("=" * 60)
            print(f"Input trees      : {len(trees)}")
            print(f"Accepted trees   : {accepted}")
            print(f"Skipped trees    : {skipped}")
            print(f"Tree meshes      : {len(meshes)}")
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_tree_mesh(
        tree,
        index,
        coordinate_engine,
        terrain_mesh,
        cartographic_product_size_mm=None,
        cartographic_nozzle_diameter_mm=None,
        cartographic_lod_level=None,
    ):
        lat = tree.get("lat")
        lon = tree.get("lon")

        if lat is None or lon is None:
            return None

        x, y = coordinate_engine.latlon_to_stl_mm(lat, lon)

        terrain_bounds = (
            AtlasTreeFoundationBuilder
            ._terrain_xy_bounds(
                terrain_mesh
            )
        )

        if terrain_bounds is None:
            return None

        (
            terrain_min_x,
            terrain_max_x,
            terrain_min_y,
            terrain_max_y,
        ) = terrain_bounds

        canonical_dimensions = (
            AtlasTreeFoundationBuilder
            ._canonical_tree_dimensions(
                tree=tree,
                scale_ratio=getattr(
                    coordinate_engine,
                    "xy_scale",
                    None,
                ),
                product_size_mm=(
                    cartographic_product_size_mm
                ),
                nozzle_diameter_mm=(
                    cartographic_nozzle_diameter_mm
                ),
                lod_level=(
                    cartographic_lod_level
                ),
            )
        )

        crown_radius_mm = (
            canonical_dimensions[
                "crown_diameter_mm"
            ]
            / 2.0
        )

        if not (
            terrain_min_x + crown_radius_mm
            <= x
            <= terrain_max_x - crown_radius_mm
            and terrain_min_y + crown_radius_mm
            <= y
            <= terrain_max_y - crown_radius_mm
        ):
            return None

        base_z = AtlasFoundationSampler.terrain_z_at_xy(
            terrain_mesh=terrain_mesh,
            x=x,
            y=y,
        )

        rng = random.Random(tree.get("id", index))

        tree_kind = AtlasTreeFoundationBuilder._select_tree_kind(
            tree,
            rng,
        )

        physical_scale = (
            AtlasTreeFoundationBuilder
            ._resolve_physical_tree_scale(tree)
        )

        canonical_tree = (
            AtlasTreeFoundationBuilder
            ._build_canonical_tree(
                x=x,
                y=y,
                base_z=base_z,
                tree=tree,
                physical_scale=physical_scale,
                scale_ratio=getattr(
                    coordinate_engine,
                    "xy_scale",
                    None,
                ),
                product_size_mm=(
                    cartographic_product_size_mm
                ),
                nozzle_diameter_mm=(
                    cartographic_nozzle_diameter_mm
                ),
                lod_level=(
                    cartographic_lod_level
                ),
            )
        )

        triangles = canonical_tree["triangles"]

        tags = dict(tree.get("tags") or {})

        return {
            "type": "tree_foundation",
            "tree_id": tree.get("id", index),
            "tree_type": tree_kind,
            "source": AtlasTreeFoundationBuilder._resolve_source(tree),
            "tags": tags,
            "bottom": [],
            "top": [],
            "walls": [],
            "triangles": triangles,
            "placement_mode": "foundation_first",
        }

    @staticmethod
    def _terrain_xy_bounds(terrain_mesh):
        if not isinstance(terrain_mesh, dict):
            return None

        triangles = terrain_mesh.get(
            "triangles",
            (),
        )

        points = [
            point
            for triangle in triangles
            for point in triangle
            if len(point) >= 2
        ]

        if not points:
            return None

        xs = [
            float(point[0])
            for point in points
        ]
        ys = [
            float(point[1])
            for point in points
        ]

        return (
            min(xs),
            max(xs),
            min(ys),
            max(ys),
        )

    @staticmethod
    def _select_tree_kind(tree, rng):
        del tree, rng

        return "canonical"

    @staticmethod
    def _resolve_physical_tree_scale(tree):
        if not isinstance(tree, dict):
            return 1.0

        tags = tree.get("tags") or {}

        if tags.get("source") != "worldcover":
            return 1.0

        variants = (0.95, 1.0, 1.05)

        rng = random.Random(
            str(tree.get("id", "worldcover_tree"))
        )

        return variants[
            rng.randrange(len(variants))
        ]

    @staticmethod
    def _canonical_tree_dimensions(
        *,
        tree=None,
        scale_ratio=None,
        product_size_mm=None,
        nozzle_diameter_mm=None,
        lod_level=None,
    ):
        crown_diameter_mm = 3.875

        tags = (
            tree.get("tags", {})
            if isinstance(tree, dict)
            else {}
        )

        source_diameter = tags.get(
            "diameter_crown"
        )

        context_complete = (
            source_diameter is not None
            and scale_ratio is not None
            and product_size_mm is not None
            and nozzle_diameter_mm is not None
            and lod_level is not None
        )

        if context_complete:
            try:
                candidate = source_diameter

                if isinstance(candidate, str):
                    candidate = (
                        candidate
                        .replace("m", "")
                        .strip()
                    )

                source_diameter_m = float(
                    candidate
                )

                if (
                    not math.isfinite(
                        source_diameter_m
                    )
                    or source_diameter_m <= 0.0
                ):
                    raise ValueError
            except (
                TypeError,
                ValueError,
            ):
                pass
            else:
                exaggeration = (
                    AtlasTreeFoundationBuilder
                    ._resolve_canonical_tree_diameter_mm(
                        source_diameter_m=(
                            source_diameter_m
                        ),
                        scale_ratio=scale_ratio,
                        product_size_mm=(
                            product_size_mm
                        ),
                        nozzle_diameter_mm=(
                            nozzle_diameter_mm
                        ),
                        minimum_printable_width_mm=(
                            AtlasTreeFoundationBuilder
                            .CANONICAL_TREE_MIN_CROWN_DIAMETER_MM
                        ),
                        lod_level=lod_level,
                    )
                )

                crown_diameter_mm = (
                    exaggeration.physical_width_mm
                )

        return {
            "total_height_mm": 5.375,
            "trunk_height_mm": 2.00,
            "trunk_diameter_mm": 1.50,
            "root_collar_diameter_mm": 2.20,
            "root_collar_height_mm": 0.80,
            "terrain_embed_depth_mm": 0.60,
            "crown_height_mm": 3.375,
            "crown_diameter_mm": crown_diameter_mm,
        }

    @staticmethod
    def _build_canonical_tree(
        *,
        x,
        y,
        base_z,
        tree=None,
        physical_scale=1.0,
        scale_ratio=None,
        product_size_mm=None,
        nozzle_diameter_mm=None,
        lod_level=None,
    ):
        dimensions = (
            AtlasTreeFoundationBuilder
            ._canonical_tree_dimensions(
                tree=tree,
                scale_ratio=scale_ratio,
                product_size_mm=product_size_mm,
                nozzle_diameter_mm=nozzle_diameter_mm,
                lod_level=lod_level,
            )
        )

        physical_scale = float(physical_scale)

        dimensions = {
            key: (
                float(value) * physical_scale
                if key in {
                    "total_height_mm",
                    "trunk_height_mm",
                    "trunk_diameter_mm",
                    "crown_height_mm",
                    "crown_diameter_mm",
                }
                else value
            )
            for key, value in dimensions.items()
        }

        segment_count = (
            AtlasTreeFoundationBuilder
            .TREE_SEGMENTS
        )

        trunk_height = dimensions[
            "trunk_height_mm"
        ]
        trunk_radius = (
            dimensions["trunk_diameter_mm"]
            / 2.0
        )
        root_collar_radius = (
            dimensions["root_collar_diameter_mm"]
            / 2.0
        )
        root_collar_height = dimensions[
            "root_collar_height_mm"
        ]
        terrain_embed_depth = dimensions[
            "terrain_embed_depth_mm"
        ]
        crown_height = dimensions[
            "crown_height_mm"
        ]
        crown_radius = (
            dimensions["crown_diameter_mm"]
            / 2.0
        )

        terrain_surface_z = float(base_z)
        trunk_bottom_z = (
            terrain_surface_z
            - terrain_embed_depth
        )
        root_collar_bottom_z = trunk_bottom_z
        root_collar_top_z = (
            root_collar_bottom_z
            + root_collar_height
        )
        trunk_top_z = (
            terrain_surface_z
            + trunk_height
        )
        crown_bottom_z = trunk_top_z
        top_z = (
            terrain_surface_z
            + dimensions["total_height_mm"]
        )

        def ring(
            radius,
            z,
            offset_x=0.0,
            offset_y=0.0,
        ):
            return [
                (
                    float(x)
                    + offset_x
                    + math.cos(
                        2.0
                        * math.pi
                        * index
                        / segment_count
                    )
                    * radius,
                    float(y)
                    + offset_y
                    + math.sin(
                        2.0
                        * math.pi
                        * index
                        / segment_count
                    )
                    * radius,
                    float(z),
                )
                for index in range(
                    segment_count
                )
            ]

        root_collar_bottom = ring(
            root_collar_radius,
            root_collar_bottom_z,
        )
        root_collar_top = ring(
            trunk_radius,
            root_collar_top_z,
        )
        trunk_top = ring(
            trunk_radius,
            trunk_top_z,
        )

        crown_rings = [
            ring(
                crown_radius * 0.48,
                crown_bottom_z,
                -0.02,
                0.00,
            ),
            ring(
                crown_radius * 0.76,
                crown_bottom_z
                + crown_height * 0.12,
                -0.03,
                0.01,
            ),
            ring(
                crown_radius * 0.96,
                crown_bottom_z
                + crown_height * 0.28,
                -0.02,
                0.02,
            ),
            ring(
                crown_radius,
                crown_bottom_z
                + crown_height * 0.46,
                0.01,
                0.02,
            ),
            ring(
                crown_radius * 0.96,
                crown_bottom_z
                + crown_height * 0.62,
                0.03,
                0.00,
            ),
            ring(
                crown_radius * 0.78,
                crown_bottom_z
                + crown_height * 0.78,
                0.03,
                -0.02,
            ),
            ring(
                crown_radius * 0.48,
                crown_bottom_z
                + crown_height * 0.91,
                0.01,
                -0.02,
            ),
            ring(
                crown_radius * 0.18,
                top_z,
                0.00,
                -0.01,
            ),
        ]

        triangles = []

        AtlasTreeFoundationBuilder._ring_to_ring(
            triangles,
            root_collar_bottom,
            root_collar_top,
        )

        AtlasTreeFoundationBuilder._ring_to_ring(
            triangles,
            root_collar_top,
            trunk_top,
        )

        AtlasTreeFoundationBuilder._ring_to_ring(
            triangles,
            trunk_top,
            crown_rings[0],
        )

        for lower, upper in zip(
            crown_rings,
            crown_rings[1:],
        ):
            AtlasTreeFoundationBuilder._ring_to_ring(
                triangles,
                lower,
                upper,
            )

        top_center = (
            float(x) + 0.01,
            float(y) - 0.01,
            top_z,
        )

        AtlasTreeFoundationBuilder._cap_bottom(
            triangles,
            root_collar_bottom,
            (
                float(x),
                float(y),
                root_collar_bottom_z,
            ),
        )

        AtlasTreeFoundationBuilder._ring_to_tip(
            triangles,
            crown_rings[-1],
            top_center,
        )

        return {
            "triangles": triangles,
            "dimensions": dimensions,
            "trunk_bottom_z": trunk_bottom_z,
            "root_collar_bottom_z": root_collar_bottom_z,
            "root_collar_top_z": root_collar_top_z,
            "trunk_top_z": trunk_top_z,
            "crown_bottom_z": crown_bottom_z,
            "top_z": top_z,
        }

    @staticmethod
    def _resolve_canonical_tree_diameter_mm(
        *,
        source_diameter_m,
        scale_ratio,
        product_size_mm,
        nozzle_diameter_mm,
        minimum_printable_width_mm,
        lod_level,
    ):
        return (
            AtlasPhysicalCartographicExaggerationResolver
            .resolve(
                semantic_class="vegetation_element",
                source_width_m=source_diameter_m,
                scale_ratio=scale_ratio,
                product_size_mm=product_size_mm,
                nozzle_diameter_mm=nozzle_diameter_mm,
                minimum_printable_width_mm=(
                    minimum_printable_width_mm
                ),
                semantic_priority=0.50,
                lod_level=lod_level,
            )
        )

    @staticmethod
    def _resolve_source(tree):
        tags = tree.get("tags") or {}

        source = tree.get("source") or tags.get("source")

        if not isinstance(source, str):
            return "osm"

        normalized = source.strip().lower()

        known_sources = {
            "worldcover",
            "osm_green_area_fill",
            "osm",
        }

        if normalized in known_sources:
            return normalized

        if "://" in normalized or normalized.startswith("www."):
            return "osm"

        return normalized or "osm"

    @staticmethod
    def _ring_to_ring(triangles, lower, upper):
        n = len(lower)

        for i in range(n):
            j = (i + 1) % n
            triangles.append((lower[i], lower[j], upper[j]))
            triangles.append((lower[i], upper[j], upper[i]))

    @staticmethod
    def _ring_to_tip(triangles, ring, tip):
        n = len(ring)

        for i in range(n):
            j = (i + 1) % n
            triangles.append((ring[i], ring[j], tip))

    @staticmethod
    def _cap_bottom(triangles, ring, center):
        n = len(ring)

        for i in range(n):
            j = (i + 1) % n
            triangles.append((center, ring[j], ring[i]))
