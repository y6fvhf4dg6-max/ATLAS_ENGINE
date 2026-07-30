from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from CORE.atlas_relief_pipeline import AtlasReliefPipeline
from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)
from CORE.atlas_relief_product_profile_catalog import (
    ROCK_CARVED_LANDMARK,
)
from CORE.atlas_rock_relief_preprocessing_preset import (
    DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
)


@dataclass(frozen=True)
class AtlasRockReliefProductionPreset:
    name: str
    product_profile: AtlasReliefProductProfile
    preprocessors: tuple[Any, ...]

    def build_from_image(
        self,
        image_path,
        **kwargs,
    ):
        return AtlasReliefPipeline.build_from_image(
            image_path,
            product_profile=self.product_profile,
            preprocessors=self.preprocessors,
            **kwargs,
        )

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise ValueError(
                "name must be a string."
            )

        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "name must not be blank."
            )

        if not isinstance(
            self.product_profile,
            AtlasReliefProductProfile,
        ):
            raise ValueError(
                "product_profile must be an "
                "AtlasReliefProductProfile."
            )

        try:
            preprocessors = tuple(
                self.preprocessors
            )
        except TypeError as exc:
            raise ValueError(
                "preprocessors must be iterable."
            ) from exc

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "preprocessors",
            preprocessors,
        )


DALYAN_ROCK_TOMBS_PRODUCTION_PRESET = (
    AtlasRockReliefProductionPreset(
        name="dalyan-rock-tombs",
        product_profile=ROCK_CARVED_LANDMARK,
        preprocessors=(
            DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
        ),
    )
)
