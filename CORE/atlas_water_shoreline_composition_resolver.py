from collections.abc import Mapping
from dataclasses import dataclass

from shapely.geometry import LineString, Polygon

from CORE.atlas_physical_cartographic_exaggeration_resolver import (
    AtlasPhysicalCartographicExaggerationResolver,
)


@dataclass(frozen=True, slots=True)
class AtlasWaterShorelineCompositionProfile:
    semantic_class: str
    composition_role: str
    first_class_scene_layer: bool
    lod_eligible: bool
    preserves_source_geometry: bool
    physical_separation_role: str
    product_scale_simplification: str
    shoreline_treatment: str


class AtlasWaterShorelineCompositionResolver:
    @staticmethod
    def resolve_cartographic_exaggeration(
        *,
        semantic_class,
        source_width_m,
        scale_ratio,
        product_size_mm,
        nozzle_diameter_mm,
        minimum_printable_width_mm,
        semantic_priority,
        lod_level,
    ):
        if semantic_class not in {
            "narrow_waterway",
            "shoreline_edge",
        }:
            raise ValueError(
                "water/shoreline cartographic exaggeration "
                "supports only narrow_waterway and "
                "shoreline_edge"
            )

        return (
            AtlasPhysicalCartographicExaggerationResolver
            .resolve(
                semantic_class=semantic_class,
                source_width_m=source_width_m,
                scale_ratio=scale_ratio,
                product_size_mm=product_size_mm,
                nozzle_diameter_mm=nozzle_diameter_mm,
                minimum_printable_width_mm=(
                    minimum_printable_width_mm
                ),
                semantic_priority=semantic_priority,
                lod_level=lod_level,
            )
        )

    @staticmethod
    def _source_shape(source):
        if not isinstance(source, Mapping):
            return None

        geometry = source.get(
            "geometry",
            (),
        )

        if not geometry or len(geometry) < 2:
            return None

        points = tuple(
            (
                float(point[0]),
                float(point[1]),
            )
            for point in geometry
        )

        if len(points) >= 3:
            polygon = Polygon(points)

            if (
                polygon.is_valid
                and not polygon.is_empty
                and polygon.area > 0.0
            ):
                return polygon

        line = LineString(points)

        if line.is_empty or line.length <= 0.0:
            return None

        return line

    @classmethod
    def resolve_interaction_flags(
        cls,
        *,
        source,
        bridges=(),
        roads=(),
        railways=(),
    ):
        source_shape = cls._source_shape(
            source
        )

        if source_shape is None:
            return {
                "bridge_interaction": False,
                "road_interaction": False,
                "rail_interaction": False,
            }

        def intersects_any(records):
            for record in records or ():
                candidate_shape = (
                    cls._source_shape(
                        record
                    )
                )

                if candidate_shape is None:
                    continue

                if source_shape.intersects(
                    candidate_shape
                ):
                    return True

            return False

        return {
            "bridge_interaction": intersects_any(
                bridges
            ),
            "road_interaction": intersects_any(
                roads
            ),
            "rail_interaction": intersects_any(
                railways
            ),
        }

    @classmethod
    def resolve_scene_records(
        cls,
        *,
        waters=(),
        coastlines=(),
        waterfront_structures=(),
        embankments=(),
        bridges=(),
        roads=(),
        railways=(),
    ):
        records = []

        for source in waters or ():
            flags = cls.resolve_interaction_flags(
                source=source,
                bridges=bridges,
                roads=roads,
                railways=railways,
            )

            record = cls.resolve_source_record(
                source,
                **flags,
            )

            if record is not None:
                records.append(record)

        for source in coastlines or ():
            flags = cls.resolve_interaction_flags(
                source=source,
                bridges=bridges,
                roads=roads,
                railways=railways,
            )

            record = cls.resolve_source_record(
                source,
                geometry_role="coastline",
                **flags,
            )

            if record is not None:
                records.append(record)

        for source in waterfront_structures or ():
            flags = cls.resolve_interaction_flags(
                source=source,
                bridges=bridges,
                roads=roads,
                railways=railways,
            )

            record = cls.resolve_source_record(
                source,
                **flags,
            )

            if record is not None:
                records.append(record)

        for source in embankments or ():
            flags = cls.resolve_interaction_flags(
                source=source,
                bridges=bridges,
                roads=roads,
                railways=railways,
            )

            record = cls.resolve_source_record(
                source,
                **flags,
            )

            if record is not None:
                records.append(record)

        return tuple(records)

    @classmethod
    def resolve_source_record(
        cls,
        source,
        *,
        geometry_role=None,
        bridge_interaction=False,
        road_interaction=False,
        rail_interaction=False,
    ):
        if not isinstance(source, Mapping):
            raise TypeError(
                "source must be a mapping"
            )

        tags = source.get(
            "tags",
            {},
        )

        if not isinstance(tags, Mapping):
            raise TypeError(
                "tags must be a mapping"
            )

        profile = cls.resolve_profile(
            tags=tags,
            geometry_role=geometry_role,
        )

        if profile is None:
            return None

        return {
            "source_id": source.get("id"),
            "semantic_class": profile.semantic_class,
            "composition_role": profile.composition_role,
            "geometry": source.get("geometry"),
            "first_class_scene_layer": (
                profile.first_class_scene_layer
            ),
            "lod_eligible": profile.lod_eligible,
            "preserves_source_geometry": (
                profile.preserves_source_geometry
            ),
            "physical_separation_role": (
                profile.physical_separation_role
            ),
            "product_scale_simplification": (
                profile.product_scale_simplification
            ),
            "shoreline_treatment": (
                profile.shoreline_treatment
            ),
            "supports_water_surface_continuity": (
                profile.composition_role
                == "water_surface"
            ),
            "supports_shoreline_readability": True,
            "bridge_interaction": bool(
                bridge_interaction
            ),
            "road_interaction": bool(
                road_interaction
            ),
            "rail_interaction": bool(
                rail_interaction
            ),
        }

    @classmethod
    def resolve_profile(
        cls,
        *,
        tags,
        geometry_role=None,
    ):
        semantic_class = cls.resolve_semantic_class(
            tags=tags,
            geometry_role=geometry_role,
        )

        if semantic_class is None:
            return None

        water_surface_classes = {
            "river",
            "canal",
            "lake",
            "coastline",
        }

        shoreline_structure_classes = {
            "embankment",
            "quay",
            "waterfront_pier",
            "marina",
        }

        if semantic_class in water_surface_classes:
            composition_role = "water_surface"
            physical_separation_role = "raised_water_solid"
            shoreline_treatment = "readable_boundary"
        elif semantic_class in shoreline_structure_classes:
            composition_role = "shoreline_structure"
            physical_separation_role = "shoreline_structure"
            shoreline_treatment = "structural_edge"
        elif semantic_class == "island":
            composition_role = "land_within_water"
            physical_separation_role = "terrain_landform"
            shoreline_treatment = "source_boundary"
        else:
            return None

        return AtlasWaterShorelineCompositionProfile(
            semantic_class=semantic_class,
            composition_role=composition_role,
            first_class_scene_layer=True,
            lod_eligible=True,
            preserves_source_geometry=True,
            physical_separation_role=(
                physical_separation_role
            ),
            product_scale_simplification=(
                "source_preserving"
            ),
            shoreline_treatment=shoreline_treatment,
        )

    @staticmethod
    def resolve_semantic_class(
        *,
        tags,
        geometry_role=None,
    ):
        tags = tags or {}

        if geometry_role == "coastline":
            return "coastline"

        if tags.get("natural") == "coastline":
            return "coastline"

        waterway = str(
            tags.get("waterway", "")
        ).strip().lower()

        if waterway == "river":
            return "river"

        if waterway == "canal":
            return "canal"

        water = str(
            tags.get("water", "")
        ).strip().lower()

        if water == "lake":
            return "lake"

        if (
            tags.get("natural") == "water"
            and not water
        ):
            return "lake"

        man_made = str(
            tags.get("man_made", "")
        ).strip().lower()

        if man_made == "embankment":
            return "embankment"

        if man_made == "quay":
            return "quay"

        if man_made == "pier":
            return "waterfront_pier"

        if (
            str(
                tags.get("leisure", "")
            ).strip().lower()
            == "marina"
        ):
            return "marina"

        if (
            str(
                tags.get("place", "")
            ).strip().lower()
            == "island"
        ):
            return "island"

        return None
