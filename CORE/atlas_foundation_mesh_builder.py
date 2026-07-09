# CORE/atlas_foundation_mesh_builder.py


class AtlasFoundationMeshBuilder:
    """
    ATLAS Foundation Mesh Builder v0.1

    Görev:
    - Building footprint'ten gerçek bir foundation mesh üretmek.

    Foundation;
    terrain üzerinde oluşan,
    binanın oturacağı fiziksel tabandır.

    Bu sınıf bina üretmez.
    """

    DEFAULT_THICKNESS_MM = 0.50

    @staticmethod
    def build(
        footprint_points,
        foundation_z,
        thickness_mm=DEFAULT_THICKNESS_MM,
    ):
        """
        Şimdilik sadece foundation geometrisini tarif eder.

        v0.2:
        Kapalı foundation mesh üretilecek.
        """

        if not footprint_points:
            return None

        return {
            "type": "foundation",
            "footprint": footprint_points,
            "foundation_z": foundation_z,
            "bottom_z": max(
                0.0,
                foundation_z - thickness_mm,
            ),
            "top_z": foundation_z,
            "thickness_mm": thickness_mm,
        }
