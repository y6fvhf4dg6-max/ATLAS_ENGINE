# CORE/atlas_base_plate_cutter.py


class AtlasBasePlateCutter:
    """
    ATLAS Base Plate Cutter v0.1

    Güvenli başlangıç noktası.
    Base plate'i değiştirmez; sadece raporlar.
    """

    @staticmethod
    def build(base_plate, road_polygons=None, debug=True):
        if road_polygons is None:
            road_polygons = []

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS BASE PLATE CUTTER REPORT")
            print("=" * 60)
            print(f"Base plate type : {base_plate.get('type', 'unknown')}")
            print(f"Road polygons   : {len(road_polygons)}")
            print("Status          : pass_through")
            print("=" * 60)
            print("")

        return base_plate
