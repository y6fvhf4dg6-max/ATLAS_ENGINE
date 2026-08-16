from __future__ import annotations

import math
from dataclasses import dataclass


def _normalize_identifier(value, *, field_name: str) -> str:
    normalized = "_".join(
        str(value).strip().lower().split()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


def _finite_triplet(value, *, field_name: str) -> tuple[float, float, float]:
    if isinstance(value, (str, bytes)):
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    try:
        items = tuple(value)
    except TypeError as exc:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        ) from exc

    if len(items) != 3:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    try:
        result = tuple(float(item) for item in items)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must contain numeric values"
        ) from exc

    if not all(math.isfinite(item) for item in result):
        raise ValueError(
            f"{field_name} must contain only finite values"
        )

    return result


@dataclass(frozen=True, slots=True)
class AtlasSemanticReliefRepetition:
    repeat_group_id: str
    quantity: int
    spacing_mm: tuple[float, float, float]
    interchangeable: bool

    def __post_init__(self) -> None:
        if not isinstance(self.interchangeable, bool):
            raise ValueError(
                "interchangeable must be a boolean"
            )

        if (
            isinstance(self.quantity, bool)
            or not isinstance(self.quantity, int)
            or self.quantity <= 0
        ):
            raise ValueError(
                "quantity must be a positive integer"
            )

        object.__setattr__(
            self,
            "repeat_group_id",
            _normalize_identifier(
                self.repeat_group_id,
                field_name="repeat_group_id",
            ),
        )
        spacing_mm = _finite_triplet(
            self.spacing_mm,
            field_name="spacing_mm",
        )

        if (
            self.quantity > 1
            and spacing_mm == (0.0, 0.0, 0.0)
        ):
            raise ValueError(
                "spacing_mm must be nonzero for multiple instances"
            )

        object.__setattr__(
            self,
            "spacing_mm",
            spacing_mm,
        )
