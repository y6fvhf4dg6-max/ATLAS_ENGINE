"""
AtlasTowerBuilder – kule geometrisi üreticisi.
Yükseklik zinciri (öncelik):
    1) height=*  (sayısal)
    2) building:levels × FLOOR_HEIGHT_M
    3) min_height (sayısal)
    4) DEFAULT_HEIGHT_M
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasTowerGeometry:
    footprint: tuple
    height_m: float


class AtlasTowerBuilder:
    DEFAULT_HEIGHT_M = 60.0
    FOOTPRINT_HEIGHT_FACTOR = 6.0
    FLOOR_HEIGHT_M   = 3.5

    @staticmethod
    def _try_float(val: str):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None
    @staticmethod
    def _estimate_height_from_footprint(footprint):
        if not footprint:
            return None

        xs = [p[0] for p in footprint]
        ys = [p[1] for p in footprint]

        span = max(max(xs) - min(xs), max(ys) - min(ys))
        estimated = span * AtlasTowerBuilder.FOOTPRINT_HEIGHT_FACTOR

        if estimated <= AtlasTowerBuilder.DEFAULT_HEIGHT_M:
            return None
        return estimated


    @staticmethod
    def build(landmark) -> "AtlasTowerGeometry":
        height_m = None

        # 1) height
        height_m = AtlasTowerBuilder._try_float(landmark.tags.get("height"))

        # 2) building:levels
        if height_m is None:
            levels = landmark.tags.get("building:levels")
            if levels and levels.isdigit():
                height_m = int(levels) * AtlasTowerBuilder.FLOOR_HEIGHT_M

        # 3) min_height
        if height_m is None:
            height_m = AtlasTowerBuilder._try_float(landmark.tags.get("min_height"))
        # 4) footprint tahmini
        if height_m is None:
            height_m = AtlasTowerBuilder._estimate_height_from_footprint(
                landmark.geometry
            )
        # 4) varsayılan
        if height_m is None:
            height_m = AtlasTowerBuilder.DEFAULT_HEIGHT_M

        return AtlasTowerGeometry(
            footprint=landmark.geometry,
            height_m=height_m,
        )
