from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasLandmarkGeometry:
    footprint: tuple
    height_m: float
