from __future__ import annotations

import math
from dataclasses import dataclass


REQUIRED_URBAN_FABRIC_SEMANTIC_CLASSES = frozenset(
    {
        "road",
        "railway",
        "pedestrian_path",
        "urban_block",
        "generic_building",
        "park",
        "plaza",
        "vegetation",
        "water",
        "infrastructure_corridor",
        "terrain",
    }
)


def _normalize_identifier(
    value,
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


def _normalize_related_ids(
    values,
) -> tuple[str, ...]:
    normalized = tuple(
        _normalize_identifier(
            value,
            field_name="related_element_ids",
        )
        for value in values
    )

    if len(normalized) != len(set(normalized)):
        raise ValueError(
            "related_element_ids must contain unique values"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class AtlasUrbanFabricElement:
    element_id: str
    semantic_class: str
    source_id: int | str | None = None
    source_type: str | None = None
    product_priority: float = 0.0
    lod_eligible: bool = True
    geometry_ref: str | None = None
    related_element_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        element_id = _normalize_identifier(
            self.element_id,
            field_name="element_id",
        )
        semantic_class = _normalize_identifier(
            self.semantic_class,
            field_name="semantic_class",
        )

        try:
            product_priority = float(
                self.product_priority
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "product_priority must be numeric"
            ) from exc

        if not math.isfinite(product_priority):
            raise ValueError(
                "product_priority must be finite"
            )

        if not 0.0 <= product_priority <= 1.0:
            raise ValueError(
                "product_priority must be in the 0.0..1.0 range"
            )

        if not isinstance(self.lod_eligible, bool):
            raise TypeError(
                "lod_eligible must be a bool"
            )

        source_id = self.source_id

        if isinstance(source_id, bool):
            raise TypeError(
                "source_id must not be a bool"
            )

        if isinstance(source_id, str):
            source_id = _normalize_identifier(
                source_id,
                field_name="source_id",
            )

        source_type = (
            None
            if self.source_type is None
            else _normalize_identifier(
                self.source_type,
                field_name="source_type",
            )
        )

        geometry_ref = (
            None
            if self.geometry_ref is None
            else _normalize_identifier(
                self.geometry_ref,
                field_name="geometry_ref",
            )
        )

        related_element_ids = _normalize_related_ids(
            self.related_element_ids
        )

        object.__setattr__(
            self,
            "element_id",
            element_id,
        )
        object.__setattr__(
            self,
            "semantic_class",
            semantic_class,
        )
        object.__setattr__(
            self,
            "source_id",
            source_id,
        )
        object.__setattr__(
            self,
            "source_type",
            source_type,
        )
        object.__setattr__(
            self,
            "product_priority",
            product_priority,
        )
        object.__setattr__(
            self,
            "geometry_ref",
            geometry_ref,
        )
        object.__setattr__(
            self,
            "related_element_ids",
            related_element_ids,
        )


@dataclass(frozen=True, slots=True)
class AtlasUrbanFabricRelationship:
    relationship_id: str
    relation_type: str
    source_element_id: str
    target_element_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "relationship_id",
            _normalize_identifier(
                self.relationship_id,
                field_name="relationship_id",
            ),
        )
        object.__setattr__(
            self,
            "relation_type",
            _normalize_identifier(
                self.relation_type,
                field_name="relation_type",
            ),
        )
        object.__setattr__(
            self,
            "source_element_id",
            _normalize_identifier(
                self.source_element_id,
                field_name="source_element_id",
            ),
        )
        object.__setattr__(
            self,
            "target_element_id",
            _normalize_identifier(
                self.target_element_id,
                field_name="target_element_id",
            ),
        )


@dataclass(frozen=True, slots=True)
class AtlasUrbanFabricScene:
    elements: tuple[AtlasUrbanFabricElement, ...] = ()
    relationships: tuple[AtlasUrbanFabricRelationship, ...] = ()

    def __post_init__(self) -> None:
        elements = tuple(self.elements)

        for element in elements:
            if not isinstance(
                element,
                AtlasUrbanFabricElement,
            ):
                raise TypeError(
                    "elements must contain "
                    "AtlasUrbanFabricElement values"
                )

        element_ids = tuple(
            element.element_id
            for element in elements
        )

        if len(element_ids) != len(set(element_ids)):
            raise ValueError(
                "elements must have unique element_id values"
            )

        element_id_set = set(element_ids)

        for element in elements:
            for related_element_id in element.related_element_ids:
                if related_element_id not in element_id_set:
                    raise ValueError(
                        "related_element_ids must reference "
                        "elements present in the scene"
                    )

        relationships = tuple(
            self.relationships
        )

        relationship_ids = set()

        for relationship in relationships:
            if not isinstance(
                relationship,
                AtlasUrbanFabricRelationship,
            ):
                raise TypeError(
                    "relationships must contain "
                    "AtlasUrbanFabricRelationship values"
                )

            if relationship.relationship_id in relationship_ids:
                raise ValueError(
                    "relationships must have unique "
                    "relationship_id values"
                )

            relationship_ids.add(
                relationship.relationship_id
            )

            if (
                relationship.source_element_id
                not in element_id_set
                or relationship.target_element_id
                not in element_id_set
            ):
                raise ValueError(
                    "relationship endpoints must reference "
                    "elements present in the scene"
                )

        object.__setattr__(
            self,
            "elements",
            elements,
        )
        object.__setattr__(
            self,
            "relationships",
            relationships,
        )

    def semantic_classes(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    element.semantic_class
                    for element in self.elements
                }
            )
        )

    def missing_required_semantic_classes(
        self,
    ) -> tuple[str, ...]:
        present = set(
            self.semantic_classes()
        )

        return tuple(
            sorted(
                REQUIRED_URBAN_FABRIC_SEMANTIC_CLASSES
                - present
            )
        )

    def get_element(
        self,
        element_id,
    ) -> AtlasUrbanFabricElement | None:
        normalized_id = _normalize_identifier(
            element_id,
            field_name="element_id",
        )

        for element in self.elements:
            if element.element_id == normalized_id:
                return element

        return None

    def elements_for_class(
        self,
        semantic_class,
    ) -> tuple[AtlasUrbanFabricElement, ...]:
        normalized_class = _normalize_identifier(
            semantic_class,
            field_name="semantic_class",
        )

        return tuple(
            element
            for element in self.elements
            if element.semantic_class == normalized_class
        )
