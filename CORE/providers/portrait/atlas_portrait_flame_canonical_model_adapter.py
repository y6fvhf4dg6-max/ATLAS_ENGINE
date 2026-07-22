from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


class AtlasPortraitFlameCanonicalModelAdapter:
    """
    Adapts raw FLAME model mappings to the ATLAS canonical contract.

    Supported source fields:

    - v_template
    - f or faces
    - shapedirs
    - posedirs
    - J_regressor
    - weights
    - kintree_table or parents

    The adapter performs no file loading, parameter fitting,
    deformation, projection, rendering, relief generation,
    or STL generation.
    """

    @classmethod
    def adapt(
        cls,
        *,
        source: Any,
        identity_parameter_count: Any,
        expression_parameter_count: Any,
        model_version: Any,
        source_format: Any,
    ) -> AtlasPortraitFlameCanonicalModel:
        if not isinstance(
            source,
            Mapping,
        ):
            raise TypeError(
                "source must be a mapping."
            )

        identity_count = cls._normalize_parameter_count(
            identity_parameter_count,
            name="identity_parameter_count",
        )
        expression_count = cls._normalize_parameter_count(
            expression_parameter_count,
            name="expression_parameter_count",
        )

        normalized_model_version = cls._normalize_required_text(
            model_version,
            name="model_version",
        )
        normalized_source_format = cls._normalize_required_text(
            source_format,
            name="source_format",
        )

        template_vertices = cls._require_array_field(
            source,
            "v_template",
        )

        triangle_faces = cls._resolve_triangle_faces(
            source,
        )

        shape_directions = cls._require_array_field(
            source,
            "shapedirs",
        )
        shape_directions = cls._normalize_shape_directions(
            shape_directions,
            vertex_count=cls._vertex_count(
                template_vertices,
            ),
        )

        total_requested_shape_count = (
            identity_count
            + expression_count
        )

        if (
            shape_directions.shape[2]
            < total_requested_shape_count
        ):
            raise ValueError(
                "identity_parameter_count and "
                "expression_parameter_count exceed the "
                "available shapedirs parameter_count."
            )

        identity_shape_directions = (
            shape_directions[
                :,
                :,
                :identity_count,
            ]
        )
        expression_shape_directions = (
            shape_directions[
                :,
                :,
                identity_count:
                total_requested_shape_count,
            ]
        )

        pose_directions = cls._normalize_pose_directions(
            cls._require_array_field(
                source,
                "posedirs",
            ),
            vertex_count=cls._vertex_count(
                template_vertices,
            ),
        )

        joint_regressor = cls._normalize_joint_regressor(
            cls._require_field(
                source,
                "J_regressor",
            )
        )

        skinning_weights = cls._require_array_field(
            source,
            "weights",
        )

        kinematic_tree = cls._resolve_kinematic_tree(
            source,
        )

        joint_count = cls._joint_count(
            joint_regressor,
        )
        pose_parameter_count = (
            joint_count
            * 3
        )

        metadata = {
            "expression_parameter_count": (
                expression_count
            ),
            "identity_parameter_count": (
                identity_count
            ),
            "model_family": "flame",
            "model_version": (
                normalized_model_version
            ),
            "source_format": (
                normalized_source_format
            ),
            "synthetic": False,
        }

        return AtlasPortraitFlameCanonicalModel(
            template_vertices=template_vertices,
            triangle_faces=triangle_faces,
            identity_shape_directions=(
                identity_shape_directions
            ),
            expression_shape_directions=(
                expression_shape_directions
            ),
            pose_directions=pose_directions,
            pose_parameter_count=(
                pose_parameter_count
            ),
            joint_regressor=joint_regressor,
            skinning_weights=skinning_weights,
            kinematic_tree=kinematic_tree,
            metadata=metadata,
        )

    @staticmethod
    def _require_field(
        source: Mapping[str, Any],
        field_name: str,
    ) -> Any:
        try:
            return source[
                field_name
            ]
        except KeyError as exc:
            raise ValueError(
                f"{field_name} is required."
            ) from exc

    @classmethod
    def _require_array_field(
        cls,
        source: Mapping[str, Any],
        field_name: str,
    ) -> np.ndarray:
        value = cls._require_field(
            source,
            field_name,
        )

        try:
            return np.asarray(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{field_name} must be array-like."
            ) from exc

    @staticmethod
    def _resolve_triangle_faces(
        source: Mapping[str, Any],
    ) -> np.ndarray:
        if "f" in source:
            value = source[
                "f"
            ]
        elif "faces" in source:
            value = source[
                "faces"
            ]
        else:
            raise ValueError(
                "faces field is required; expected "
                "'f' or 'faces'."
            )

        try:
            return np.asarray(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "faces must be array-like."
            ) from exc

    @staticmethod
    def _normalize_shape_directions(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        try:
            directions = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "shapedirs must be numeric."
            ) from exc

        if (
            directions.ndim != 3
            or directions.shape[0]
            != vertex_count
            or directions.shape[1] != 3
            or directions.shape[2] < 1
        ):
            raise ValueError(
                "shapedirs must have shape "
                f"({vertex_count}, 3, P) with P >= 1."
            )

        if not np.isfinite(
            directions,
        ).all():
            raise ValueError(
                "shapedirs contains non-finite values."
            )

        return directions.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_pose_directions(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        try:
            directions = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "posedirs must be numeric."
            ) from exc

        if directions.ndim == 3:
            if (
                directions.shape[0]
                != vertex_count
                or directions.shape[1] != 3
                or directions.shape[2] < 1
            ):
                raise ValueError(
                    "posedirs tensor must have shape "
                    f"({vertex_count}, 3, P) with P >= 1."
                )

            normalized = directions

        elif directions.ndim == 2:
            expected_flat_vertex_count = (
                vertex_count
                * 3
            )

            if (
                directions.shape[0]
                != expected_flat_vertex_count
                or directions.shape[1] < 1
            ):
                raise ValueError(
                    "posedirs matrix must have shape "
                    f"({expected_flat_vertex_count}, P) "
                    "with P >= 1."
                )

            normalized = directions.reshape(
                vertex_count,
                3,
                directions.shape[1],
            )

        else:
            raise ValueError(
                "posedirs must be either a "
                "two-dimensional flattened matrix or "
                "a three-dimensional direction tensor."
            )

        if not np.isfinite(
            normalized,
        ).all():
            raise ValueError(
                "posedirs contains non-finite values."
            )

        return normalized.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_joint_regressor(
        value: Any,
    ) -> np.ndarray:
        if hasattr(
            value,
            "toarray",
        ):
            try:
                value = value.toarray()
            except Exception as exc:
                raise ValueError(
                    "J_regressor sparse conversion failed."
                ) from exc

        try:
            regressor = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "J_regressor must be numeric."
            ) from exc

        if (
            regressor.ndim != 2
            or regressor.shape[0] < 1
            or regressor.shape[1] < 1
        ):
            raise ValueError(
                "J_regressor must have shape (J, N)."
            )

        if not np.isfinite(
            regressor,
        ).all():
            raise ValueError(
                "J_regressor contains non-finite values."
            )

        return regressor.astype(
            np.float64,
            copy=True,
        )

    @classmethod
    def _resolve_kinematic_tree(
        cls,
        source: Mapping[str, Any],
    ) -> np.ndarray:
        if "parents" in source:
            return cls._normalize_parent_vector(
                source[
                    "parents"
                ]
            )

        if "kintree_table" in source:
            return cls._normalize_kintree_table(
                source[
                    "kintree_table"
                ]
            )

        raise ValueError(
            "kinematic hierarchy is required; expected "
            "'kintree_table' or 'parents'."
        )

    @staticmethod
    def _normalize_parent_vector(
        value: Any,
    ) -> np.ndarray:
        try:
            numeric = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "parents must be numeric."
            ) from exc

        if (
            numeric.ndim != 1
            or numeric.shape[0] < 1
        ):
            raise ValueError(
                "parents must have shape (J,)."
            )

        if not np.isfinite(
            numeric,
        ).all():
            raise ValueError(
                "parents contains non-finite values."
            )

        if not np.equal(
            numeric,
            np.rint(
                numeric,
            ),
        ).all():
            raise ValueError(
                "parents must contain integer values."
            )

        return numeric.astype(
            np.int64,
            copy=True,
        )

    @staticmethod
    def _normalize_kintree_table(
        value: Any,
    ) -> np.ndarray:
        try:
            numeric = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "kintree_table must be numeric."
            ) from exc

        if (
            numeric.ndim != 2
            or numeric.shape[0] != 2
            or numeric.shape[1] < 1
        ):
            raise ValueError(
                "kintree_table must have shape (2, J)."
            )

        if not np.isfinite(
            numeric,
        ).all():
            raise ValueError(
                "kintree_table contains non-finite values."
            )

        parent_row = numeric[
            0
        ]

        if not np.equal(
            parent_row,
            np.rint(
                parent_row,
            ),
        ).all():
            raise ValueError(
                "kintree_table parent row must contain "
                "integer values."
            )

        return parent_row.astype(
            np.int64,
            copy=True,
        )

    @staticmethod
    def _normalize_parameter_count(
        value: Any,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(
                value,
                bool,
            )
            or not isinstance(
                value,
                (
                    int,
                    np.integer,
                ),
            )
        ):
            raise TypeError(
                f"{name} must be a positive "
                "parameter_count integer."
            )

        normalized = int(
            value,
        )

        if normalized < 1:
            raise ValueError(
                f"{name} parameter_count must be "
                "greater than zero."
            )

        return normalized

    @staticmethod
    def _normalize_required_text(
        value: Any,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized

    @staticmethod
    def _vertex_count(
        template_vertices: Any,
    ) -> int:
        try:
            vertices = np.asarray(
                template_vertices,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "v_template must be array-like."
            ) from exc

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 3
            or vertices.shape[0] < 3
        ):
            raise ValueError(
                "v_template must have shape (N, 3) "
                "with N >= 3."
            )

        return int(
            vertices.shape[0]
        )

    @staticmethod
    def _joint_count(
        joint_regressor: np.ndarray,
    ) -> int:
        return int(
            joint_regressor.shape[0]
        )
