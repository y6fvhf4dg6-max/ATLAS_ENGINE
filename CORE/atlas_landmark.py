from dataclasses import dataclass
from typing import Any, Mapping

from CORE.atlas_landmark_type import AtlasLandmarkType


@dataclass(frozen=True, slots=True)
class AtlasLandmark:
    id: int
    landmark_type: AtlasLandmarkType
    geometry: tuple
    tags: Mapping[str, Any]
    source: str
