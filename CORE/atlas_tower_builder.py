"""
AtlasTowerBuilder – kule geometrisi üreticisi.

Yükseklik zinciri:
    1) height
    2) building:levels × FLOOR_HEIGHT_M
    3) min_height
    4) footprint tahmini
    5) DEFAULT_HEIGHT_M
"""

from dataclasses import dataclass

from CORE.atlas_tower_profile_resolver import AtlasTowerProfileResolver


@dataclass(frozen=True, slots=True)
class AtlasTowerGeometry:
    footprint: tuple
    height_m: float
    profile: str = "generic"


class AtlasTowerBuilder:
    DEFAULT_HEIGHT_M = 60.0
    FOOTPRINT_HEIGHT_FACTOR = 6.0
    FLOOR_HEIGHT_M = 3.5

    @staticmethod
    def _try_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_footprint(geometry):
        exterior = getattr(geometry, "exterior", geometry)
        coords = getattr(exterior, "coords", exterior)
        return tuple(coords)

    @staticmethod
    def _estimate_height_from_footprint(footprint):
        if not footprint:
            return None

        xs = [point[0] for point in footprint]
        ys = [point[1] for point in footprint]

        span = max(max(xs) - min(xs), max(ys) - min(ys))
        estimated = span * AtlasTowerBuilder.FOOTPRINT_HEIGHT_FACTOR

        if estimated <= AtlasTowerBuilder.DEFAULT_HEIGHT_M:
            return None

        return estimated

    @staticmethod
    def build(landmark) -> AtlasTowerGeometry:
        tags = getattr(landmark, "tags", {}) or {}
        footprint = AtlasTowerBuilder._normalize_footprint(
            landmark.geometry
        )

        height_m = AtlasTowerBuilder._try_float(
            tags.get("height")
        )

        if height_m is None:
            levels = tags.get("building:levels")
            if levels and str(levels).isdigit():
                height_m = (
                    int(levels)
                    * AtlasTowerBuilder.FLOOR_HEIGHT_M
                )

        if height_m is None:
            height_m = AtlasTowerBuilder._try_float(
                tags.get("min_height")
            )

        if height_m is None:
            height_m = (
                AtlasTowerBuilder._estimate_height_from_footprint(
                    footprint
                )
            )

        if height_m is None:
            height_m = AtlasTowerBuilder.DEFAULT_HEIGHT_M

        return AtlasTowerGeometry(
            footprint=footprint,
            height_m=height_m,
            profile=AtlasTowerProfileResolver.resolve(tags),
        )
