from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_architectural_relief_depth_composer import (
    AtlasArchitecturalReliefDepthProfile,
)
from CORE.atlas_architectural_relief_detail_scale_filter import (
    AtlasArchitecturalReliefDetailScaleProfile,
)
from CORE.atlas_architectural_relief_physical_profile import (
    AtlasArchitecturalReliefPhysicalProfile,
)
from CORE.atlas_architectural_relief_structure_preserver import (
    AtlasArchitecturalReliefStructureProfile,
)
from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)
from CORE.atlas_relief_product_profile_catalog import (
    ROCK_CARVED_LANDMARK,
)
from CORE.atlas_relief_risk_profile import (
    AtlasReliefRiskProfile,
)


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefV1Standard:
    name: str
    version: str
    product_profile: AtlasReliefProductProfile
    depth_profile: AtlasArchitecturalReliefDepthProfile
    structure_profile: AtlasArchitecturalReliefStructureProfile
    detail_scale_profile: AtlasArchitecturalReliefDetailScaleProfile
    physical_profile: AtlasArchitecturalReliefPhysicalProfile
    risk_profile: AtlasReliefRiskProfile

    def __post_init__(self) -> None:
        name = self._normalized_text(
            self.name,
            field_name="name",
        )
        version = self._normalized_text(
            self.version,
            field_name="version",
        )

        expected_types = (
            (
                "product_profile",
                self.product_profile,
                AtlasReliefProductProfile,
            ),
            (
                "depth_profile",
                self.depth_profile,
                AtlasArchitecturalReliefDepthProfile,
            ),
            (
                "structure_profile",
                self.structure_profile,
                AtlasArchitecturalReliefStructureProfile,
            ),
            (
                "detail_scale_profile",
                self.detail_scale_profile,
                AtlasArchitecturalReliefDetailScaleProfile,
            ),
            (
                "physical_profile",
                self.physical_profile,
                AtlasArchitecturalReliefPhysicalProfile,
            ),
            (
                "risk_profile",
                self.risk_profile,
                AtlasReliefRiskProfile,
            ),
        )

        for field_name, value, expected_type in expected_types:
            if not isinstance(
                value,
                expected_type,
            ):
                raise TypeError(
                    f"{field_name} must be an instance of "
                    f"{expected_type.__name__}."
                )

        object.__setattr__(
            self,
            "name",
            name,
        )
        object.__setattr__(
            self,
            "version",
            version,
        )

    @staticmethod
    def _normalized_text(
        value,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized


ARCHITECTURAL_RELIEF_V1 = (
    AtlasArchitecturalReliefV1Standard(
        name="architectural-relief-v1",
        version="1.0",
        product_profile=ROCK_CARVED_LANDMARK,
        depth_profile=(
            AtlasArchitecturalReliefDepthProfile(
                form_weight=(
                    ROCK_CARVED_LANDMARK
                    .form_weight
                ),
                detail_weight=(
                    ROCK_CARVED_LANDMARK
                    .detail_weight
                ),
                micro_detail_weight=(
                    ROCK_CARVED_LANDMARK
                    .micro_detail_weight
                ),
                micro_detail_limit=(
                    ROCK_CARVED_LANDMARK
                    .micro_detail_limit
                ),
            )
        ),
        structure_profile=(
            AtlasArchitecturalReliefStructureProfile(
                strength=1.0,
                max_correction=0.05,
            )
        ),
        detail_scale_profile=(
            AtlasArchitecturalReliefDetailScaleProfile(
                minimum_feature_mm=0.8,
                activity_threshold=0.02,
                minimum_density=0.25,
            )
        ),
        physical_profile=(
            AtlasArchitecturalReliefPhysicalProfile(
                name="architectural-relief-v1",
                base_thickness_mm=0.8,
                relief_height_mm=(
                    ROCK_CARVED_LANDMARK
                    .relief_height_mm
                ),
                target_sample_spacing_mm=0.25,
            )
        ),
        risk_profile=(
            AtlasReliefRiskProfile(
                name="architectural-relief-v1",
                warning_slope_degrees=55.0,
                critical_slope_degrees=75.0,
                warning_slope_area_percent=0.0,
                critical_slope_area_percent=0.0,
            )
        ),
    )
)
