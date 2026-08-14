from dataclasses import dataclass, fields
from typing import Tuple


RGB = Tuple[int, int, int]


@dataclass(frozen=True)
class AtlasProductPreviewMaterialProfile:
    name: str
    frame_rgb: RGB
    building_rgb: RGB
    building_wall_rgb: RGB
    building_roof_rgb: RGB
    landmark_rgb: RGB
    terrain_rgb: RGB
    road_rgb: RGB
    green_rgb: RGB
    tree_rgb: RGB
    water_rgb: RGB
    label_plate_rgb: RGB = (28, 28, 28)
    label_text_rgb: RGB = (232, 228, 216)
    landmark_roof_rgb: RGB | None = None

    def __post_init__(self):
        for field in fields(self):
            if not field.name.endswith("_rgb"):
                continue

            value = getattr(self, field.name)

            if (
                field.name == "landmark_roof_rgb"
                and value is None
            ):
                continue

            if (
                not isinstance(value, tuple)
                or len(value) != 3
                or any(
                    not isinstance(channel, int)
                    or isinstance(channel, bool)
                    or channel < 0
                    or channel > 255
                    for channel in value
                )
            ):
                raise ValueError(
                    f"{field.name} must be an RGB tuple with integer "
                    "channels between 0 and 255"
                )

    @classmethod
    def competitor_comparison_v1(cls):
        return cls(
            name="COMPETITOR_COMPARISON_V1",
            frame_rgb=(28, 28, 28),
            building_rgb=(232, 228, 216),
            building_wall_rgb=(232, 228, 216),
            building_roof_rgb=(156, 48, 42),
            landmark_rgb=(232, 228, 216),
            terrain_rgb=(205, 190, 160),
            road_rgb=(190, 184, 170),
            green_rgb=(105, 137, 78),
            tree_rgb=(73, 105, 58),
            water_rgb=(104, 165, 184),
            label_plate_rgb=(28, 28, 28),
            label_text_rgb=(232, 228, 216),
        )

    @classmethod
    def koeln_premium_v1(cls):
        black = (20, 20, 20)
        desert_tan = (205, 190, 160)
        brick_red = (156, 48, 42)
        dark_green = (73, 105, 58)
        blue = (70, 140, 180)

        return cls(
            name="KOELN_PREMIUM_V1",
            frame_rgb=black,
            building_rgb=desert_tan,
            building_wall_rgb=desert_tan,
            building_roof_rgb=brick_red,
            landmark_rgb=desert_tan,
            terrain_rgb=desert_tan,
            road_rgb=black,
            green_rgb=dark_green,
            tree_rgb=dark_green,
            water_rgb=blue,
            label_plate_rgb=desert_tan,
            label_text_rgb=black,
        )

    @classmethod
    def bonn_birthplace_v1(cls):
        black = (20, 20, 20)
        white = (245, 245, 240)
        desert_tan = (205, 190, 160)
        brick_red = (156, 48, 42)
        dark_green = (73, 105, 58)

        return cls(
            name="BONN_BIRTHPLACE_V1",
            frame_rgb=black,
            building_rgb=desert_tan,
            building_wall_rgb=desert_tan,
            building_roof_rgb=desert_tan,
            landmark_rgb=desert_tan,
            terrain_rgb=white,
            road_rgb=black,
            green_rgb=dark_green,
            tree_rgb=dark_green,
            water_rgb=white,
            label_plate_rgb=white,
            label_text_rgb=black,
            landmark_roof_rgb=brick_red,
        )

    @classmethod
    def dalyan_kaunos_premium_v1(cls):
        ivory = (242, 235, 218)
        sandstone = (190, 145, 92)
        olive = (91, 112, 63)
        charcoal = (26, 25, 23)
        mediterranean_blue = (66, 126, 151)

        return cls(
            name="DALYAN_KAUNOS_PREMIUM_V1",
            frame_rgb=charcoal,
            building_rgb=ivory,
            building_wall_rgb=ivory,
            building_roof_rgb=ivory,
            landmark_rgb=sandstone,
            terrain_rgb=ivory,
            road_rgb=ivory,
            green_rgb=olive,
            tree_rgb=olive,
            water_rgb=mediterranean_blue,
            label_plate_rgb=ivory,
            label_text_rgb=charcoal,
        )

