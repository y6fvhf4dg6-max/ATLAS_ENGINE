from collections.abc import Mapping
import math
from dataclasses import dataclass

from CORE.atlas_worldcover_surface_aggregator import (
    AtlasWorldCoverSurfaceAggregator,
)


@dataclass(frozen=True, slots=True)
class AtlasVegetationCompositionProfile:
    semantic_role: str
    representation_mode: str

    _ROLE_MODES = {
        "isolated_tree": "individual",
        "tree_row": "ordered_row",
        "tree_cluster": "controlled_cluster",
        "forest_canopy": "continuous_canopy",
    }

    def __post_init__(self):
        expected_mode = self._ROLE_MODES.get(self.semantic_role)

        if expected_mode is None:
            raise ValueError(
                f"unsupported vegetation semantic_role: {self.semantic_role}"
            )

        if self.representation_mode != expected_mode:
            raise ValueError(
                f"{self.semantic_role} requires representation_mode={expected_mode}"
            )


class AtlasVegetationCompositionResolver:
    _ROLE_MODES = {
        "isolated_tree": "individual",
        "tree_row": "ordered_row",
        "tree_cluster": "controlled_cluster",
        "forest_canopy": "continuous_canopy",
    }

    @staticmethod
    def resolve_semantic_role(source):
        if not isinstance(source, Mapping):
            raise TypeError("source must be a mapping")

        vegetation_role = source.get("vegetation_role")
        if vegetation_role == "tree_cluster":
            return "tree_cluster"

        if (
            source.get("source") == "worldcover"
            and source.get("class_id") == 10
        ):
            return "forest_canopy"

        tags = source.get("tags") or {}
        if isinstance(tags, Mapping):
            source_name = tags.get("source")

            if source_name == "worldcover":
                return "forest_canopy"

            if source_name == "osm_green_area_fill":
                return "tree_cluster"

        tree_type = source.get("tree_type")
        if tree_type == "tree":
            return "isolated_tree"
        if tree_type == "tree_row":
            return "tree_row"

        if source.get("surface_type") == "forest":
            return "forest_canopy"

        return None

    @classmethod
    def resolve_profile(cls, source):
        semantic_role = cls.resolve_semantic_role(source)

        if semantic_role is None:
            return None

        return AtlasVegetationCompositionProfile(
            semantic_role=semantic_role,
            representation_mode=cls._ROLE_MODES[semantic_role],
        )

    @classmethod
    def resolve_collection(cls, sources):
        grouped = {
            "isolated_tree": [],
            "tree_row": [],
            "tree_cluster": [],
            "forest_canopy": [],
        }

        for source in sources or ():
            semantic_role = cls.resolve_semantic_role(source)

            if semantic_role is None:
                continue

            grouped[semantic_role].append(source)

        return {
            role: tuple(
                sorted(
                    grouped[role],
                    key=cls._source_sort_key,
                )
            )
            for role in (
                "isolated_tree",
                "tree_row",
                "tree_cluster",
                "forest_canopy",
            )
        }

    @staticmethod
    def _source_sort_key(source):
        source_id = source.get("id")

        if isinstance(source_id, int) and not isinstance(source_id, bool):
            return (0, source_id)

        if isinstance(source_id, str):
            return (1, source_id)

        if source_id is not None:
            return (2, repr(source_id))

        return (3, repr(source))

    @classmethod
    def _split_forest_canopy_groups(cls, sources):
        remaining = list(
            sorted(
                sources,
                key=cls._source_sort_key,
            )
        )
        groups = []

        while remaining:
            seed = remaining.pop(0)
            group = [seed]
            frontier = [seed]

            while frontier:
                current = frontier.pop(0)
                connected = []

                for candidate in remaining:
                    if cls._forest_cells_connected(
                        current,
                        candidate,
                    ):
                        connected.append(candidate)

                for candidate in connected:
                    remaining.remove(candidate)
                    group.append(candidate)
                    frontier.append(candidate)

            groups.append(
                tuple(
                    sorted(
                        group,
                        key=cls._source_sort_key,
                    )
                )
            )

        return tuple(groups)

    @classmethod
    def _forest_cells_connected(cls, first, second):
        required_coordinates = ("lat", "lon")

        if (
            any(key not in first for key in required_coordinates)
            or any(key not in second for key in required_coordinates)
        ):
            return True

        first_tags = first.get("tags") or {}
        second_tags = second.get("tags") or {}

        first_resolution = float(
            first.get(
                "resolution_m",
                first_tags.get("resolution_m", 10),
            )
        )
        second_resolution = float(
            second.get(
                "resolution_m",
                second_tags.get("resolution_m", 10),
            )
        )

        adjacency_m = (
            max(first_resolution, second_resolution)
            * math.sqrt(2.0)
            * 1.05
        )

        return (
            cls._distance_meters(first, second)
            <= adjacency_m
        )

    @staticmethod
    def _distance_meters(first, second):
        lat1 = float(first["lat"])
        lon1 = float(first["lon"])
        lat2 = float(second["lat"])
        lon2 = float(second["lon"])

        mean_lat = math.radians(
            (lat1 + lat2) / 2.0
        )

        meters_per_degree_lat = 111_320.0
        meters_per_degree_lon = (
            111_320.0 * math.cos(mean_lat)
        )

        dx = (lon2 - lon1) * meters_per_degree_lon
        dy = (lat2 - lat1) * meters_per_degree_lat

        return math.sqrt(dx * dx + dy * dy)

    @classmethod
    def resolve_forest_canopy_group(cls, sources):
        members = tuple(
            sorted(
                tuple(sources or ()),
                key=cls._source_sort_key,
            )
        )

        if not members:
            raise ValueError(
                "forest_canopy group must not be empty"
            )

        for source in members:
            if cls.resolve_semantic_role(source) != "forest_canopy":
                raise ValueError(
                    "forest_canopy group requires forest_canopy members"
                )

        return {
            "semantic_role": "forest_canopy",
            "representation_mode": "continuous_canopy",
            "members": members,
        }

    @classmethod
    def resolve_tree_cluster_group(cls, sources):
        members = tuple(
            sorted(
                tuple(sources or ()),
                key=cls._source_sort_key,
            )
        )

        if not members:
            raise ValueError(
                "tree_cluster group must not be empty"
            )

        for source in members:
            if cls.resolve_semantic_role(source) != "tree_cluster":
                raise ValueError(
                    "tree_cluster group requires tree_cluster members"
                )

        return {
            "semantic_role": "tree_cluster",
            "representation_mode": "controlled_cluster",
            "members": members,
        }

    @classmethod
    def compose_collection(cls, sources):
        grouped = cls.resolve_collection(sources)

        tree_clusters = ()

        if grouped["tree_cluster"]:
            cluster_groups = {}

            for source in grouped["tree_cluster"]:
                tags = source.get("tags") or {}
                park_id = (
                    tags.get("park_id")
                    if isinstance(tags, Mapping)
                    else None
                )

                group_key = (
                    ("park", park_id)
                    if park_id is not None
                    else ("ungrouped", None)
                )

                cluster_groups.setdefault(
                    group_key,
                    [],
                ).append(source)

            tree_clusters = tuple(
                cls.resolve_tree_cluster_group(
                    cluster_groups[group_key]
                )
                for group_key in sorted(
                    cluster_groups,
                    key=repr,
                )
            )

        forest_canopies = ()
        if grouped["forest_canopy"]:
            forest_canopies = tuple(
                cls.resolve_forest_canopy_group(group)
                for group in cls._split_forest_canopy_groups(
                    grouped["forest_canopy"]
                )
            )

        return {
            "isolated_trees": grouped["isolated_tree"],
            "tree_rows": grouped["tree_row"],
            "tree_clusters": tree_clusters,
            "forest_canopies": forest_canopies,
        }

    @classmethod
    def resolve_forest_canopy_surfaces(cls, canopy):
        if not isinstance(canopy, Mapping):
            raise TypeError("canopy must be a mapping")

        if canopy.get("semantic_role") != "forest_canopy":
            raise ValueError(
                "canopy semantic_role must be forest_canopy"
            )

        members = canopy.get("members") or ()

        return tuple(
            AtlasWorldCoverSurfaceAggregator.dissolve(
                cells=members,
                surface_type="forest",
            )
        )

    @classmethod
    def compose_nature_data(cls, nature_data):
        if not isinstance(nature_data, Mapping):
            raise TypeError("nature_data must be a mapping")

        sources = []

        for tree in nature_data.get("trees", ()):
            tags = tree.get("tags") or {}

            if (
                isinstance(tags, Mapping)
                and tags.get("source") == "worldcover"
            ):
                continue

            sources.append(tree)

        sources.extend(
            nature_data.get("tree_rows", ())
        )

        sources.extend(
            nature_data.get("forests", ())
        )

        result = cls.compose_collection(sources)

        forest_canopy_surfaces = tuple(
            surface
            for canopy in result["forest_canopies"]
            for surface in cls.resolve_forest_canopy_surfaces(
                canopy
            )
        )

        return {
            **result,
            "forest_canopy_surfaces": forest_canopy_surfaces,
        }
