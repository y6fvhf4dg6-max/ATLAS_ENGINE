class AtlasDebugReporter:
    """
    ATLAS Debug Reporter v1.0

    Amaç:
    - Engine içindeki debug çıktılarını tek yerde toplamak.
    - Üretim algoritmasını raporlama kodundan ayırmak.
    - Kod tekrarını azaltmak.
    - Gelecekte log sistemi veya dosyaya yazma desteği eklemek.

    Bu sınıf STL üretmez.
    Mesh oluşturmaz.
    Sadece raporlama yapar.
    """

    @staticmethod
    def count_triangles(meshes):
        total = 0

        for mesh in meshes:
            if isinstance(mesh, dict):
                if mesh.get("triangles"):
                    total += len(mesh["triangles"])
                elif mesh.get("faces"):
                    total += len(mesh["faces"])

        return total

    @staticmethod
    def print_header():
        print("")
        print("=" * 60)
        print("ATLAS ENGINE AREA-FIRST / SCENE-FIRST MODE")
        print("=" * 60)

    @staticmethod
    def print_footer(
        output_path,
        xy_scale,
        meshes,
        buildings,
        roads,
    ):
        print("")
        print("=" * 60)
        print("ATLAS ENGINE STL EXPORTED")
        print("=" * 60)
        print("Mode      : area_first_scene_first_product")
        print(f"XY scale  : {xy_scale:.2f}")
        print(f"Meshes    : {len(meshes)}")
        print(f"Triangles : {AtlasDebugReporter.count_triangles(meshes)}")
        print(f"Buildings : {buildings}")
        print(f"Roads     : {roads}")
        print(output_path)
        print("=" * 60)
        print("")

    @staticmethod
    def print_xy_report(meshes, title):
        print("")
        print("=" * 60)
        print(title)
        print("=" * 60)

        for index, mesh in enumerate(meshes):
            mesh_type = mesh.get("type", "unknown")
            points = []

            points.extend(mesh.get("bottom", []))
            points.extend(mesh.get("top", []))

            for triangle in mesh.get("triangles", []):
                points.extend(triangle)

            if not points:
                continue

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            print(
                f"{index:03d} | {mesh_type:20s} | "
                f"x={min(xs):.2f}..{max(xs):.2f} | "
                f"y={min(ys):.2f}..{max(ys):.2f}"
            )

        print("=" * 60)

    @staticmethod
    def print_z_report(meshes, title):
        print("")
        print("=" * 60)
        print(title)
        print("=" * 60)

        for index, mesh in enumerate(meshes):
            mesh_type = mesh.get("type", "unknown")
            zs = []

            for tri in mesh.get("triangles", []):
                for point in tri:
                    zs.append(point[2])

            if not zs:
                continue

            print(
                f"{index:03d} | {mesh_type:20s} | "
                f"min_z={min(zs):.3f} | max_z={max(zs):.3f}"
            )

        print("=" * 60)

    @staticmethod
    def print_mesh_debug_report(meshes, title):
        print("")
        print("=" * 60)
        print(title)
        print("=" * 60)

        for index, mesh in enumerate(meshes):
            mesh_type = mesh.get("type", "unknown")
            triangles = mesh.get("triangles", [])

            xs = []
            ys = []
            zs = []

            for triangle in triangles:
                for point in triangle:
                    xs.append(point[0])
                    ys.append(point[1])
                    zs.append(point[2])

            if not triangles:
                print(f"{index:03d} | {mesh_type:20s} | tri=0 | no triangle data")
                continue

            print(
                f"{index:03d} | {mesh_type:20s} | "
                f"tri={len(triangles):5d} | "
                f"x={min(xs):7.2f}..{max(xs):7.2f} | "
                f"y={min(ys):7.2f}..{max(ys):7.2f} | "
                f"z={min(zs):7.2f}..{max(zs):7.2f}"
            )

        print("=" * 60)
