from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadIdentityShape:
    identity_shape_id: str
    reference_geometry: AtlasCanonicalHeadGeometry
    identity_displacement: np.ndarray

    def __post_init__(self) -> None:
        identity_shape_id = self._normalize_identifier(
            self.identity_shape_id,
            name="identity_shape_id",
        )

        if not isinstance(
            self.reference_geometry,
            AtlasCanonicalHeadGeometry,
        ):
            raise TypeError(
                "reference_geometry must be an "
                "AtlasCanonicalHeadGeometry."
            )

        try:
            displacement = np.asarray(
                self.identity_displacement,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "identity_displacement must be numeric."
            ) from exc

        expected_shape = self.reference_geometry.vertices.shape

        if displacement.shape != expected_shape:
            raise ValueError(
                "identity_displacement must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            displacement
        ).all():
            raise ValueError(
                "identity_displacement must contain only finite values."
            )

        displacement = displacement.copy()
        displacement.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "identity_shape_id",
            identity_shape_id,
        )
        object.__setattr__(
            self,
            "identity_displacement",
            displacement,
        )

    @property
    def connectivity_signature(
        self,
    ) -> str:
        return (
            self.reference_geometry
            .connectivity_signature
        )

    @property
    def resolved_geometry(
        self,
    ) -> AtlasCanonicalHeadGeometry:
        return AtlasCanonicalHeadGeometry(
            topology=self.reference_geometry.topology,
            vertices=(
                self.reference_geometry.vertices
                + self.identity_displacement
            ),
        )

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
