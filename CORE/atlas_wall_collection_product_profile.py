from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasWallCollectionProductProfile:
    """
    Immutable product profile for framed My Life Map
    Wall Collection models.
    """

    name: str
    product_type: str
    frame_width_mm: float
    frame_height_mm: float
    model_area_mm: float
    model_min_height_mm: float
    model_max_height_mm: float
