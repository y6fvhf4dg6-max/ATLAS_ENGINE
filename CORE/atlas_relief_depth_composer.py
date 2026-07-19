from __future__ import annotations

import math
from typing import Any

import numpy as np


class AtlasReliefDepthComposer:
    """
    Combines multiscale relief bands into a deterministic
    unnormalized depth candidate.

    Broad form receives the strongest default weight.
    Medium detail is reduced.
    Micro detail is limited before weighting so image noise
    and very small texture cannot dominate the relief.
    """

    @staticmethod
    def compose(
        *,
        form: Any,
        detail: Any,
        micro_detail: Any,
        form_weight: float = 1.0,
        detail_weight: float = 0.35,
        micro_detail_weight: float = 0.10,
        micro_detail_limit: float = 0.05,
    ) -> dict[str, Any]:
        form_array = (
            AtlasReliefDepthComposer
            ._as_valid_array(
                form,
                name="form",
            )
        )

        detail_array = (
            AtlasReliefDepthComposer
            ._as_valid_array(
                detail,
                name="detail",
            )
        )

        micro_detail_array = (
            AtlasReliefDepthComposer
            ._as_valid_array(
                micro_detail,
                name="micro_detail",
            )
        )

        if not (
            form_array.shape
            == detail_array.shape
            == micro_detail_array.shape
        ):
            raise ValueError(
                "Relief bands must have identical shapes."
            )

        form_weight_value = (
            AtlasReliefDepthComposer
            ._validate_nonnegative_parameter(
                form_weight,
                name="form_weight",
            )
        )

        detail_weight_value = (
            AtlasReliefDepthComposer
            ._validate_nonnegative_parameter(
                detail_weight,
                name="detail_weight",
            )
        )

        micro_detail_weight_value = (
            AtlasReliefDepthComposer
            ._validate_nonnegative_parameter(
                micro_detail_weight,
                name="micro_detail_weight",
            )
        )

        micro_detail_limit_value = (
            AtlasReliefDepthComposer
            ._validate_positive_parameter(
                micro_detail_limit,
                name="micro_detail_limit",
            )
        )

        weighted_form = (
            form_array
            * form_weight_value
        )

        weighted_detail = (
            detail_array
            * detail_weight_value
        )

        limited_micro_detail = np.clip(
            micro_detail_array,
            -micro_detail_limit_value,
            micro_detail_limit_value,
        )

        weighted_micro_detail = (
            limited_micro_detail
            * micro_detail_weight_value
        )

        depth_candidate = (
            weighted_form
            + weighted_detail
            + weighted_micro_detail
        )

        return {
            "type": "relief_depth_candidate",
            "form_weight": form_weight_value,
            "detail_weight": detail_weight_value,
            "micro_detail_weight": (
                micro_detail_weight_value
            ),
            "micro_detail_limit": (
                micro_detail_limit_value
            ),
            "weighted_form": weighted_form.astype(
                np.float64,
                copy=True,
            ),
            "weighted_detail": weighted_detail.astype(
                np.float64,
                copy=True,
            ),
            "limited_micro_detail": (
                limited_micro_detail.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "weighted_micro_detail": (
                weighted_micro_detail.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "depth_candidate": depth_candidate.astype(
                np.float64,
                copy=True,
            ),
        }

    @staticmethod
    def _validate_nonnegative_parameter(
        value: Any,
        *,
        name: str,
    ) -> float:
        numeric_value = (
            AtlasReliefDepthComposer
            ._as_finite_number(
                value,
                name=name,
            )
        )

        if numeric_value < 0.0:
            raise ValueError(
                f"{name} must not be negative."
            )

        return numeric_value

    @staticmethod
    def _validate_positive_parameter(
        value: Any,
        *,
        name: str,
    ) -> float:
        numeric_value = (
            AtlasReliefDepthComposer
            ._as_finite_number(
                value,
                name=name,
            )
        )

        if numeric_value <= 0.0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return numeric_value

    @staticmethod
    def _as_finite_number(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric_value = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(numeric_value):
            raise ValueError(
                f"{name} must be finite."
            )

        return numeric_value

    @staticmethod
    def _as_valid_array(
        values: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            array = np.asarray(
                values,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if array.ndim != 2:
            raise ValueError(
                f"{name} must be two-dimensional."
            )

        if array.size == 0:
            raise ValueError(
                f"{name} must not be empty."
            )

        if not np.isfinite(array).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return array.copy()
