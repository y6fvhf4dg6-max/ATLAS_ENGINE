from dataclasses import dataclass

from CORE.atlas_geometry import AtlasGeometry


@dataclass(frozen=True, slots=True)
class AtlasLandmarkMeshBuilding:
    geometry: tuple
    estimated_height: float
    area_m2: float
    is_building_part: bool = False


class AtlasLandmarkMeshAdapter:
    @staticmethod
    def from_geometry(geometry):
        footprint = tuple(geometry.footprint)

        return AtlasLandmarkMeshBuilding(
            geometry=footprint,
            estimated_height=float(geometry.height_mm),
            area_m2=float(
                AtlasGeometry.polygon_area_m2(footprint)
            ),
            is_building_part=False,
        )
