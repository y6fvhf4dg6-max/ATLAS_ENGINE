"""
ATLAS Castle Shell Builder v0.2

Multipolygon relation biçimindeki kaleleri, iç avlusu boş,
terrain üzerine oturan kapalı 3D kale kabuklarına dönüştürür.

Özellikler:
- OSM outer / inner rollerini geometrik olarak düzeltir
- Delikli polygon triangulation kullanır
- Terrain yüksekliğini her sınır noktasında örnekler
- Dış sınır ile iç avlu arasındaki yerel kalınlığı ölçer
- Kalın ve sürekli bölgeleri kule / burç olarak yükseltir
- Üst ve alt yüzey üretir
- Dış ve iç avlu duvarlarını kapatır
- Baskıya uygun manifold mesh hedefler

v0.2:
- Üç güçlü kule / burç bölgesi otomatik belirlenebilir
- Normal sur yüksekliği korunur
- Kule bölgeleri normal surdan daha yüksek üretilir
"""

from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)
from CORE.atlas_castle_shell_height_profiler import (
    AtlasCastleShellHeightProfiler,
)
from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)


class AtlasCastleShellBuilder:
    DEFAULT_SHELL_HEIGHT_M = 10.0
    MIN_SHELL_HEIGHT_MM = 6.00

    POINT_PRECISION = 9
    HEIGHT_PRECISION = 6

    @staticmethod
    def build_shells(
        castles,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []
        accepted = 0
        skipped = 0
        corrected_roles = 0
        tower_regions = 0
        tower_points = 0

        for castle in castles:
            geometry_type = castle.get("geometry_type")

            if geometry_type not in (
                "relation",
                "way",
            ):
                skipped += 1
                continue

            mesh = AtlasCastleShellBuilder._build_shell_mesh(
                castle=castle,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
            )

            if mesh:
                meshes.append(mesh)
                accepted += 1

                if mesh.get("roles_corrected"):
                    corrected_roles += 1

                tower_regions += mesh.get(
                    "tower_region_count",
                    0,
                )

                tower_points += mesh.get(
                    "tower_point_count",
                    0,
                )
            else:
                skipped += 1

        if debug:
            print("")
            print("=" * 64)
            print("ATLAS CASTLE SHELL BUILDER REPORT")
            print("=" * 64)
            print(f"Input castles       : {len(castles)}")
            print(f"Accepted shells     : {accepted}")
            print(f"Skipped castles     : {skipped}")
            print(f"Corrected roles     : {corrected_roles}")
            print(f"Tower regions       : {tower_regions}")
            print(f"Tower points        : {tower_points}")
            print(f"Shell meshes        : {len(meshes)}")
            print(
                f"Shell triangles     : "
                f"{AtlasCastleShellBuilder._count_triangles(meshes)}"
            )
            print("=" * 64)
            print("")

        return meshes

    @staticmethod
    def _build_shell_mesh(
        castle,
        coordinate_engine,
        terrain_mesh,
    ):
        outer_geometries = castle.get(
            "outer_geometries",
            [],
        )

        inner_geometries = castle.get(
            "inner_geometries",
            [],
        )

        if not outer_geometries:
            return None

        converted_outer_rings = [
            coordinate_engine.geometry_to_stl_mm(geometry)
            for geometry in outer_geometries
            if len(geometry) >= 3
        ]

        converted_inner_rings = [
            coordinate_engine.geometry_to_stl_mm(geometry)
            for geometry in inner_geometries
            if len(geometry) >= 3
        ]

        if not converted_outer_rings:
            return None

        primary_outer = converted_outer_rings[0]

        candidate_inner_rings = []
        candidate_inner_rings.extend(converted_outer_rings[1:])
        candidate_inner_rings.extend(converted_inner_rings)

        normalized = AtlasCastleShellTriangulator.normalize_rings(
            outer_ring=primary_outer,
            inner_rings=candidate_inner_rings,
        )

        outer_ring = normalized.get(
            "outer_ring",
            [],
        )

        inner_rings = normalized.get(
            "inner_rings",
            [],
        )

        if len(outer_ring) < 3:
            return None

        flat_triangles = AtlasCastleShellTriangulator.triangulate(
            outer_ring=primary_outer,
            inner_rings=candidate_inner_rings,
        )

        if not flat_triangles:
            return None

        tags = castle.get("tags", {})

        height_m = AtlasCastleShellBuilder._read_positive_float(
            tags.get("height"),
            AtlasCastleShellBuilder.DEFAULT_SHELL_HEIGHT_M,
        )

        height_mm = max(
            coordinate_engine.height_to_stl_mm(height_m),
            AtlasCastleShellBuilder.MIN_SHELL_HEIGHT_MM,
        )

        oriented_outer = AtlasCastleShellBuilder._ensure_ccw(outer_ring)

        oriented_holes = [
            AtlasCastleShellBuilder._ensure_cw(ring) for ring in inner_rings
        ]

        height_profile = AtlasCastleShellHeightProfiler.build_profile(
            outer_ring=oriented_outer,
            inner_rings=oriented_holes,
        )

        # Ana kale kabuğu eşit sur yüksekliğinde kalır.
        # Kuleler ayrı ve düz tepeli cap meshleri olarak üretilecektir.
        height_by_key = AtlasCastleShellBuilder._build_height_map(
            outer_ring=oriented_outer,
            inner_rings=oriented_holes,
            base_height_mm=height_mm,
            outer_multipliers=[1.0] * len(oriented_outer),
        )

        vertex_cache = {}

        all_rings = [oriented_outer]
        all_rings.extend(oriented_holes)

        bottom = []
        top = []

        for ring in all_rings:
            for point in ring:
                point_height_mm = AtlasCastleShellBuilder._height_for_point(
                    point=point,
                    height_by_key=height_by_key,
                    default_height_mm=height_mm,
                )

                bottom_point, top_point = AtlasCastleShellBuilder._get_vertex_pair(
                    point=point,
                    terrain_mesh=terrain_mesh,
                    height_mm=point_height_mm,
                    vertex_cache=vertex_cache,
                )

                bottom.append(bottom_point)
                top.append(top_point)

        triangles = []

        for flat_triangle in flat_triangles:
            p1_2d, p2_2d, p3_2d = flat_triangle

            if AtlasCastleShellBuilder._triangle_signed_area(flat_triangle) < 0:
                p2_2d, p3_2d = p3_2d, p2_2d

            h1 = AtlasCastleShellBuilder._height_for_point(
                point=p1_2d,
                height_by_key=height_by_key,
                default_height_mm=height_mm,
            )

            h2 = AtlasCastleShellBuilder._height_for_point(
                point=p2_2d,
                height_by_key=height_by_key,
                default_height_mm=height_mm,
            )

            h3 = AtlasCastleShellBuilder._height_for_point(
                point=p3_2d,
                height_by_key=height_by_key,
                default_height_mm=height_mm,
            )

            b1, t1 = AtlasCastleShellBuilder._get_vertex_pair(
                point=p1_2d,
                terrain_mesh=terrain_mesh,
                height_mm=h1,
                vertex_cache=vertex_cache,
            )

            b2, t2 = AtlasCastleShellBuilder._get_vertex_pair(
                point=p2_2d,
                terrain_mesh=terrain_mesh,
                height_mm=h2,
                vertex_cache=vertex_cache,
            )

            b3, t3 = AtlasCastleShellBuilder._get_vertex_pair(
                point=p3_2d,
                terrain_mesh=terrain_mesh,
                height_mm=h3,
                vertex_cache=vertex_cache,
            )

            # Üst yüzey
            triangles.append(
                (
                    t1,
                    t2,
                    t3,
                )
            )

            # Alt yüzey, ters yön
            triangles.append(
                (
                    b3,
                    b2,
                    b1,
                )
            )

        walls = []

        AtlasCastleShellBuilder._add_ring_walls(
            ring=oriented_outer,
            terrain_mesh=terrain_mesh,
            height_by_key=height_by_key,
            default_height_mm=height_mm,
            vertex_cache=vertex_cache,
            triangles=triangles,
            walls=walls,
            is_hole=False,
        )

        for hole in oriented_holes:
            AtlasCastleShellBuilder._add_ring_walls(
                ring=hole,
                terrain_mesh=terrain_mesh,
                height_by_key=height_by_key,
                default_height_mm=height_mm,
                vertex_cache=vertex_cache,
                triangles=triangles,
                walls=walls,
                is_hole=True,
            )

        if not triangles:
            return None

        tower_runs = height_profile.get(
            "tower_runs",
            [],
        )

        tower_point_count = height_profile.get(
            "tower_point_count",
            0,
        )

        return {
            "type": "castle_shell_foundation",
            "source_id": castle.get("id"),
            "castle_type": castle.get(
                "castle_type",
                tags.get(
                    "castle_type",
                    "castle",
                ),
            ),
            "name": tags.get("name"),
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "placement_mode": "foundation_first",
            "shell_height_mm": height_mm,
            "tower_height_multiplier": (
                AtlasCastleShellHeightProfiler.TOWER_HEIGHT_MULTIPLIER
            ),
            "tower_height_mm": (
                height_mm * AtlasCastleShellHeightProfiler.TOWER_HEIGHT_MULTIPLIER
            ),
            "tower_region_count": len(tower_runs),
            "tower_point_count": tower_point_count,
            "tower_runs": tower_runs,
            "tower_threshold_mm": height_profile.get(
                "threshold_mm",
                0.0,
            ),
            "outer_point_count": len(oriented_outer),
            "inner_ring_count": len(oriented_holes),
            "inner_point_count": sum(len(ring) for ring in oriented_holes),
            "roles_corrected": normalized.get(
                "roles_corrected",
                False,
            ),
        }

    @staticmethod
    def _build_height_map(
        outer_ring,
        inner_rings,
        base_height_mm,
        outer_multipliers,
    ):
        height_by_key = {}

        for index, point in enumerate(outer_ring):
            multiplier = 1.0

            if index < len(outer_multipliers):
                multiplier = float(outer_multipliers[index])

            point_height_mm = base_height_mm * multiplier

            height_by_key[AtlasCastleShellBuilder._point_key(point)] = point_height_mm

        for ring in inner_rings:
            for point in ring:
                height_by_key[AtlasCastleShellBuilder._point_key(point)] = (
                    base_height_mm
                )

        return height_by_key

    @staticmethod
    def _height_for_point(
        point,
        height_by_key,
        default_height_mm,
    ):
        return height_by_key.get(
            AtlasCastleShellBuilder._point_key(point),
            default_height_mm,
        )

    @staticmethod
    def _add_ring_walls(
        ring,
        terrain_mesh,
        height_by_key,
        default_height_mm,
        vertex_cache,
        triangles,
        walls,
        is_hole,
    ):
        point_count = len(ring)

        for index in range(point_count):
            next_index = (index + 1) % point_count

            point_1 = ring[index]
            point_2 = ring[next_index]

            height_1 = AtlasCastleShellBuilder._height_for_point(
                point=point_1,
                height_by_key=height_by_key,
                default_height_mm=default_height_mm,
            )

            height_2 = AtlasCastleShellBuilder._height_for_point(
                point=point_2,
                height_by_key=height_by_key,
                default_height_mm=default_height_mm,
            )

            b1, t1 = AtlasCastleShellBuilder._get_vertex_pair(
                point=point_1,
                terrain_mesh=terrain_mesh,
                height_mm=height_1,
                vertex_cache=vertex_cache,
            )

            b2, t2 = AtlasCastleShellBuilder._get_vertex_pair(
                point=point_2,
                terrain_mesh=terrain_mesh,
                height_mm=height_2,
                vertex_cache=vertex_cache,
            )

            if is_hole:
                triangles.append(
                    (
                        b1,
                        t2,
                        b2,
                    )
                )

                triangles.append(
                    (
                        b1,
                        t1,
                        t2,
                    )
                )

                walls.append(
                    (
                        b1,
                        t1,
                        t2,
                        b2,
                    )
                )
            else:
                triangles.append(
                    (
                        b1,
                        b2,
                        t2,
                    )
                )

                triangles.append(
                    (
                        b1,
                        t2,
                        t1,
                    )
                )

                walls.append(
                    (
                        b1,
                        b2,
                        t2,
                        t1,
                    )
                )

    @staticmethod
    def _get_vertex_pair(
        point,
        terrain_mesh,
        height_mm,
        vertex_cache,
    ):
        key = (
            AtlasCastleShellBuilder._point_key(point),
            round(
                float(height_mm),
                AtlasCastleShellBuilder.HEIGHT_PRECISION,
            ),
        )

        cached = vertex_cache.get(key)

        if cached is not None:
            return cached

        x = float(point[0])
        y = float(point[1])

        terrain_z = AtlasFoundationSampler.terrain_z_at_xy(
            terrain_mesh=terrain_mesh,
            x=x,
            y=y,
        )

        bottom_point = (
            x,
            y,
            terrain_z,
        )

        top_point = (
            x,
            y,
            terrain_z + height_mm,
        )

        pair = (
            bottom_point,
            top_point,
        )

        vertex_cache[key] = pair

        return pair

    @staticmethod
    def _read_positive_float(
        value,
        default,
    ):
        try:
            parsed = float(value)

            if parsed > 0:
                return parsed

        except (TypeError, ValueError):
            pass

        return default

    @staticmethod
    def _ensure_ccw(points):
        if AtlasCastleShellBuilder._signed_area(points) < 0:
            return list(reversed(points))

        return list(points)

    @staticmethod
    def _ensure_cw(points):
        if AtlasCastleShellBuilder._signed_area(points) > 0:
            return list(reversed(points))

        return list(points)

    @staticmethod
    def _signed_area(points):
        area = 0.0

        for index in range(len(points)):
            next_index = (index + 1) % len(points)

            x1, y1 = points[index]
            x2, y2 = points[next_index]

            area += x1 * y2
            area -= x2 * y1

        return area / 2.0

    @staticmethod
    def _triangle_signed_area(
        triangle,
    ):
        p1, p2, p3 = triangle

        return (
            p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
        ) / 2.0

    @staticmethod
    def _point_key(point):
        return (
            round(
                float(point[0]),
                AtlasCastleShellBuilder.POINT_PRECISION,
            ),
            round(
                float(point[1]),
                AtlasCastleShellBuilder.POINT_PRECISION,
            ),
        )

    @staticmethod
    def _count_triangles(meshes):
        return sum(len(mesh.get("triangles", [])) for mesh in meshes)
