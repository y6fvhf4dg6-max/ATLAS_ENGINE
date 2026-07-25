from dataclasses import dataclass


@dataclass(frozen=True, slots=True, init=False)
class AtlasLandmarkGeometry:
    footprint: tuple
    height_m: float
    height_mm: float

    def __init__(
        self,
        footprint,
        *,
        height_m=None,
        height_mm=None,
    ):
        if height_m is None and height_mm is None:
            raise TypeError(
                "Either height_m or height_mm must be provided"
            )

        if height_m is not None and height_mm is not None:
            raise TypeError(
                "Provide only one of height_m or height_mm"
            )

        if height_m is not None:
            resolved_height_m = float(height_m)
            resolved_height_mm = resolved_height_m * 1000.0
        else:
            resolved_height_mm = float(height_mm)
            resolved_height_m = resolved_height_mm / 1000.0

        object.__setattr__(self, "footprint", tuple(footprint))
        object.__setattr__(self, "height_m", resolved_height_m)
        object.__setattr__(self, "height_mm", resolved_height_mm)
