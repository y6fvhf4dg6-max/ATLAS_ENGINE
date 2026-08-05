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
class AtlasChurchSemanticProfile:
    name: str
    architectural_style: str
    plan_type: str
    tower_scheme: str
    roof_character: str
    facade_rhythm: str

    def __post_init__(self) -> None:
        for field_name in (
            "name",
            "architectural_style",
            "plan_type",
            "tower_scheme",
            "roof_character",
            "facade_rhythm",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_identifier(
                    getattr(
                        self,
                        field_name,
                    ),
                    field_name=field_name,
                ),
            )


class AtlasChurchSemanticProfileSystem:
    _PROFILES = {
        "generic_church": AtlasChurchSemanticProfile(
            name="generic_church",
            architectural_style="generic",
            plan_type="cross_plan",
            tower_scheme="grammar_driven",
            roof_character="pitched",
            facade_rhythm="regular",
        ),
        "romanesque_cathedral": AtlasChurchSemanticProfile(
            name="romanesque_cathedral",
            architectural_style="romanesque",
            plan_type="basilica_cross_plan",
            tower_scheme="multi_tower",
            roof_character="stepped_pitched",
            facade_rhythm="heavy_round_arch",
        ),
    }

    @classmethod
    def resolve(
        cls,
        profile_name,
    ) -> AtlasChurchSemanticProfile:
        normalized_name = _normalize_identifier(
            profile_name,
            field_name="profile_name",
        )

        profile = cls._PROFILES.get(
            normalized_name
        )

        if profile is None:
            raise ValueError(
                "unsupported church semantic profile: "
                f"{normalized_name}"
            )

        return profile
