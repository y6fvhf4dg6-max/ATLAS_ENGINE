from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasRockCutTombGeometry:
    footprint: tuple
    height_m: float


class AtlasRockCutTombBuilder:
    DEFAULT_HEIGHT_M = 3.0

    @staticmethod
    def _try_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def build(cls, landmark) -> AtlasRockCutTombGeometry:
        tags = getattr(landmark, "tags", {}) or {}

        height_m = cls._try_float(
            tags.get("height")
        )

        if height_m is None or height_m <= 0.0:
            height_m = cls.DEFAULT_HEIGHT_M

        return AtlasRockCutTombGeometry(
            footprint=tuple(landmark.geometry),
            height_m=height_m,
        )
