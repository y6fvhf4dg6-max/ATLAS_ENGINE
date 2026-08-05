from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
    _normalize_identifier,
)


@dataclass(frozen=True, slots=True)
class AtlasSemanticArchitectureModel:
    landmark_family: str
    grammar_name: str
    components: tuple[
        AtlasSemanticArchitectureComponent,
        ...,
    ]
    profile_name: str = "generic_architecture"
    flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        landmark_family = _normalize_identifier(
            self.landmark_family,
            field_name="landmark_family",
        )
        grammar_name = _normalize_identifier(
            self.grammar_name,
            field_name="grammar_name",
        )
        profile_name = _normalize_identifier(
            self.profile_name,
            field_name="profile_name",
        )

        components = tuple(
            self.components
        )

        if not components:
            raise ValueError(
                "components must not be empty"
            )

        identities = set()

        for component in components:
            if not isinstance(
                component,
                AtlasSemanticArchitectureComponent,
            ):
                raise TypeError(
                    "components must contain "
                    "AtlasSemanticArchitectureComponent instances"
                )

            if (
                component.landmark_family
                != landmark_family
            ):
                raise ValueError(
                    "component landmark_family must match "
                    "model landmark_family"
                )

            identity = (
                component.role,
                component.instance_index,
            )

            if identity in identities:
                raise ValueError(
                    "duplicate component identity"
                )

            identities.add(
                identity
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
            "grammar_name",
            grammar_name,
        )
        object.__setattr__(
            self,
            "components",
            components,
        )
        object.__setattr__(
            self,
            "profile_name",
            profile_name,
        )
        object.__setattr__(
            self,
            "flags",
            flags,
        )

    def components_for_role(
        self,
        role,
    ) -> tuple[
        AtlasSemanticArchitectureComponent,
        ...,
    ]:
        normalized_role = _normalize_identifier(
            role,
            field_name="role",
        )

        return tuple(
            component
            for component in self.components
            if component.role == normalized_role
        )
