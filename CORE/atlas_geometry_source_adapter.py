from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)


class AtlasGeometrySourceAdapter(ABC):
    @abstractmethod
    def adapt(
        self,
        source: Any,
    ) -> AtlasGeometrySourceResult:
        raise NotImplementedError

    @staticmethod
    def validate_result(
        result: Any,
    ) -> AtlasGeometrySourceResult:
        if not isinstance(
            result,
            AtlasGeometrySourceResult,
        ):
            raise TypeError(
                "result must be an AtlasGeometrySourceResult"
            )

        return result

    @classmethod
    def validate_projection_mode(
        cls,
        result: Any,
        projection_mode: Any,
    ) -> str:
        canonical_result = cls.validate_result(
            result,
        )

        return canonical_result.require_projection_mode(
            projection_mode,
        )
