from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_relief_normal_height_integrator import (
    AtlasReliefNormalHeightIntegrator,
)
from CORE.atlas_relief_normal_structure_detail_decomposer import (
    AtlasReliefNormalStructureDetailDecomposer,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadDsineResidualDetailFieldResult:
    scalar_detail_field: np.ndarray
    confidence_field: np.ndarray

    def __post_init__(self) -> None:
        scalar_detail_field = np.asarray(
            self.scalar_detail_field,
            dtype=np.float64,
        )
        confidence_field = np.asarray(
            self.confidence_field,
            dtype=np.float64,
        )

        if scalar_detail_field.ndim != 2:
            raise ValueError(
                "scalar_detail_field must be two-dimensional."
            )

        if confidence_field.shape != scalar_detail_field.shape:
            raise ValueError(
                "confidence_field shape must match "
                "scalar_detail_field."
            )

        if not np.isfinite(
            scalar_detail_field
        ).all():
            raise ValueError(
                "scalar_detail_field must contain only finite values."
            )

        if not np.isfinite(
            confidence_field
        ).all():
            raise ValueError(
                "confidence_field must contain only finite values."
            )

        if (
            np.any(
                confidence_field < 0.0
            )
            or np.any(
                confidence_field > 1.0
            )
        ):
            raise ValueError(
                "confidence_field values must be "
                "in the 0.0..1.0 range."
            )

        scalar_snapshot = scalar_detail_field.copy()
        confidence_snapshot = confidence_field.copy()

        scalar_snapshot.setflags(
            write=False
        )
        confidence_snapshot.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "scalar_detail_field",
            scalar_snapshot,
        )
        object.__setattr__(
            self,
            "confidence_field",
            confidence_snapshot,
        )


class AtlasCanonicalHeadDsineResidualDetailFieldSource:
    @classmethod
    def build(
        cls,
        *,
        normals: Any,
        confidence_field: Any,
        mask: Any | None = None,
        structure_radius: int = 5,
    ) -> AtlasCanonicalHeadDsineResidualDetailFieldResult:
        try:
            normal_array = np.asarray(
                normals,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "normals must be numeric."
            ) from exc

        if (
            normal_array.ndim != 3
            or normal_array.shape[2] != 3
        ):
            raise ValueError(
                "normals must have shape "
                "(rows, columns, 3)."
            )

        if not np.isfinite(
            normal_array
        ).all():
            raise ValueError(
                "normals must contain only finite values."
            )

        try:
            confidence = np.asarray(
                confidence_field,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "confidence_field must be numeric."
            ) from exc

        if confidence.shape != normal_array.shape[:2]:
            raise ValueError(
                "confidence_field shape must match "
                "the normal field."
            )

        if not np.isfinite(
            confidence
        ).all():
            raise ValueError(
                "confidence_field must contain only finite values."
            )

        if (
            np.any(
                confidence < 0.0
            )
            or np.any(
                confidence > 1.0
            )
        ):
            raise ValueError(
                "confidence_field values must be "
                "in the 0.0..1.0 range."
            )

        if mask is None:
            active_mask = None
        else:
            try:
                active_mask = np.asarray(
                    mask,
                    dtype=np.float64,
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "mask must be numeric."
                ) from exc

            if active_mask.shape != normal_array.shape[:2]:
                raise ValueError(
                    "mask shape must match "
                    "the normal field."
                )

            if not np.isfinite(
                active_mask
            ).all():
                raise ValueError(
                    "mask must contain only finite values."
                )

            active_mask = np.clip(
                active_mask,
                0.0,
                1.0,
            )

            if not np.any(
                active_mask > 0.0
            ):
                raise ValueError(
                    "mask must contain at least "
                    "one active pixel."
                )

        _, detail_normals = (
            AtlasReliefNormalStructureDetailDecomposer
            .decompose(
                normal_array,
                mask=active_mask,
                structure_radius=structure_radius,
            )
        )

        scalar_detail_field = (
            AtlasReliefNormalHeightIntegrator
            .integrate(
                detail_normals,
                mask=active_mask,
                normalize_output=False,
            )
        )

        scalar_detail_field = np.asarray(
            scalar_detail_field,
            dtype=np.float64,
        )

        if active_mask is None:
            scalar_detail_field = (
                scalar_detail_field
                - float(
                    np.mean(
                        scalar_detail_field
                    )
                )
            )
        else:
            active = (
                active_mask > 0.0
            )

            active_mean = float(
                np.mean(
                    scalar_detail_field[
                        active
                    ]
                )
            )

            scalar_detail_field = np.where(
                active,
                scalar_detail_field
                - active_mean,
                0.0,
            )

        return (
            AtlasCanonicalHeadDsineResidualDetailFieldResult(
                scalar_detail_field=scalar_detail_field,
                confidence_field=confidence,
            )
        )
