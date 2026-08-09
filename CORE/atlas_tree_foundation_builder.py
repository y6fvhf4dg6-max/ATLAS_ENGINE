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

        if not (0.0 <= x <= 200.0 and 0.0 <= y <= 200.0):
            return None

        base_z = AtlasFoundationSampler.terrain_z_at_xy(
            terrain_mesh=terrain_mesh,
            x=x,
            y=y,
        )

        rng = random.Random(tree.get("id", index))

        tree_kind = AtlasTreeFoundationBuilder._select_tree_kind(tree, rng)

        if tree_kind == "conifer":
            triangles = AtlasTreeFoundationBuilder._build_conifer(
                x=x,
                y=y,
                base_z=base_z,
                rng=rng,
            )
        elif tree_kind == "park_tree_symbol":
            cartographic_context_complete = (
                cartographic_product_size_mm is not None
                and cartographic_nozzle_diameter_mm is not None
                and cartographic_lod_level is not None
            )

            if cartographic_context_complete:
                triangles = (
                    AtlasTreeFoundationBuilder
                    ._build_park_tree_symbol(
                        x=x,
                        y=y,
                        base_z=base_z,
                        rng=rng,
                        tree=tree,
                        scale_ratio=(
                            coordinate_engine.xy_scale
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
            else:
                triangles = (
                    AtlasTreeFoundationBuilder
                    ._build_park_tree_symbol(
                        x=x,
                        y=y,
                        base_z=base_z,
                        rng=rng,
                    )
                )
        else:
            triangles = AtlasTreeFoundationBuilder._build_round_tree(
                x=x,
                y=y,
                base_z=base_z,
                rng=rng,
            )

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
    def _select_tree_kind(tree, rng):
        explicit_kind = tree.get("tree_kind")

        if explicit_kind is not None:
            explicit_kind = str(explicit_kind)

            if explicit_kind not in {
                "round",
                "conifer",
                "park_tree_symbol",
            }:
                raise ValueError(
                    "unsupported explicit tree_kind"
                )

            return explicit_kind

        source = (tree.get("source") or "").lower()

        # WorldCover tekil ağaç türü bilgisi sağlamaz.
        # Bu nedenle WorldCover örnekleri mevcut yuvarlak taçlı
        # ATLAS ağacıyla üretilir.
        tags = tree.get("tags", {})

        source = (tree.get("source") or tags.get("source") or "").lower()

        if source == "worldcover":
            return "park_tree_symbol"

        leaf_type = tags.get("leaf_type")
        genus = (tags.get("genus") or "").lower()
        species = (tags.get("species") or "").lower()

        conifer_words = {
            "needleleaved",
            "conifer",
            "pinus",
            "pine",
            "cedrus",
            "cypress",
            "cupressus",
            "fir",
            "abies",
            "spruce",
            "picea",
        }

        tag_text = f"{leaf_type} {genus} {species}".lower()

        if any(word in tag_text for word in conifer_words):
            return "conifer"

        if rng.random() < 0.25:
            return "conifer"

        return "round"

    @staticmethod
    def _build_round_tree(x, y, base_z, rng):
        n = AtlasTreeFoundationBuilder.TREE_SEGMENTS

        trunk_r = 0.20 * rng.uniform(0.90, 1.15)
        trunk_h = 0.45 * rng.uniform(0.85, 1.15)

        crown_r = 0.72 * rng.uniform(0.85, 1.18)
        crown_h = 0.78 * rng.uniform(0.85, 1.18)

        crown_offset_x = rng.uniform(-0.10, 0.10)
        crown_offset_y = rng.uniform(-0.10, 0.10)

        trunk_bottom = []
        trunk_top = []
        crown_low = []
        crown_mid = []
        crown_high = []

        for i in range(n):
            a = 2.0 * math.pi * i / n

            trunk_bottom.append(
                (
                    x + math.cos(a) * trunk_r,
                    y + math.sin(a) * trunk_r,
                    base_z,
                )
            )

            trunk_top.append(
                (
                    x + math.cos(a) * trunk_r,
                    y + math.sin(a) * trunk_r,
                    base_z + trunk_h,
                )
            )

            cx = x + crown_offset_x
            cy = y + crown_offset_y

            crown_low.append(
                (
                    cx + math.cos(a) * crown_r * 0.72,
                    cy + math.sin(a) * crown_r * 0.72,
                    base_z + trunk_h + crown_h * 0.15,
                )
            )

            crown_mid.append(
                (
                    cx + math.cos(a) * crown_r,
                    cy + math.sin(a) * crown_r,
                    base_z + trunk_h + crown_h * 0.50,
                )
            )

            crown_high.append(
                (
                    cx + math.cos(a) * crown_r * 0.55,
                    cy + math.sin(a) * crown_r * 0.55,
                    base_z + trunk_h + crown_h * 0.82,
                )
            )

        top = (
            x + crown_offset_x,
            y + crown_offset_y,
            base_z + trunk_h + crown_h,
        )

        triangles = []

        AtlasTreeFoundationBuilder._ring_to_ring(triangles, trunk_bottom, trunk_top)
        AtlasTreeFoundationBuilder._ring_to_ring(triangles, trunk_top, crown_low)
        AtlasTreeFoundationBuilder._ring_to_ring(triangles, crown_low, crown_mid)
        AtlasTreeFoundationBuilder._ring_to_ring(triangles, crown_mid, crown_high)
        AtlasTreeFoundationBuilder._ring_to_tip(triangles, crown_high, top)
        AtlasTreeFoundationBuilder._cap_bottom(triangles, trunk_bottom, (x, y, base_z))

        return triangles

    @staticmethod
    def _build_conifer(x, y, base_z, rng):
        n = AtlasTreeFoundationBuilder.TREE_SEGMENTS

        trunk_r = 0.16 * rng.uniform(0.90, 1.15)
        trunk_h = 0.35 * rng.uniform(0.85, 1.15)

        lower_r = 0.75 * rng.uniform(0.85, 1.15)
        mid_r = lower_r * 0.58
        high_r = lower_r * 0.28

        total_h = 1.45 * rng.uniform(0.90, 1.15)

        trunk_bottom = []
        trunk_top = []
        lower = []
        mid = []
        high = []

        for i in range(n):
            a = 2.0 * math.pi * i / n

            trunk_bottom.append(
                (
                    x + math.cos(a) * trunk_r,
                    y + math.sin(a) * trunk_r,
                    base_z,
                )
            )

            trunk_top.append(
                (
                    x + math.cos(a) * trunk_r,
                    y + math.sin(a) * trunk_r,
                    base_z + trunk_h,
                )
            )

            lower.append(
                (
                    x + math.cos(a) * lower_r,
                    y + math.sin(a) * lower_r,
                    base_z + trunk_h + total_h * 0.10,
                )
            )

            mid.append(
                (
                    x + math.cos(a) * mid_r,
                    y + math.sin(a) * mid_r,
                    base_z + trunk_h + total_h * 0.50,
                )
            )

            high.append(
                (
                    x + math.cos(a) * high_r,
                    y + math.sin(a) * high_r,
                    base_z + trunk_h + total_h * 0.78,
                )
            )

        top = (x, y, base_z + trunk_h + total_h)

        triangles = []

        AtlasTreeFoundationBuilder._ring_to_ring(triangles, trunk_bottom, trunk_top)
        AtlasTreeFoundationBuilder._ring_to_ring(triangles, trunk_top, lower)
        AtlasTreeFoundationBuilder._ring_to_ring(triangles, lower, mid)
        AtlasTreeFoundationBuilder._ring_to_ring(triangles, mid, high)
        AtlasTreeFoundationBuilder._ring_to_tip(triangles, high, top)
        AtlasTreeFoundationBuilder._cap_bottom(triangles, trunk_bottom, (x, y, base_z))

        return triangles

    @staticmethod
    def _round_crown_profile(
        crown_radius,
        crown_height,
    ):
        del crown_radius, crown_height

        return [
            (0.00, 0.28),
            (0.16, 0.68),
            (0.38, 1.00),
            (0.64, 0.82),
            (0.84, 0.46),
            (1.00, 0.00),
        ]

    @staticmethod
    def _round_crown_lobes(rng):
        lobes = []

        for angle_index in range(4):
            angle = (
                2.0
                * math.pi
                * angle_index
                / 4.0
                + rng.uniform(-0.30, 0.30)
            )

            offset = rng.uniform(0.06, 0.18)

            lobes.append(
                {
                    "offset_x": math.cos(angle) * offset,
                    "offset_y": math.sin(angle) * offset,
                    "radius_scale": rng.uniform(0.82, 1.12),
                    "height_scale": rng.uniform(0.88, 1.10),
                }
            )

        return lobes

    @staticmethod
    def _park_tree_symbol_profile():
        return [
            (0.00, 0.52),
            (0.22, 0.78),
            (0.52, 1.00),
            (0.78, 0.64),
            (1.00, 0.00),
        ]

    @staticmethod
    def _resolve_park_tree_symbol_diameter_mm(
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
    def _park_tree_symbol_dimensions(
        rng,
        *,
        tree=None,
        scale_ratio=None,
        product_size_mm=None,
        nozzle_diameter_mm=None,
        lod_level=None,
    ):
        height_mm = rng.uniform(
            AtlasTreeFoundationBuilder
            .PARK_TREE_SYMBOL_MIN_HEIGHT_MM,
            AtlasTreeFoundationBuilder
            .PARK_TREE_SYMBOL_MAX_HEIGHT_MM,
        )

        diameter_mm = rng.uniform(
            AtlasTreeFoundationBuilder
            .PARK_TREE_SYMBOL_MIN_DIAMETER_MM,
            AtlasTreeFoundationBuilder
            .PARK_TREE_SYMBOL_MAX_DIAMETER_MM,
        )

        tags = (
            tree.get("tags", {})
            if isinstance(tree, dict)
            else {}
        )

        source_diameter = tags.get(
            "diameter_crown"
        )

        if (
            source_diameter is not None
            and scale_ratio is not None
            and product_size_mm is not None
            and nozzle_diameter_mm is not None
            and lod_level is not None
        ):
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
                    ._resolve_park_tree_symbol_diameter_mm(
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
                            .PARK_TREE_SYMBOL_MIN_DIAMETER_MM
                        ),
                        lod_level=lod_level,
                    )
                )

                diameter_mm = (
                    exaggeration.physical_width_mm
                )

        return {
            "height_mm": height_mm,
            "diameter_mm": diameter_mm,
        }

    @staticmethod
    def _build_park_tree_symbol(
        x,
        y,
        base_z,
        rng,
        tree=None,
        scale_ratio=None,
        product_size_mm=None,
        nozzle_diameter_mm=None,
        lod_level=None,
    ):
        dimensions = (
            AtlasTreeFoundationBuilder
            ._park_tree_symbol_dimensions(
                rng,
                tree=tree,
                scale_ratio=scale_ratio,
                product_size_mm=product_size_mm,
                nozzle_diameter_mm=nozzle_diameter_mm,
                lod_level=lod_level,
            )
        )
        profile = (
            AtlasTreeFoundationBuilder
            ._park_tree_symbol_profile()
        )

        height = dimensions["height_mm"]
        radius = dimensions["diameter_mm"] / 2.0
        segment_count = AtlasTreeFoundationBuilder.TREE_SEGMENTS

        rings = []

        for height_scale, radius_scale in profile:
            if radius_scale <= 0.0:
                continue

            ring = []

            for index in range(segment_count):
                angle = (
                    2.0
                    * math.pi
                    * index
                    / segment_count
                )

                ring.append(
                    (
                        x + math.cos(angle) * radius * radius_scale,
                        y + math.sin(angle) * radius * radius_scale,
                        base_z + height * height_scale,
                    )
                )

            rings.append(ring)

        triangles = []

        for lower, upper in zip(rings, rings[1:]):
            AtlasTreeFoundationBuilder._ring_to_ring(
                triangles,
                lower,
                upper,
            )

        tip = (
            x,
            y,
            base_z + height,
        )

        AtlasTreeFoundationBuilder._ring_to_tip(
            triangles,
            rings[-1],
            tip,
        )
        AtlasTreeFoundationBuilder._cap_bottom(
            triangles,
            rings[0],
            (x, y, base_z),
        )

        return triangles

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
