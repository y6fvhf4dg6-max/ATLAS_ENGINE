from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasLighthouseGeometry:
    footprint: tuple
    height_m: float


class AtlasLighthouseBuilder:
    DEFAULT_HEIGHT_M = 35.0

    @staticmethod
    def _try_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def build(landmark):
        tags = getattr(landmark, "tags", {}) or {}

        height_m = AtlasLighthouseBuilder._try_float(
            tags.get("height")
        )

        if height_m is None:
            height_m = AtlasLighthouseBuilder.DEFAULT_HEIGHT_M

        return AtlasLighthouseGeometry(
            footprint=tuple(landmark.geometry),
            height_m=height_m,
        )
