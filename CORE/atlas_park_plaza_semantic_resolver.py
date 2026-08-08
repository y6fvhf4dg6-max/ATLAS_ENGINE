from collections.abc import Mapping
from dataclasses import dataclass

from shapely.geometry import LineString, Polygon


@dataclass(frozen=True, slots=True)
class AtlasParkPlazaSemanticProfile:
    semantic_class: str
    ground_surface_role: str
    supports_internal_paths: bool = False
    supports_tree_rows: bool = False
    supports_vegetation_clusters: bool = False
    supports_clearings: bool = False
    supports_borders: bool = False
    supports_edges: bool = False


class AtlasParkPlazaSemanticResolver:
    @classmethod
    def resolve_surface_record(
        cls,
        source,
        *,
        geometry_role=None,
        pedestrian_paths=(),
    ):
        if not isinstance(source, Mapping):
            raise TypeError("source must be a mapping")

        tags = source.get("tags", {})

        if not isinstance(tags, Mapping):
            raise TypeError("tags must be a mapping")

        profile = cls.resolve_profile(
            tags,
            geometry_role=geometry_role,
        )

        if profile is None:
            return None

        internal_paths = list(
            source.get("internal_paths", ())
        )

        if (
            profile.supports_internal_paths
            and pedestrian_paths
        ):
            park_geometry = source.get("geometry", ())

            if len(park_geometry) >= 3:
                park_shape = Polygon(park_geometry)

                if (
                    park_shape.is_valid
                    and park_shape.area > 0.0
                ):
                    for path in pedestrian_paths:
                        path_geometry = path.get("geometry", ())

                        if len(path_geometry) < 2:
                            continue

                        path_shape = LineString(path_geometry)

                        if (
                            path_shape.is_valid
                            and not path_shape.is_empty
                            and park_shape.covers(path_shape)
                        ):
                            internal_paths.append(path)

        deduplicated_internal_paths = []
        seen_internal_path_ids = set()

        for path in internal_paths:
            path_id = path.get("id")

            if (
                path_id is not None
                and path_id in seen_internal_path_ids
            ):
                continue

            if path_id is not None:
                seen_internal_path_ids.add(path_id)

            deduplicated_internal_paths.append(path)

        def internal_path_sort_key(path):
            path_id = path.get("id")

            if isinstance(path_id, int) and not isinstance(path_id, bool):
                return (0, path_id)

            if isinstance(path_id, str):
                return (1, path_id)

            if path_id is not None:
                return (2, repr(path_id))

            return (3, repr(path.get("geometry", ())))

        internal_paths = tuple(
            sorted(
                deduplicated_internal_paths,
                key=internal_path_sort_key,
            )
        )

        composition_layers = [
            profile.ground_surface_role,
        ]

        supported_layers = (
            (
                "internal_paths",
                profile.supports_internal_paths,
            ),
            (
                "tree_rows",
                profile.supports_tree_rows,
            ),
            (
                "vegetation_clusters",
                profile.supports_vegetation_clusters,
            ),
        )

        for key, supported in supported_layers:
            value = (
                internal_paths
                if key == "internal_paths"
                else source.get(key)
            )
            if supported and value:
                composition_layers.append(key)

        extended_layers = (
            ("clearings", profile.supports_clearings),
            ("borders", profile.supports_borders),
            ("edges", profile.supports_edges),
        )

        for key, supported in extended_layers:
            if supported and source.get(key):
                composition_layers.append(key)

        return {
            "source_id": source.get("id"),
            "semantic_class": profile.semantic_class,
            "ground_surface_role": profile.ground_surface_role,
            "composition_layers": tuple(composition_layers),
            "geometry": source.get("geometry"),
            "source_park_type": source.get("park_type"),
            "supports_internal_paths": profile.supports_internal_paths,
            "internal_paths": internal_paths,
            "supports_tree_rows": profile.supports_tree_rows,
            "tree_rows": source.get("tree_rows", ()),
            "supports_vegetation_clusters": (
                profile.supports_vegetation_clusters
            ),
            "supports_clearings": profile.supports_clearings,
            "supports_borders": profile.supports_borders,
            "supports_edges": profile.supports_edges,
            "vegetation_clusters": source.get(
                "vegetation_clusters",
                (),
            ),
            "clearings": source.get("clearings", ()),
            "borders": source.get("borders", ()),
            "edges": source.get("edges", ()),
        }

    @classmethod
    def resolve_profile(
        cls,
        tags,
        *,
        geometry_role=None,
    ):
        semantic_class = cls.resolve_semantic_class(
            tags,
            geometry_role=geometry_role,
        )

        if semantic_class == "park":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="park",
                ground_surface_role="park_ground",
                supports_internal_paths=True,
                supports_tree_rows=True,
                supports_vegetation_clusters=True,
                supports_clearings=True,
                supports_borders=True,
                supports_edges=True,
            )

        if semantic_class == "plaza":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="plaza",
                ground_surface_role="plaza_ground",
            )

        if semantic_class == "pedestrian_square":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="pedestrian_square",
                ground_surface_role="pedestrian_square_ground",
            )

        if semantic_class == "garden":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="garden",
                ground_surface_role="garden_ground",
                supports_internal_paths=True,
                supports_tree_rows=True,
                supports_vegetation_clusters=True,
            )

        if semantic_class == "grass_area":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="grass_area",
                ground_surface_role="grass_ground",
            )

        if semantic_class == "cemetery":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="cemetery",
                ground_surface_role="cemetery_ground",
            )

        if semantic_class == "sports_field":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="sports_field",
                ground_surface_role="sports_field_ground",
            )

        if semantic_class == "courtyard":
            return AtlasParkPlazaSemanticProfile(
                semantic_class="courtyard",
                ground_surface_role="courtyard_ground",
            )

        return None

    @classmethod
    def resolve_semantic_class(
        cls,
        tags,
        *,
        geometry_role=None,
    ):
        if not isinstance(tags, Mapping):
            raise TypeError("tags must be a mapping")

        if geometry_role == "courtyard":
            return "courtyard"

        if tags.get("leisure") == "park":
            return "park"

        if tags.get("leisure") == "garden":
            return "garden"

        if (
            tags.get("highway") == "pedestrian"
            and tags.get("area") == "yes"
        ):
            return "pedestrian_square"

        if tags.get("place") == "square":
            return "plaza"

        if tags.get("landuse") == "grass":
            return "grass_area"

        if tags.get("landuse") == "cemetery":
            return "cemetery"

        if tags.get("leisure") == "pitch":
            return "sports_field"

        return None
