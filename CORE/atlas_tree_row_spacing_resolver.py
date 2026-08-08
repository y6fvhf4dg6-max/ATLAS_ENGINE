from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailResolver,
)
from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


class AtlasTreeRowSpacingResolver:
    @staticmethod
    def resolve_fallback(
        *,
        nozzle_diameter_mm,
    ):
        nozzle_diameter_mm = float(nozzle_diameter_mm)

        if nozzle_diameter_mm <= 0.0:
            raise ValueError(
                "nozzle_diameter_mm must be positive"
            )

        tree_symbol_max_diameter_mm = (
            AtlasTreeFoundationBuilder
            .PARK_TREE_SYMBOL_MAX_DIAMETER_MM
        )

        return {
            "action": "fallback",
            "evidence_source": "product_readability",
            "resolved_spacing_mm": (
                tree_symbol_max_diameter_mm
                + nozzle_diameter_mm
            ),
            "tree_symbol_max_diameter_mm": (
                tree_symbol_max_diameter_mm
            ),
            "clearance_mm": nozzle_diameter_mm,
        }

    @staticmethod
    def resolve(
        *,
        source_spacing_m,
        scale_ratio,
        nozzle_diameter_mm,
    ):
        decision = AtlasPhysicalDetailResolver.resolve(
            real_size_m=source_spacing_m,
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
            detail_type="tree_row_spacing",
        )

        return {
            "action": decision.action,
            "source_spacing_m": float(source_spacing_m),
            "scaled_spacing_mm": decision.scaled_size_mm,
            "minimum_printable_mm": (
                decision.minimum_printable_mm
            ),
            "resolved_spacing_mm": (
                decision.resolved_size_mm
            ),
            "scale_factor": decision.scale_factor,
        }
