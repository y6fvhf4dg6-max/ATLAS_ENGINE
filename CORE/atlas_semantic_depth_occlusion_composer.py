from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from CORE.atlas_semantic_relief_scene import (
    AtlasSemanticReliefScene,
)


class AtlasSemanticDepthOcclusionComposer:
    @classmethod
    def compose(
        cls,
        scene: Any,
        *,
        depth_band_ranges: Mapping[
            str,
            tuple[float, float],
        ],
        depth_relations: Mapping[
            str,
            Mapping[str, Any],
        ] | None = None,
        operator_overrides: Mapping[
            str,
            Mapping[str, Any],
        ] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(
            scene,
            AtlasSemanticReliefScene,
        ):
            raise TypeError(
                "scene must be an "
                "AtlasSemanticReliefScene"
            )

        ranges = cls._normalize_depth_band_ranges(
            depth_band_ranges
        )

        ordered_components = []

        components_by_id = {
            component.component_id: component
            for component in scene.components
        }

        normalized_relations = (
            cls._normalize_depth_relations(
                depth_relations,
                components_by_id=components_by_id,
            )
        )

        (
            normalized_overrides,
            operator_override_records,
        ) = cls._normalize_operator_overrides(
            operator_overrides,
            components_by_id=components_by_id,
        )

        def effective_depth_band(component):
            override = normalized_overrides.get(
                component.component_id
            )

            if override is not None:
                return override["depth_band"]

            return component.depth_band

        def resolve_depth_band(component):
            resolved = component
            inherited = False
            depth_band = effective_depth_band(
                resolved
            )

            while (
                depth_band == "primary"
                and resolved.parent_component_id
                is not None
            ):
                resolved = components_by_id[
                    resolved.parent_component_id
                ]
                inherited = True
                depth_band = effective_depth_band(
                    resolved
                )

            return (
                depth_band,
                inherited,
            )

        for component in scene.components:
            (
                resolved_depth_band,
                inherited_depth_band,
            ) = resolve_depth_band(
                component
            )

            if resolved_depth_band not in ranges:
                raise ValueError(
                    "depth_band has no configured "
                    f"range: {resolved_depth_band}"
                )

            local_relief_range = ranges[
                resolved_depth_band
            ]

            depth_relation = (
                normalized_relations.get(
                    component.component_id
                )
            )

            if (
                depth_relation is not None
                and depth_relation["mode"] == "embed"
            ):
                available_depth = (
                    local_relief_range[1]
                    - local_relief_range[0]
                )

                if (
                    depth_relation["depth_amount"]
                    >= available_depth - 1e-12
                ):
                    raise ValueError(
                        "impossible embed: depth_amount "
                        "must be smaller than the resolved "
                        "local relief range"
                    )

            ordered_components.append(
                {
                    "component_id": (
                        component.component_id
                    ),
                    "geometry_boundary_id": (
                        component.component_id
                    ),
                    "semantic_class": (
                        component.semantic_class
                    ),
                    "depth_band": (
                        resolved_depth_band
                    ),
                    "local_relief_range": (
                        local_relief_range
                    ),
                    "layer_order": (
                        component.layer_order
                    ),
                    "occlusion_policy": (
                        component.occlusion_policy
                    ),
                    "material_role": (
                        component.material_role
                    ),
                    "parent_component_id": (
                        component.parent_component_id
                    ),
                    "inherited_depth_band": (
                        inherited_depth_band
                    ),
                    "depth_relation": (
                        depth_relation
                    ),
                }
            )

        ordered_components.sort(
            key=lambda item: (
                item["local_relief_range"][0],
                item["layer_order"],
                item["component_id"],
            )
        )

        conflicts = []

        for index, item in enumerate(
            ordered_components
        ):
            if (
                item["occlusion_policy"]
                == "occludes_lower_layers"
                and index == 0
            ):
                conflicts.append(
                    {
                        "type": (
                            "invalid_occlusion_direction"
                        ),
                        "component_id": (
                            item["component_id"]
                        ),
                        "occlusion_policy": (
                            item["occlusion_policy"]
                        ),
                        "reason": (
                            "component has no lower "
                            "semantic layer to occlude"
                        ),
                    }
                )

        return {
            "type": (
                "semantic_depth_occlusion_plan"
            ),
            "scene_id": scene.scene_id,
            "depth_band_ranges": ranges,
            "ordered_components": tuple(
                ordered_components
            ),
            "conflicts": tuple(
                conflicts
            ),
            "operator_overrides": (
                operator_override_records
            ),
        }

    @classmethod
    def _normalize_operator_overrides(
        cls,
        operator_overrides: Any,
        *,
        components_by_id: Mapping[str, Any],
    ) -> tuple[
        dict[str, dict[str, str]],
        tuple[dict[str, str], ...],
    ]:
        if operator_overrides is None:
            return {}, ()

        if not isinstance(
            operator_overrides,
            Mapping,
        ):
            raise TypeError(
                "operator_overrides must be a mapping or None"
            )

        normalized = {}
        records = []

        for raw_component_id, raw_override in (
            operator_overrides.items()
        ):
            component_id = cls._normalize_identifier(
                raw_component_id,
                field_name="operator override component_id",
            )

            if component_id not in components_by_id:
                raise ValueError(
                    "operator override references unknown component: "
                    f"{component_id}"
                )

            if not isinstance(
                raw_override,
                Mapping,
            ):
                raise TypeError(
                    "operator override must be a mapping"
                )

            fields = tuple(
                raw_override.keys()
            )

            if fields != ("depth_band",):
                unsupported = tuple(
                    str(field)
                    for field in fields
                    if field != "depth_band"
                )

                field_name = (
                    unsupported[0]
                    if unsupported
                    else "missing"
                )

                raise ValueError(
                    "unsupported operator override field: "
                    f"{field_name}"
                )

            override_depth_band = (
                cls._normalize_identifier(
                    raw_override["depth_band"],
                    field_name=(
                        "operator override depth_band"
                    ),
                )
            )

            component = components_by_id[
                component_id
            ]

            normalized[component_id] = {
                "depth_band": override_depth_band,
            }

            records.append(
                {
                    "component_id": component_id,
                    "field": "depth_band",
                    "original_value": (
                        component.depth_band
                    ),
                    "override_value": (
                        override_depth_band
                    ),
                }
            )

        records.sort(
            key=lambda item: (
                item["component_id"],
                item["field"],
            )
        )

        return (
            normalized,
            tuple(records),
        )

    @classmethod
    def _normalize_depth_relations(
        cls,
        depth_relations: Any,
        *,
        components_by_id: Mapping[str, Any],
    ) -> dict[str, dict[str, Any]]:
        if depth_relations is None:
            return {}

        if not isinstance(
            depth_relations,
            Mapping,
        ):
            raise TypeError(
                "depth_relations must be a mapping or None"
            )

        normalized = {}

        for raw_component_id, raw_relation in (
            depth_relations.items()
        ):
            component_id = cls._normalize_identifier(
                raw_component_id,
                field_name="depth_relation component_id",
            )

            if component_id not in components_by_id:
                raise ValueError(
                    "depth relation references unknown component: "
                    f"{component_id}"
                )

            if not isinstance(
                raw_relation,
                Mapping,
            ):
                raise TypeError(
                    "depth relation must be a mapping"
                )

            if "mode" not in raw_relation:
                raise ValueError(
                    "depth relation requires mode"
                )

            mode = cls._normalize_identifier(
                raw_relation["mode"],
                field_name="depth_relation mode",
            )

            if mode not in {
                "contact",
                "embed",
                "recess",
                "raised",
            }:
                raise ValueError(
                    "unsupported depth relation mode: "
                    f"{mode}"
                )

            component = components_by_id[
                component_id
            ]

            parent_component_id = (
                component.parent_component_id
            )

            has_depth_amount = (
                "depth_amount" in raw_relation
            )
            depth_amount = raw_relation.get(
                "depth_amount"
            )

            if mode == "contact":
                if has_depth_amount:
                    raise ValueError(
                        "contact relation must not define "
                        "depth_amount"
                    )
                depth_amount = None
            else:
                if not has_depth_amount:
                    raise ValueError(
                        "depth_amount is required for "
                        f"{mode} relation"
                    )

                depth_amount = cls._finite_number(
                    depth_amount,
                    field_name="depth_amount",
                )

                if depth_amount <= 0.0:
                    raise ValueError(
                        "depth_amount must be greater than zero"
                    )

                if parent_component_id is None:
                    raise ValueError(
                        f"{mode} relation requires parent component"
                    )

            normalized[component_id] = {
                "mode": mode,
                "depth_amount": depth_amount,
                "parent_component_id": (
                    parent_component_id
                ),
            }

        return normalized

    @classmethod
    def _normalize_depth_band_ranges(
        cls,
        depth_band_ranges: Any,
    ) -> dict[
        str,
        tuple[float, float],
    ]:
        if not isinstance(
            depth_band_ranges,
            Mapping,
        ):
            raise TypeError(
                "depth_band_ranges must be a mapping"
            )

        if not depth_band_ranges:
            raise ValueError(
                "depth_band_ranges must not be empty"
            )

        normalized = {}

        for raw_name, raw_range in (
            depth_band_ranges.items()
        ):
            name = cls._normalize_identifier(
                raw_name,
                field_name="depth_band",
            )

            if name in normalized:
                raise ValueError(
                    "duplicate normalized depth_band"
                )

            if (
                not isinstance(
                    raw_range,
                    (tuple, list),
                )
                or len(raw_range) != 2
            ):
                raise ValueError(
                    "depth band range must contain "
                    "exactly two numeric values"
                )

            lower = cls._finite_number(
                raw_range[0],
                field_name="depth_band_range[0]",
            )
            upper = cls._finite_number(
                raw_range[1],
                field_name="depth_band_range[1]",
            )

            if (
                lower < 0.0
                or upper > 1.0
                or lower >= upper
            ):
                raise ValueError(
                    "depth band range must satisfy "
                    "0.0 <= lower < upper <= 1.0"
                )

            normalized[name] = (
                lower,
                upper,
            )

        ordered_ranges = sorted(
            normalized.items(),
            key=lambda item: (
                item[1][0],
                item[1][1],
                item[0],
            ),
        )

        for (
            previous_name,
            previous_range,
        ), (
            current_name,
            current_range,
        ) in zip(
            ordered_ranges,
            ordered_ranges[1:],
        ):
            if current_range[0] < previous_range[1]:
                raise ValueError(
                    "depth band ranges overlap: "
                    f"{previous_name} and {current_name}"
                )

        return normalized

    @staticmethod
    def _normalize_identifier(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank"
            )

        return normalized

    @staticmethod
    def _finite_number(
        value: Any,
        *,
        field_name: str,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be numeric"
            )

        try:
            numeric = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{field_name} must be numeric"
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{field_name} must be finite"
            )

        return numeric
