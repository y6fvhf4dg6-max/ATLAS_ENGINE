from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevel,
)
from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


@dataclass(frozen=True, slots=True)
class AtlasLoDComponentVisibilityDecision:
    component: AtlasSemanticArchitectureComponent
    level: AtlasLoDLevel
    required_feature: str
    visible: bool

    def __post_init__(self) -> None:
        if not isinstance(
            self.component,
            AtlasSemanticArchitectureComponent,
        ):
            raise TypeError(
                "component must be an "
                "AtlasSemanticArchitectureComponent"
            )

        if not isinstance(
            self.level,
            AtlasLoDLevel,
        ):
            raise TypeError(
                "level must be an AtlasLoDLevel"
            )

        required_feature = "_".join(
            str(
                self.required_feature
            ).strip().lower().split()
        )

        if not required_feature:
            raise ValueError(
                "required_feature must not be blank"
            )

        if not isinstance(
            self.visible,
            bool,
        ):
            raise TypeError(
                "visible must be a boolean"
            )

        object.__setattr__(
            self,
            "required_feature",
            required_feature,
        )


class AtlasLoDComponentVisibilityPolicy:
    _ROLE_TO_FEATURE = {
        "footprint": "footprint",
        "foundation": "base_mass",
        "base_mass": "base_mass",
        "body": "main_body",
        "nave": "main_body",
        "transept": "main_body",
        "prayer_hall": "main_body",
        "roof": "primary_roof",
        "roof_section": "primary_roof",
        "primary_roof": "primary_roof",
        "tower": "tower",
        "crossing_tower": "tower",
        "minaret": "tower",
        "minaret_body": "tower",
        "minaret_cap": "tower",
        "main_dome": "dome",
        "dome": "dome",
        "dome_drum": "dome",
        "apse": "apse",
        "facade_opening": "facade_opening",
        "window_bay_system": "facade_opening",
        "facade_structural_detail": (
            "structural_detail"
        ),
        "structural_detail": (
            "structural_detail"
        ),
        "buttress_system": "structural_detail",
        "ornament": "ornament",
        "architectural_relief": (
            "architectural_relief"
        ),
    }

    @classmethod
    def required_feature(
        cls,
        component: AtlasSemanticArchitectureComponent,
    ) -> str:
        cls._validate_component(
            component
        )

        return cls._ROLE_TO_FEATURE.get(
            component.role,
            "major_component",
        )

    @classmethod
    def resolve(
        cls,
        *,
        component: AtlasSemanticArchitectureComponent,
        level: AtlasLoDLevel,
    ) -> AtlasLoDComponentVisibilityDecision:
        cls._validate_component(
            component
        )
        cls._validate_level(
            level
        )

        required_feature = (
            cls.required_feature(
                component
            )
        )

        return AtlasLoDComponentVisibilityDecision(
            component=component,
            level=level,
            required_feature=required_feature,
            visible=level.supports(
                required_feature
            ),
        )

    @classmethod
    def visible_components(
        cls,
        *,
        model: AtlasSemanticArchitectureModel,
        level: AtlasLoDLevel,
    ) -> tuple[
        AtlasSemanticArchitectureComponent,
        ...,
    ]:
        if not isinstance(
            model,
            AtlasSemanticArchitectureModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasSemanticArchitectureModel"
            )

        cls._validate_level(
            level
        )

        return tuple(
            component
            for component in model.components
            if cls.resolve(
                component=component,
                level=level,
            ).visible
        )

    @staticmethod
    def _validate_component(
        component,
    ) -> None:
        if not isinstance(
            component,
            AtlasSemanticArchitectureComponent,
        ):
            raise TypeError(
                "component must be an "
                "AtlasSemanticArchitectureComponent"
            )

    @staticmethod
    def _validate_level(
        level,
    ) -> None:
        if not isinstance(
            level,
            AtlasLoDLevel,
        ):
            raise TypeError(
                "level must be an AtlasLoDLevel"
            )
