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

        canonical_dimensions = (
            AtlasTreeFoundationBuilder
            ._canonical_tree_dimensions()
        )

        tree_symbol_max_diameter_mm = (
            canonical_dimensions[
                "crown_diameter_mm"
            ]
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

        canonical_dimensions = (
            AtlasTreeFoundationBuilder
            ._canonical_tree_dimensions()
        )

        canonical_minimum_spacing_mm = (
            canonical_dimensions[
                "crown_diameter_mm"
            ]
            + float(nozzle_diameter_mm)
        )

        if decision.action == "omit":
            resolved_spacing_mm = 0.0
            resolved_action = "omit"
        else:
            resolved_spacing_mm = max(
                decision.resolved_size_mm,
                canonical_minimum_spacing_mm,
            )

            if (
                resolved_spacing_mm
                > decision.resolved_size_mm
            ):
                resolved_action = "enlarge"
            else:
                resolved_action = decision.action

        return {
            "action": resolved_action,
            "source_spacing_m": float(source_spacing_m),
            "scaled_spacing_mm": decision.scaled_size_mm,
            "minimum_printable_mm": (
                decision.minimum_printable_mm
            ),
            "resolved_spacing_mm": (
                resolved_spacing_mm
            ),
            "canonical_minimum_spacing_mm": (
                canonical_minimum_spacing_mm
            ),
            "scale_factor": decision.scale_factor,
        }
