from __future__ import annotations

from dataclasses import dataclass


def _normalize_identifier(
    value,
    *,
    field_name: str,
) -> str:
    normalized = "_".join(
        str(value).strip().lower().split()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class AtlasSemanticArchitectureComponent:
    landmark_family: str
    role: str
    geometry_kind: str
    parent_role: str | None = None
    instance_index: int = 0
    flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        landmark_family = _normalize_identifier(
            self.landmark_family,
            field_name="landmark_family",
        )
        role = _normalize_identifier(
            self.role,
            field_name="role",
        )
        geometry_kind = _normalize_identifier(
            self.geometry_kind,
            field_name="geometry_kind",
        )

        parent_role = self.parent_role

        if parent_role is not None:
            parent_role = _normalize_identifier(
                parent_role,
                field_name="parent_role",
            )

        instance_index = self.instance_index

        if (
            isinstance(instance_index, bool)
            or not isinstance(instance_index, int)
            or instance_index < 0
        ):
            raise ValueError(
                "instance_index must be a non-negative integer"
            )

        flags = tuple(
            _normalize_identifier(
                flag,
                field_name="flag",
            )
            for flag in self.flags
        )

        object.__setattr__(
            self,
            "landmark_family",
            landmark_family,
        )
        object.__setattr__(
            self,
            "role",
            role,
        )
        object.__setattr__(
            self,
            "geometry_kind",
            geometry_kind,
        )
        object.__setattr__(
            self,
            "parent_role",
            parent_role,
        )
        object.__setattr__(
            self,
            "instance_index",
            instance_index,
        )
        object.__setattr__(
            self,
            "flags",
            flags,
        )
