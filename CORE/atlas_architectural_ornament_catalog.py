from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType


def _identifier(value, *, field_name):
    normalized = "_".join(
        str(value).strip().lower().split()
    )
    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )
    return normalized


def _non_empty_tuple(values, *, field_name):
    try:
        normalized = tuple(
            _identifier(
                value,
                field_name=field_name,
            )
            for value in values
        )
    except TypeError as exc:
        raise ValueError(
            f"{field_name} must be iterable"
        ) from exc

    if not normalized:
        raise ValueError(
            f"{field_name} must not be empty"
        )

    return normalized


SUPPORTED_PROJECTION_MODES = frozenset(
    {
        "flat_plane",
        "oriented_planar",
        "bilinear_surface",
        "cylindrical_surface",
        "dome_surface",
        "vault_surface",
        "indexed_mesh_surface",
    }
)


SUPPORTED_OUTPUT_ELIGIBILITY = frozenset(
    {
        "assembled",
        "relief",
        "kit",
    }
)


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalOrnamentInstance:
    component_id: str
    version: str
    parameters: object
    geometry_producer: str
    occurrence_id: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "parameters",
            MappingProxyType(
                dict(self.parameters)
            ),
        )

        if self.occurrence_id is not None:
            object.__setattr__(
                self,
                "occurrence_id",
                _identifier(
                    self.occurrence_id,
                    field_name="occurrence_id",
                ),
            )


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalOrnamentCatalogEntry:
    component_id: str
    version: str
    semantic_class: str
    style_tags: tuple[str, ...]
    parameter_names: tuple[str, ...]
    anchor_names: tuple[str, ...]
    supported_projection_modes: tuple[str, ...]
    minimum_printable_profile: object
    material_role: str
    repetition_mode: str
    symmetry: str
    output_eligibility: tuple[str, ...]
    license_id: str
    provenance: object
    geometry_producer: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "component_id",
            _identifier(
                self.component_id,
                field_name="component_id",
            ),
        )
        object.__setattr__(
            self,
            "version",
            str(self.version).strip(),
        )
        if not self.version:
            raise ValueError(
                "version must not be blank"
            )

        for field_name in (
            "semantic_class",
            "material_role",
            "repetition_mode",
            "symmetry",
            "license_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _identifier(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

        geometry_producer = str(
            self.geometry_producer
        ).strip()
        if not geometry_producer:
            raise ValueError(
                "geometry_producer must not be blank"
            )
        object.__setattr__(
            self,
            "geometry_producer",
            geometry_producer,
        )

        for field_name in (
            "style_tags",
            "parameter_names",
            "anchor_names",
            "supported_projection_modes",
            "output_eligibility",
        ):
            normalized_values = _non_empty_tuple(
                getattr(self, field_name),
                field_name=field_name,
            )

            if (
                field_name in {
                    "parameter_names",
                    "anchor_names",
                }
                and len(normalized_values)
                != len(set(normalized_values))
            ):
                raise ValueError(
                    f"{field_name} values must be unique"
                )

            if field_name == "supported_projection_modes":
                unsupported_modes = tuple(
                    mode
                    for mode in normalized_values
                    if mode not in SUPPORTED_PROJECTION_MODES
                )
                if unsupported_modes:
                    raise ValueError(
                        "supported_projection_modes contains "
                        f"unsupported values: {unsupported_modes}"
                    )

            if field_name == "output_eligibility":
                unsupported_outputs = tuple(
                    output
                    for output in normalized_values
                    if output not in SUPPORTED_OUTPUT_ELIGIBILITY
                )
                if unsupported_outputs:
                    raise ValueError(
                        "output_eligibility contains "
                        f"unsupported values: {unsupported_outputs}"
                    )

            object.__setattr__(
                self,
                field_name,
                normalized_values,
            )

        try:
            printable_profile = dict(
                self.minimum_printable_profile
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "minimum_printable_profile must be mapping-like"
            ) from exc

        if not printable_profile:
            raise ValueError(
                "minimum_printable_profile must not be empty"
            )

        normalized_printable_profile = {}

        for key, value in printable_profile.items():
            normalized_key = _identifier(
                key,
                field_name="minimum_printable_profile key",
            )

            try:
                numeric_value = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "minimum_printable_profile values "
                    "must be numeric and positive"
                ) from exc

            if (
                not math.isfinite(numeric_value)
                or numeric_value <= 0.0
            ):
                raise ValueError(
                    "minimum_printable_profile values "
                    "must be finite and positive"
                )

            normalized_printable_profile[
                normalized_key
            ] = numeric_value

        object.__setattr__(
            self,
            "minimum_printable_profile",
            MappingProxyType(
                normalized_printable_profile
            ),
        )

        try:
            provenance = dict(
                self.provenance
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "provenance must be mapping-like"
            ) from exc

        if not provenance:
            raise ValueError(
                "provenance must not be empty"
            )

        object.__setattr__(
            self,
            "provenance",
            MappingProxyType(
                provenance
            ),
        )

    def bind(
        self,
        *,
        parameters,
        occurrence_id=None,
    ):
        try:
            parameters = dict(
                parameters
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "parameters must be mapping-like"
            ) from exc

        expected = set(
            self.parameter_names
        )
        actual = set(
            parameters
        )

        if actual != expected:
            missing = tuple(
                sorted(
                    expected - actual
                )
            )
            unexpected = tuple(
                sorted(
                    actual - expected
                )
            )
            raise ValueError(
                "parameters must match catalog contract; "
                f"missing={missing}, unexpected={unexpected}"
            )

        normalized_parameters = {}

        for name in self.parameter_names:
            value = parameters[name]

            if name == "arch_segments":
                if (
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < 3
                ):
                    raise ValueError(
                        "arch_segments must be an integer "
                        "greater than or equal to 3"
                    )
                normalized_parameters[name] = value
                continue

            if name.endswith("_mm"):
                try:
                    numeric_value = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"{name} must be numeric and finite"
                    ) from exc

                if not math.isfinite(numeric_value):
                    raise ValueError(
                        f"{name} must be numeric and finite"
                    )

                if name == "embed_mm":
                    if numeric_value < 0.0:
                        raise ValueError(
                            "embed_mm must be non-negative"
                        )
                elif numeric_value <= 0.0:
                    raise ValueError(
                        f"{name} must be positive"
                    )

                normalized_parameters[name] = numeric_value
                continue

            normalized_parameters[name] = value

        for profile_name, minimum_value in (
            self.minimum_printable_profile.items()
        ):
            if not profile_name.startswith("minimum_"):
                continue

            parameter_name = profile_name[len("minimum_"):]

            if parameter_name not in normalized_parameters:
                continue

            parameter_value = normalized_parameters[
                parameter_name
            ]

            if (
                isinstance(parameter_value, bool)
                or not isinstance(
                    parameter_value,
                    (int, float),
                )
            ):
                continue

            if float(parameter_value) < float(minimum_value):
                raise ValueError(
                    f"{parameter_name} violates minimum printable profile "
                    f"({parameter_value} < {minimum_value})"
                )

        return AtlasArchitecturalOrnamentInstance(
            component_id=self.component_id,
            version=self.version,
            parameters=normalized_parameters,
            geometry_producer=self.geometry_producer,
            occurrence_id=occurrence_id,
        )


class AtlasArchitecturalOrnamentCatalog:
    def __init__(
        self,
        *,
        entries,
    ):
        try:
            entries = tuple(entries)
        except TypeError as exc:
            raise ValueError(
                "entries must be iterable"
            ) from exc

        registry = {}

        for entry in entries:
            if not isinstance(
                entry,
                AtlasArchitecturalOrnamentCatalogEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "AtlasArchitecturalOrnamentCatalogEntry instances"
                )

            key = (
                entry.component_id,
                entry.version,
            )

            if key in registry:
                raise ValueError(
                    "duplicate architectural ornament catalog entry"
                )

            registry[key] = entry

        self._registry = registry
        self._entries = entries

    @property
    def component_ids(self):
        return tuple(
            sorted(
                {
                    entry.component_id
                    for entry in self._entries
                }
            )
        )

    def get(
        self,
        *,
        component_id,
        version,
    ):
        normalized_component_id = _identifier(
            component_id,
            field_name="component_id",
        )
        normalized_version = str(
            version
        ).strip()

        if not normalized_version:
            raise ValueError(
                "version must not be blank"
            )

        key = (
            normalized_component_id,
            normalized_version,
        )

        try:
            return self._registry[key]
        except KeyError as exc:
            raise KeyError(
                "architectural ornament catalog entry not found: "
                f"{normalized_component_id}@{normalized_version}"
            ) from exc


def build_default_architectural_ornament_catalog():
    round_arch_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="arch.round_v1",
        version="1.0.0",
        semantic_class="arch",
        style_tags=(
            "round_arch",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
            "arch_segments",
        ),
        anchor_names=(
            "center",
            "spring_left",
            "spring_right",
            "apex",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_arch_mesher",
        },
        geometry_producer="AtlasFacadeArchMesher",
    )

    cornice_band_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="cornice.band_v1",
        version="1.0.0",
        semantic_class="cornice",
        style_tags=(
            "band",
            "generic",
        ),
        parameter_names=(
            "band_height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "start",
            "center",
            "end",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_band_height_mm": 0.40,
            "minimum_depth_mm": 0.24,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="linear",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_cornice_mesher",
        },
        geometry_producer="AtlasFacadeCorniceMesher",
    )

    recessed_rect_opening_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="opening.recessed_rect_v1",
        version="1.0.0",
        semantic_class="recessed_opening",
        style_tags=(
            "rectangular",
            "recessed",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "bottom_left",
            "bottom_right",
            "top_right",
            "top_left",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.8,
            "minimum_height_mm": 0.8,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_opening",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_opening_mesher",
        },
        geometry_producer="AtlasFacadeOpeningMesher",
    )

    circular_medallion_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="medallion.circular_v1",
        version="1.0.0",
        semantic_class="medallion",
        style_tags=(
            "circular",
            "generic",
        ),
        parameter_names=(
            "diameter_mm",
            "depth_mm",
            "embed_mm",
            "segments",
        ),
        anchor_names=(
            "center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_diameter_mm": 1.2,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="radial",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_circular_panel_builder",
        },
        geometry_producer="AtlasFacadeCircularPanelBuilder",
    )

    inscription_panel_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="panel.inscription_rect_v1",
        version="1.0.0",
        semantic_class="inscription_panel",
        style_tags=(
            "rectangular",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "bottom_left",
            "bottom_right",
            "top_right",
            "top_left",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 0.8,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_panel_builder",
        },
        geometry_producer="AtlasFacadePanelBuilder",
    )

    rectangular_portal_surround_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="portal.surround_rect_v1",
        version="1.0.0",
        semantic_class="portal_surround",
        style_tags=(
            "rectangular",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "surround_width_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "threshold_center",
            "lintel_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 1.2,
            "minimum_surround_width_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_portal_surround_mesher",
        },
        geometry_producer="AtlasFacadePortalSurroundMesher",
    )

    rectangular_pilaster_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="pilaster.rect_v1",
        version="1.0.0",
        semantic_class="pilaster",
        style_tags=(
            "rectangular",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "base_center",
            "top_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.8,
            "minimum_height_mm": 1.2,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_pilaster_mesher",
        },
        geometry_producer="AtlasFacadePilasterMesher",
    )

    classical_round_column_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="column.classical_round_v1",
        version="1.0.0",
        semantic_class="column",
        style_tags=(
            "classical",
            "round",
            "generic",
        ),
        parameter_names=(
            "diameter_mm",
            "height_mm",
            "segments",
        ),
        anchor_names=(
            "center",
            "base_center",
            "top_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
        ),
        minimum_printable_profile={
            "minimum_diameter_mm": 1.2,
            "minimum_height_mm": 1.2,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="radial",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "classical_colonnade",
        },
        geometry_producer="AtlasClassicalColonnadeBuilder",
    )

    classical_round_column_base_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="column_base.classical_round_v1",
        version="1.0.0",
        semantic_class="column_base",
        style_tags=(
            "classical",
            "round",
            "generic",
        ),
        parameter_names=(
            "diameter_mm",
            "height_mm",
            "segments",
        ),
        anchor_names=(
            "center",
            "bottom_center",
            "top_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
        ),
        minimum_printable_profile={
            "minimum_diameter_mm": 1.0,
            "minimum_height_mm": 0.3,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="radial",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "classical_column_detail_mesher",
        },
        geometry_producer="AtlasClassicalColumnDetailMesher",
    )

    classical_round_column_capital_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="column_capital.classical_round_v1",
        version="1.0.0",
        semantic_class="column_capital",
        style_tags=(
            "classical",
            "round",
            "generic",
        ),
        parameter_names=(
            "diameter_mm",
            "height_mm",
            "segments",
        ),
        anchor_names=(
            "center",
            "bottom_center",
            "top_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
        ),
        minimum_printable_profile={
            "minimum_diameter_mm": 1.0,
            "minimum_height_mm": 0.3,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="radial",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "classical_column_detail_mesher",
        },
        geometry_producer="AtlasClassicalColumnDetailMesher",
    )

    generic_frieze_band_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="frieze.band_v1",
        version="1.0.0",
        semantic_class="frieze",
        style_tags=(
            "band",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "start",
            "end",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="linear",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_panel_builder",
        },
        geometry_producer="AtlasFacadePanelBuilder",
    )

    circular_rosette_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="rosette.circular_v1",
        version="1.0.0",
        semantic_class="rosette",
        style_tags=(
            "circular",
            "radial",
            "generic",
        ),
        parameter_names=(
            "diameter_mm",
            "depth_mm",
            "embed_mm",
            "segments",
        ),
        anchor_names=(
            "center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_diameter_mm": 1.2,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="radial",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_circular_panel_builder",
        },
        geometry_producer="AtlasFacadeCircularPanelBuilder",
    )

    geometric_polygon_ornament_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="ornament.geometric_polygon_v1",
        version="1.0.0",
        semantic_class="geometric_ornament",
        style_tags=(
            "geometric",
            "polygon",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
        ),
        anchor_names=(
            "center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.0,
            "minimum_height_mm": 1.0,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="custom",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "geometric_ornament_mesher",
        },
        geometry_producer="AtlasGeometricOrnamentMesher",
    )

    floral_radial_ornament_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="ornament.floral_radial_v1",
        version="1.0.0",
        semantic_class="floral_ornament",
        style_tags=(
            "floral",
            "radial",
            "generic",
        ),
        parameter_names=(
            "outer_diameter_mm",
            "inner_ratio",
            "petal_count",
            "depth_mm",
        ),
        anchor_names=(
            "center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_outer_diameter_mm": 1.2,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="radial",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "floral_ornament_mesher",
        },
        geometry_producer="AtlasFloralOrnamentMesher",
    )

    recessed_arch_niche_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="niche.recessed_arch_v1",
        version="1.0.0",
        semantic_class="statue_niche",
        style_tags=(
            "recessed",
            "arched",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "spring_height_mm",
            "recess_depth_mm",
            "arch_segments",
        ),
        anchor_names=(
            "center",
            "bottom_center",
            "spring_center",
            "top_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 1.6,
            "minimum_spring_height_mm": 0.8,
            "minimum_recess_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "recessed_arch_niche_mesher",
        },
        geometry_producer="AtlasRecessedArchNicheMesher",
    )

    round_archivolt_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="archivolt.round_v1",
        version="1.0.0",
        semantic_class="archivolt",
        style_tags=(
            "round",
            "arched",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
            "arch_segments",
            "arch_height_ratio",
        ),
        anchor_names=(
            "center",
            "spring_left",
            "spring_right",
            "apex",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.8,
            "minimum_height_mm": 0.8,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_arch_mesher",
        },
        geometry_producer="AtlasFacadeArchMesher",
    )

    mullion_transom_tracery_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="tracery.mullion_transom_v1",
        version="1.0.0",
        semantic_class="tracery",
        style_tags=(
            "mullion",
            "transom",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "mullion_width_mm",
            "transom_height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "bottom_center",
            "top_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 1.2,
            "minimum_mullion_width_mm": 1.2,
            "minimum_transom_height_mm": 1.2,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_tracery_mesher",
        },
        geometry_producer="AtlasFacadeTraceryMesher",
    )

    triangular_tympanum_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="tympanum.triangular_v1",
        version="1.0.0",
        semantic_class="tympanum",
        style_tags=(
            "triangular",
            "pediment",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
        ),
        anchor_names=(
            "center",
            "base_left",
            "base_right",
            "apex",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "tympanum_mesher",
        },
        geometry_producer="AtlasTympanumMesher",
    )

    rectangular_molding_band_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="molding.rectangular_band_v1",
        version="1.0.0",
        semantic_class="molding",
        style_tags=(
            "rectangular",
            "band",
            "linear",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "start",
            "end",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_molding_mesher",
        },
        geometry_producer="AtlasFacadeMoldingMesher",
    )

    figurative_rect_plaque_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="plaque.figurative_rect_v1",
        version="1.0.0",
        semantic_class="figurative_plaque",
        style_tags=(
            "figurative",
            "rectangular",
            "relief_carrier",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
        ),
        anchor_names=(
            "center",
            "bottom_center",
            "top_center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.2,
            "minimum_height_mm": 1.2,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "figurative_plaque_mesher",
        },
        geometry_producer="AtlasFigurativePlaqueMesher",
    )

    brick_surface_unit_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="surface_unit.brick_v1",
        version="1.0.0",
        semantic_class="repeatable_surface_unit",
        style_tags=(
            "brick",
            "masonry",
            "repeatable",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
        ),
        anchor_names=(
            "center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.8,
            "minimum_height_mm": 0.5,
            "minimum_depth_mm": 0.18,
        },
        material_role="surface_unit",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "repeatable_surface_unit_mesher",
            "unit_kind": "brick",
        },
        geometry_producer="AtlasRepeatableSurfaceUnitMesher",
    )

    stone_block_surface_unit_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="surface_unit.stone_block_v1",
        version="1.0.0",
        semantic_class="repeatable_surface_unit",
        style_tags=(
            "stone_block",
            "masonry",
            "repeatable",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
        ),
        anchor_names=(
            "center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 1.0,
            "minimum_height_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="surface_unit",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "repeatable_surface_unit_mesher",
            "unit_kind": "stone_block",
        },
        geometry_producer="AtlasRepeatableSurfaceUnitMesher",
    )

    roof_tile_surface_unit_v1 = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="surface_unit.roof_tile_v1",
        version="1.0.0",
        semantic_class="repeatable_surface_unit",
        style_tags=(
            "roof_tile",
            "roofing",
            "repeatable",
            "generic",
        ),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
        ),
        anchor_names=(
            "center",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.8,
            "minimum_height_mm": 0.8,
            "minimum_depth_mm": 0.18,
        },
        material_role="surface_unit",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "repeatable_surface_unit_mesher",
            "unit_kind": "roof_tile",
        },
        geometry_producer="AtlasRepeatableSurfaceUnitMesher",
    )

    return AtlasArchitecturalOrnamentCatalog(
        entries=(
            round_arch_v1,
            cornice_band_v1,
            recessed_rect_opening_v1,
            circular_medallion_v1,
            inscription_panel_v1,
            rectangular_portal_surround_v1,
            rectangular_pilaster_v1,
            classical_round_column_v1,
            classical_round_column_base_v1,
            classical_round_column_capital_v1,
            generic_frieze_band_v1,
            circular_rosette_v1,
            geometric_polygon_ornament_v1,
            floral_radial_ornament_v1,
            recessed_arch_niche_v1,
            round_archivolt_v1,
            mullion_transom_tracery_v1,
            triangular_tympanum_v1,
            rectangular_molding_band_v1,
            figurative_rect_plaque_v1,
            brick_surface_unit_v1,
            stone_block_surface_unit_v1,
            roof_tile_surface_unit_v1,
        ),
    )
