from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_surface_projection_engine import (
    AtlasSurfaceProjectionEngine,
)
from CORE.atlas_surface_target import (
    AtlasSurfaceTarget,
)


def _required_text(value, *, field_name):
    normalized = str(value).strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


def _normalized_tuple(
    values,
    *,
    field_name,
):
    normalized = tuple(
        _required_text(
            value,
            field_name=field_name,
        )
        for value in values
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be empty"
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasArchitecturalSemanticReliefProduct:
    product_id: str
    component_ids: tuple[str, ...]
    depth_bands: tuple[str, ...]
    baseline_mode: str
    target_surface_id: str | None = None
    projection_mode: str | None = None
    surface_target: AtlasSurfaceTarget | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "product_id",
            _required_text(
                self.product_id,
                field_name="product_id",
            ),
        )
        object.__setattr__(
            self,
            "component_ids",
            _normalized_tuple(
                self.component_ids,
                field_name="component_ids",
            ),
        )
        object.__setattr__(
            self,
            "depth_bands",
            _normalized_tuple(
                self.depth_bands,
                field_name="depth_bands",
            ),
        )
        object.__setattr__(
            self,
            "baseline_mode",
            _required_text(
                self.baseline_mode,
                field_name="baseline_mode",
            ),
        )

        if self.surface_target is not None:
            if not isinstance(
                self.surface_target,
                AtlasSurfaceTarget,
            ):
                raise TypeError(
                    "surface_target must be an "
                    "AtlasSurfaceTarget instance"
                )

            derived_surface_id = (
                self.surface_target.surface_id
            )
            derived_projection_mode = (
                self.surface_target.projection_mode
            )

            if (
                self.target_surface_id is not None
                and _required_text(
                    self.target_surface_id,
                    field_name="target_surface_id",
                )
                != derived_surface_id
            ):
                raise ValueError(
                    "target_surface_id must match "
                    "surface_target.surface_id"
                )

            if (
                self.projection_mode is not None
                and _required_text(
                    self.projection_mode,
                    field_name="projection_mode",
                )
                != derived_projection_mode
            ):
                raise ValueError(
                    "projection_mode must match "
                    "surface_target.projection_mode"
                )

            object.__setattr__(
                self,
                "target_surface_id",
                derived_surface_id,
            )
            object.__setattr__(
                self,
                "projection_mode",
                derived_projection_mode,
            )
        else:
            object.__setattr__(
                self,
                "target_surface_id",
                _required_text(
                    self.target_surface_id,
                    field_name="target_surface_id",
                ),
            )
            object.__setattr__(
                self,
                "projection_mode",
                _required_text(
                    self.projection_mode,
                    field_name="projection_mode",
                ),
            )

    def is_phase7_product_ready(
        self,
        *,
        comparison_report,
        operator_visual_accepted,
        physical_coupon_accepted=True,
    ):
        if not isinstance(
            comparison_report,
            dict,
        ):
            raise TypeError(
                "comparison_report must be a dictionary"
            )

        if (
            comparison_report.get("type")
            != "architectural_semantic_relief_comparison_report"
        ):
            raise ValueError(
                "comparison_report has unsupported type"
            )

        comparison_passed = (
            comparison_report.get("status") == "PASS"
            and comparison_report.get(
                "semantic_more_readable"
            )
            is True
        )

        return (
            comparison_passed
            and operator_visual_accepted is True
            and physical_coupon_accepted is True
        )

    def project_mesh(
        self,
        mesh,
    ):
        if self.surface_target is None:
            raise ValueError(
                "surface_target is required for projection"
            )

        result = AtlasSurfaceProjectionEngine.project(
            mesh=mesh,
            target=self.surface_target,
        )

        return {
            **result,
            "target_surface_id": (
                self.surface_target.surface_id
            ),
        }

    @property
    def has_recessed_opening(self):
        return any(
            component_id.startswith(
                "opening.recessed_"
            )
            for component_id
            in self.component_ids
        )

    @property
    def has_raised_ornament(self):
        raised_prefixes = (
            "arch.",
            "archivolt.",
            "cornice.",
            "frieze.",
            "molding.",
            "medallion.",
            "rosette.",
            "ornament.",
            "pilaster.",
            "column.",
            "column_base.",
            "column_capital.",
            "tympanum.",
            "tracery.",
        )

        return any(
            component_id.startswith(
                raised_prefixes
            )
            for component_id
            in self.component_ids
        )

    @property
    def has_figurative_or_emblematic_feature(
        self,
    ):
        prefixes = (
            "plaque.figurative_",
            "medallion.",
            "rosette.",
        )

        return any(
            component_id.startswith(
                prefixes
            )
            for component_id
            in self.component_ids
        )

    @property
    def has_inscription_or_panel(self):
        return any(
            component_id.startswith(
                "panel."
            )
            for component_id
            in self.component_ids
        )

    @property
    def has_minimum_depth_band_count(self):
        return len(
            set(self.depth_bands)
        ) >= 3

    @property
    def phase7_semantic_content_ready(self):
        return all(
            (
                self.has_recessed_opening,
                self.has_raised_ornament,
                self.has_figurative_or_emblematic_feature,
                self.has_inscription_or_panel,
                self.has_minimum_depth_band_count,
            )
        )
