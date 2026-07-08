"""
ATLAS Engine 2.0

Module : Adaptive Detail Engine
Version: 1.0

Purpose:
Calculate automatic detail thresholds based on model scale.

Core idea:
Real world size / model size = scale ratio

Example:
1000 m real area / 200 mm model = 1:5000
"""

class AtlasDetailEngine:

    def __init__(self, real_world_size_m, model_size_mm):
        self.real_world_size_m = real_world_size_m
        self.model_size_mm = model_size_mm

        self.real_world_size_mm = real_world_size_m * 1000
        self.scale_ratio = self.real_world_size_mm / model_size_mm

    def model_mm_to_real_m(self, model_mm):
        return (model_mm * self.scale_ratio) / 1000

    def real_m_to_model_mm(self, real_m):
        return (real_m * 1000) / self.scale_ratio

    def minimum_visible_real_size_m(self):
        return self.model_mm_to_real_m(1.0)

    def minimum_building_area_m2(self):
        min_side_m = self.minimum_visible_real_size_m()
        return min_side_m * min_side_m

    def minimum_road_width_m(self):
        return self.minimum_visible_real_size_m()

    def minimum_water_width_m(self):
        return self.minimum_visible_real_size_m() * 1.5

    def minimum_park_area_m2(self):
        min_side_m = self.minimum_visible_real_size_m() * 3
        return min_side_m * min_side_m

    def should_show_footways(self):
        return self.scale_ratio <= 2500

    def should_show_trees_individually(self):
        return self.scale_ratio <= 1000

    def should_show_roof_detail(self):
        return self.scale_ratio <= 1500

    def report(self):
        print()
        print("=" * 60)
        print("ATLAS ADAPTIVE DETAIL ENGINE v1.0")
        print("=" * 60)
        print("Real world size :", self.real_world_size_m, "m")
        print("Model size      :", self.model_size_mm, "mm")
        print("Scale           : 1:", round(self.scale_ratio))
        print()
        print("1 mm model      :", round(self.minimum_visible_real_size_m(), 2), "m real")
        print("Min building    :", round(self.minimum_building_area_m2(), 2), "m²")
        print("Min road width  :", round(self.minimum_road_width_m(), 2), "m")
        print("Min water width :", round(self.minimum_water_width_m(), 2), "m")
        print("Min park area   :", round(self.minimum_park_area_m2(), 2), "m²")
        print()
        print("Show footways   :", self.should_show_footways())
        print("Show trees      :", self.should_show_trees_individually())
        print("Show roof detail:", self.should_show_roof_detail())
        print("=" * 60)


def main():
    detail = AtlasDetailEngine(
        real_world_size_m=1000,
        model_size_mm=200
    )

    detail.report()


if __name__ == "__main__":
    main()