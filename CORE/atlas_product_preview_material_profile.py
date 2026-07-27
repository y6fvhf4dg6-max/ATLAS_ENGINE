from dataclasses import dataclass, fields
from typing import Tuple


RGB = Tuple[int, int, int]


@dataclass(frozen=True)
class AtlasProductPreviewMaterialProfile:
    name: str
    frame_rgb: RGB
    building_rgb: RGB
    terrain_rgb: RGB
    road_rgb: RGB
    green_rgb: RGB
    tree_rgb: RGB
    water_rgb: RGB

    def __post_init__(self):
        for field in fields(self):
            if not field.name.endswith("_rgb"):
                continue

            value = getattr(self, field.name)

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
            terrain_rgb=(205, 190, 160),
            road_rgb=(190, 184, 170),
            green_rgb=(105, 137, 78),
            tree_rgb=(73, 105, 58),
            water_rgb=(104, 165, 184),
        )
