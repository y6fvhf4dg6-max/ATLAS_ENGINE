from __future__ import annotations

from copy import deepcopy


class AtlasCityCompositionMeshFilter:
    GROUP_SOURCE_CONTRACTS = {
        "roads": ("road", "source_id"),
        "parks": ("park", "source_id"),
        "buildings": ("building", "source_id"),
        "waters": ("water", "source_id"),
        "landmarks": ("landmark", "landmark_id"),
    }

    @classmethod
    def filter(
        cls,
        *,
        mesh_groups,
        decisions,
    ):
        if not isinstance(mesh_groups, dict):
            raise TypeError(
                "mesh_groups must be a dictionary"
            )

        if not isinstance(decisions, dict):
            raise TypeError(
                "decisions must be a dictionary"
            )

        filtered_groups = deepcopy(mesh_groups)
        suppressed_mesh_count = 0

        for group_name, contract in (
            cls.GROUP_SOURCE_CONTRACTS.items()
        ):
            if group_name not in mesh_groups:
                continue

            prefix, source_key = contract
            source_meshes = mesh_groups[group_name]

            if not isinstance(
                source_meshes,
                (list, tuple),
            ):
                raise TypeError(
                    f"{group_name} must be a list or tuple"
                )

            retained_meshes = []

            for mesh in source_meshes:
                if not isinstance(mesh, dict):
                    retained_meshes.append(
                        deepcopy(mesh)
                    )
                    continue

                source_id = mesh.get(source_key)

                if source_id is None:
                    retained_meshes.append(
                        deepcopy(mesh)
                    )
                    continue

                element_id = (
                    f"{prefix}_{source_id}"
                )

                decision = decisions.get(
                    element_id
                )

                if (
                    isinstance(decision, dict)
                    and decision.get("retain")
                    is False
                ):
                    suppressed_mesh_count += 1
                    continue

                retained_meshes.append(
                    deepcopy(mesh)
                )

            filtered_groups[group_name] = (
                retained_meshes
            )

        return {
            "mesh_groups": filtered_groups,
            "suppressed_mesh_count": (
                suppressed_mesh_count
            ),
        }
