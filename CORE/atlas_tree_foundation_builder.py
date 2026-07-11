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


class AtlasTreeFoundationBuilder:
    TREE_SEGMENTS = 12

    @staticmethod
    def build_trees(
        trees,
        coordinate_engine,
        terrain_mesh,
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
    def _build_tree_mesh(tree, index, coordinate_engine, terrain_mesh):
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
        else:
            triangles = AtlasTreeFoundationBuilder._build_round_tree(
                x=x,
                y=y,
                base_z=base_z,
                rng=rng,
            )

        return {
            "type": "tree_foundation",
            "tree_type": tree_kind,
            "bottom": [],
            "top": [],
            "walls": [],
            "triangles": triangles,
            "placement_mode": "foundation_first",
        }

    @staticmethod
    def _select_tree_kind(tree, rng):
        source = (tree.get("source") or "").lower()

        # WorldCover tekil ağaç türü bilgisi sağlamaz.
        # Bu nedenle WorldCover örnekleri mevcut yuvarlak taçlı
        # ATLAS ağacıyla üretilir.
        tags = tree.get("tags", {})

        source = (tree.get("source") or tags.get("source") or "").lower()

        if source == "worldcover":
            return "round"

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
