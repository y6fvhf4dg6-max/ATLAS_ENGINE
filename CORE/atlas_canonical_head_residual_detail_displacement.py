from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailDisplacement:
    detail_id: str
    topology: AtlasCanonicalHeadTopology
    displacement: np.ndarray

    def __post_init__(self) -> None:
        detail_id = self._normalize_identifier(
            self.detail_id,
            name="detail_id",
        )

        if not isinstance(
            self.topology,
            AtlasCanonicalHeadTopology,
        ):
            raise TypeError(
                "topology must be an "
                "AtlasCanonicalHeadTopology."
            )

        try:
            displacement = np.asarray(
                self.displacement,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "displacement must be numeric."
            ) from exc

        expected_shape = (
            self.topology.vertex_count,
            3,
        )

        if displacement.shape != expected_shape:
            raise ValueError(
                "displacement must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            displacement
        ).all():
            raise ValueError(
                "displacement must contain only finite values."
            )

        displacement = displacement.copy()
        displacement.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "detail_id",
            detail_id,
        )
        object.__setattr__(
            self,
            "displacement",
            displacement,
        )

    @property
    def connectivity_signature(
        self,
    ) -> str:
        return self.topology.connectivity_signature

    @staticmethod
    def _normalize_identifier(
        value: object,
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
