from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral
from types import MappingProxyType
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadTopology:
    topology_id: str
    vertex_count: int
    faces: tuple[tuple[int, int, int], ...]
    semantic_vertex_regions: Mapping[str, tuple[int, ...]]

    def __post_init__(self) -> None:
        topology_id = self._normalize_identifier(
            self.topology_id,
            name="topology_id",
        )
        vertex_count = self._normalize_vertex_count(
            self.vertex_count,
        )
        faces = self._normalize_faces(
            self.faces,
            vertex_count=vertex_count,
        )
        semantic_vertex_regions = (
            self._normalize_semantic_vertex_regions(
                self.semantic_vertex_regions,
                vertex_count=vertex_count,
            )
        )

        object.__setattr__(
            self,
            "topology_id",
            topology_id,
        )
        object.__setattr__(
            self,
            "vertex_count",
            vertex_count,
        )
        object.__setattr__(
            self,
            "faces",
            faces,
        )
        object.__setattr__(
            self,
            "semantic_vertex_regions",
            MappingProxyType(
                semantic_vertex_regions
            ),
        )

    @property
    def connectivity_signature(self) -> str:
        payload = json.dumps(
            {
                "vertex_count": self.vertex_count,
                "faces": self.faces,
            },
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(
            payload
        ).hexdigest()

    @staticmethod
    def _normalize_identifier(
        value: Any,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = "_".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_vertex_count(
        value: Any,
    ) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise TypeError(
                "vertex_count must be an integer."
            )

        vertex_count = int(
            value
        )

        if vertex_count <= 0:
            raise ValueError(
                "vertex_count must be greater than zero."
            )

        return vertex_count

    @classmethod
    def _normalize_faces(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> tuple[tuple[int, int, int], ...]:
        if isinstance(
            value,
            (str, bytes),
        ):
            raise TypeError(
                "faces must be a non-empty sequence."
            )

        try:
            raw_faces = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "faces must be a non-empty sequence."
            ) from exc

        if not raw_faces:
            raise ValueError(
                "faces must not be empty."
            )

        normalized_faces = []

        for raw_face in raw_faces:
            try:
                indices = tuple(
                    raw_face
                )
            except TypeError as exc:
                raise TypeError(
                    "each face must contain exactly three vertex indices."
                ) from exc

            if len(indices) != 3:
                raise ValueError(
                    "each face must contain exactly three vertex indices."
                )

            normalized = tuple(
                cls._normalize_vertex_index(
                    index,
                    vertex_count=vertex_count,
                )
                for index in indices
            )

            if len(
                set(normalized)
            ) != 3:
                raise ValueError(
                    "face vertex indices must be distinct."
                )

            normalized_faces.append(
                normalized
            )

        if len(
            normalized_faces
        ) != len(
            set(normalized_faces)
        ):
            raise ValueError(
                "faces must be unique."
            )

        return tuple(
            normalized_faces
        )

    @classmethod
    def _normalize_semantic_vertex_regions(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> dict[str, tuple[int, ...]]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "semantic_vertex_regions must be a mapping."
            )

        if not value:
            raise ValueError(
                "semantic_vertex_regions must not be empty."
            )

        normalized_regions = {}

        for raw_name, raw_indices in value.items():
            name = cls._normalize_identifier(
                raw_name,
                name="semantic region name",
            )

            try:
                indices = tuple(
                    raw_indices
                )
            except TypeError as exc:
                raise TypeError(
                    f"semantic region {name} must contain vertex indices."
                ) from exc

            if not indices:
                raise ValueError(
                    f"semantic region {name} must not be empty."
                )

            normalized_indices = tuple(
                cls._normalize_vertex_index(
                    index,
                    vertex_count=vertex_count,
                )
                for index in indices
            )

            if len(
                normalized_indices
            ) != len(
                set(normalized_indices)
            ):
                raise ValueError(
                    f"semantic region {name} vertex indices must be unique."
                )

            if name in normalized_regions:
                raise ValueError(
                    "semantic region names must be unique after normalization."
                )

            normalized_regions[
                name
            ] = normalized_indices

        return normalized_regions

    @staticmethod
    def _normalize_vertex_index(
        value: Any,
        *,
        vertex_count: int,
    ) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise TypeError(
                "vertex index must be an integer."
            )

        index = int(
            value
        )

        if (
            index < 0
            or index >= vertex_count
        ):
            raise ValueError(
                "vertex index must be inside vertex_count."
            )

        return index
