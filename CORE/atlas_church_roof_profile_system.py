from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasChurchRoofSection:
    section_type: str
    roof_shape: str
    orientation: str
    eave_z: float
    ridge_z: float
    longitudinal_ratio: float
    lateral_ratio: float
    polygon_sides: int = 0


@dataclass(frozen=True, slots=True)
class AtlasChurchRoofProfile:
    sections: tuple[AtlasChurchRoofSection, ...]

    def section(
        self,
        section_type,
    ) -> AtlasChurchRoofSection:
        for section in self.sections:
            if section.section_type == section_type:
                return section

        raise KeyError(
            f"Unknown church roof section: {section_type}"
        )


class AtlasChurchRoofProfileSystem:
    @classmethod
    def resolve(
        cls,
        *,
        longitudinal_span,
        lateral_span,
        wall_height,
    ) -> AtlasChurchRoofProfile:
        longitudinal_span = float(
            longitudinal_span
        )
        lateral_span = float(
            lateral_span
        )
        wall_height = float(
            wall_height
        )

        if longitudinal_span <= 0.0:
            raise ValueError(
                "longitudinal_span must be greater than zero"
            )

        if lateral_span <= 0.0:
            raise ValueError(
                "lateral_span must be greater than zero"
            )

        if wall_height <= 0.0:
            raise ValueError(
                "wall_height must be greater than zero"
            )

        aisle_eave_z = (
            wall_height * 0.72
        )
        aisle_ridge_z = (
            wall_height * 0.84
        )

        nave_eave_z = wall_height
        nave_ridge_z = (
            wall_height * 1.18
        )

        transept_eave_z = (
            wall_height * 0.94
        )
        transept_ridge_z = (
            wall_height * 1.13
        )

        apse_eave_z = (
            wall_height * 0.86
        )
        apse_ridge_z = (
            wall_height * 1.06
        )

        return AtlasChurchRoofProfile(
            sections=(
                AtlasChurchRoofSection(
                    section_type="outer_aisle_left",
                    roof_shape="gable",
                    orientation="longitudinal",
                    eave_z=aisle_eave_z,
                    ridge_z=aisle_ridge_z,
                    longitudinal_ratio=0.82,
                    lateral_ratio=0.18,
                ),
                AtlasChurchRoofSection(
                    section_type="outer_aisle_right",
                    roof_shape="gable",
                    orientation="longitudinal",
                    eave_z=aisle_eave_z,
                    ridge_z=aisle_ridge_z,
                    longitudinal_ratio=0.82,
                    lateral_ratio=0.18,
                ),
                AtlasChurchRoofSection(
                    section_type="main_nave",
                    roof_shape="gable",
                    orientation="longitudinal",
                    eave_z=nave_eave_z,
                    ridge_z=nave_ridge_z,
                    longitudinal_ratio=0.78,
                    lateral_ratio=0.46,
                ),
                AtlasChurchRoofSection(
                    section_type="transept",
                    roof_shape="gable",
                    orientation="lateral",
                    eave_z=transept_eave_z,
                    ridge_z=transept_ridge_z,
                    longitudinal_ratio=0.24,
                    lateral_ratio=0.88,
                ),
                AtlasChurchRoofSection(
                    section_type="apse",
                    roof_shape="polygon_pyramid",
                    orientation="radial",
                    eave_z=apse_eave_z,
                    ridge_z=apse_ridge_z,
                    longitudinal_ratio=0.16,
                    lateral_ratio=0.34,
                    polygon_sides=8,
                ),
            )
        )
