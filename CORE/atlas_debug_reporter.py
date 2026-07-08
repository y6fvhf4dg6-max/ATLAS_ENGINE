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
