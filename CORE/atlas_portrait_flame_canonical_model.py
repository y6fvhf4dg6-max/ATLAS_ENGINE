from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitFlameCanonicalModel:
    """
    Immutable provider-independent FLAME canonical model.

    The contract stores template geometry, fixed topology,
    identity and expression shape directions, pose
    directions, joint regression data, skinning weights,
    kinematic hierarchy, and deterministic metadata.

    It performs no model loading, parameter initialization,
    fitting, optimization, blendshape evaluation, linear
    blend skinning, mesh deformation, projection,
    rendering, relief compression, or STL generation.
    """

    template_vertices: np.ndarray
    triangle_faces: np.ndarray

    identity_shape_directions: np.ndarray
    expression_shape_directions: np.ndarray
    pose_directions: np.ndarray

    joint_regressor: np.ndarray
    skinning_weights: np.ndarray
    kinematic_tree: np.ndarray

    metadata: Mapping[str, Any]

    SKINNING_WEIGHT_SUM_TOLERANCE = 1.0e-12

    def __post_init__(self) -> None:
        template_vertices = self._normalize_template_vertices(
            self.template_vertices,
        )

        vertex_count = int(
            template_vertices.shape[0],
        )

        triangle_faces = self._normalize_triangle_faces(
            self.triangle_faces,
            vertex_count=vertex_count,
        )

        identity_shape_directions = (
            self._normalize_direction_tensor(
                self.identity_shape_directions,
                name="identity_shape_directions",
                vertex_count=vertex_count,
            )
        )

        expression_shape_directions = (
            self._normalize_direction_tensor(
                self.expression_shape_directions,
                name="expression_shape_directions",
                vertex_count=vertex_count,
            )
        )

        pose_directions = self._normalize_direction_tensor(
            self.pose_directions,
            name="pose_directions",
            vertex_count=vertex_count,
        )

        joint_regressor = self._normalize_joint_regressor(
            self.joint_regressor,
            vertex_count=vertex_count,
        )

        joint_count = int(
            joint_regressor.shape[0],
        )

        skinning_weights = self._normalize_skinning_weights(
            self.skinning_weights,
            vertex_count=vertex_count,
            joint_count=joint_count,
        )

        kinematic_tree = self._normalize_kinematic_tree(
            self.kinematic_tree,
            joint_count=joint_count,
        )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        for array in (
            template_vertices,
            triangle_faces,
            identity_shape_directions,
            expression_shape_directions,
            pose_directions,
            joint_regressor,
            skinning_weights,
            kinematic_tree,
        ):
            array.setflags(
                write=False,
            )

        object.__setattr__(
            self,
            "template_vertices",
            template_vertices,
        )
        object.__setattr__(
            self,
            "triangle_faces",
            triangle_faces,
        )
        object.__setattr__(
            self,
            "identity_shape_directions",
            identity_shape_directions,
        )
        object.__setattr__(
            self,
            "expression_shape_directions",
            expression_shape_directions,
        )
        object.__setattr__(
            self,
            "pose_directions",
            pose_directions,
        )
        object.__setattr__(
            self,
            "joint_regressor",
            joint_regressor,
        )
        object.__setattr__(
            self,
            "skinning_weights",
            skinning_weights,
        )
        object.__setattr__(
            self,
            "kinematic_tree",
            kinematic_tree,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def vertex_count(
        self,
    ) -> int:
        return int(
            self.template_vertices.shape[0],
        )

    @property
    def triangle_count(
        self,
    ) -> int:
        return int(
            self.triangle_faces.shape[0],
        )

    @property
    def identity_parameter_count(
        self,
    ) -> int:
        return int(
            self.identity_shape_directions.shape[2],
        )

    @property
    def expression_parameter_count(
        self,
    ) -> int:
        return int(
            self.expression_shape_directions.shape[2],
        )

    @property
    def pose_parameter_count(
        self,
    ) -> int:
        return int(
            self.pose_directions.shape[2],
        )

    @property
    def joint_count(
        self,
    ) -> int:
        return int(
            self.joint_regressor.shape[0],
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,
            "identity_parameter_count": (
                self.identity_parameter_count
            ),
            "expression_parameter_count": (
                self.expression_parameter_count
            ),
            "pose_parameter_count": (
                self.pose_parameter_count
            ),
            "joint_count": self.joint_count,
            "template_vertices": (
                self.template_vertices.tolist()
            ),
            "triangle_faces": (
                self.triangle_faces.tolist()
            ),
            "identity_shape_directions": (
                self.identity_shape_directions.tolist()
            ),
            "expression_shape_directions": (
                self.expression_shape_directions.tolist()
            ),
            "pose_directions": (
                self.pose_directions.tolist()
            ),
            "joint_regressor": (
                self.joint_regressor.tolist()
            ),
            "skinning_weights": (
                self.skinning_weights.tolist()
            ),
            "kinematic_tree": (
                self.kinematic_tree.tolist()
            ),
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_template_vertices(
        value: Any,
    ) -> np.ndarray:
        vertices = (
            AtlasPortraitFlameCanonicalModel
            ._normalize_float_array(
                value,
                name="template_vertices",
            )
        )

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 3
            or vertices.shape[0] < 3
        ):
            raise ValueError(
                "template_vertices must have shape "
                "(N, 3) and contain at least three "
                "vertices."
            )

        return vertices

    @staticmethod
    def _normalize_triangle_faces(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        faces = (
            AtlasPortraitFlameCanonicalModel
            ._normalize_integer_array(
                value,
                name="triangle_faces",
            )
        )

        if (
            faces.ndim != 2
            or faces.shape[1] != 3
            or faces.shape[0] < 1
        ):
            raise ValueError(
                "triangle_faces must have shape (M, 3) "
                "and must not be empty."
            )

        if (
            np.any(
                faces < 0,
            )
            or np.any(
                faces >= vertex_count,
            )
        ):
            raise ValueError(
                "triangle_faces contains indices outside "
                "the template vertex range."
            )

        sorted_faces = np.sort(
            faces,
            axis=1,
        )

        if (
            np.any(
                sorted_faces[:, 0]
                == sorted_faces[:, 1]
            )
            or np.any(
                sorted_faces[:, 1]
                == sorted_faces[:, 2]
            )
        ):
            raise ValueError(
                "triangle_faces contains a degenerate "
                "triangle."
            )

        return faces

    @staticmethod
    def _normalize_direction_tensor(
        value: Any,
        *,
        name: str,
        vertex_count: int,
    ) -> np.ndarray:
        directions = (
            AtlasPortraitFlameCanonicalModel
            ._normalize_float_array(
                value,
                name=name,
            )
        )

        if (
            directions.ndim != 3
            or directions.shape[0] != vertex_count
            or directions.shape[1] != 3
            or directions.shape[2] < 1
        ):
            raise ValueError(
                f"{name} must have shape "
                f"({vertex_count}, 3, P) with P >= 1."
            )

        return directions

    @staticmethod
    def _normalize_joint_regressor(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        regressor = (
            AtlasPortraitFlameCanonicalModel
            ._normalize_float_array(
                value,
                name="joint_regressor",
            )
        )

        if (
            regressor.ndim != 2
            or regressor.shape[0] < 1
            or regressor.shape[1] != vertex_count
        ):
            raise ValueError(
                "joint_regressor must have shape "
                f"(J, {vertex_count}) with J >= 1."
            )

        return regressor

    @classmethod
    def _normalize_skinning_weights(
        cls,
        value: Any,
        *,
        vertex_count: int,
        joint_count: int,
    ) -> np.ndarray:
        weights = cls._normalize_float_array(
            value,
            name="skinning_weights",
        )

        if weights.shape != (
            vertex_count,
            joint_count,
        ):
            raise ValueError(
                "skinning_weights must have shape "
                f"({vertex_count}, {joint_count})."
            )

        if np.any(
            weights < 0.0,
        ):
            raise ValueError(
                "skinning_weights must not contain "
                "negative values."
            )

        row_sums = np.sum(
            weights,
            axis=1,
            dtype=np.float64,
        )

        if not np.allclose(
            row_sums,
            1.0,
            rtol=0.0,
            atol=cls.SKINNING_WEIGHT_SUM_TOLERANCE,
        ):
            raise ValueError(
                "skinning_weights rows must sum to 1.0."
            )

        return weights

    @staticmethod
    def _normalize_kinematic_tree(
        value: Any,
        *,
        joint_count: int,
    ) -> np.ndarray:
        tree = (
            AtlasPortraitFlameCanonicalModel
            ._normalize_integer_array(
                value,
                name="kinematic_tree",
            )
        )

        if tree.shape != (
            joint_count,
        ):
            raise ValueError(
                "kinematic_tree must have shape "
                f"({joint_count},)."
            )

        if tree[
            0
        ] != -1:
            raise ValueError(
                "kinematic_tree root parent must be -1."
            )

        for joint_index in range(
            1,
            joint_count,
        ):
            parent_index = int(
                tree[
                    joint_index
                ]
            )

            if (
                parent_index < 0
                or parent_index >= joint_index
            ):
                raise ValueError(
                    "kinematic_tree parent indices must "
                    "reference an earlier joint."
                )

        return tree

    @staticmethod
    def _normalize_float_array(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            array = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not np.isfinite(
            array,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return array.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_integer_array(
        value: Any,
        *,
        name: str,
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
                f"{name} must be numeric."
            ) from exc

        if not np.isfinite(
            numeric,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        if not np.equal(
            numeric,
            np.rint(
                numeric,
            ),
        ).all():
            raise ValueError(
                f"{name} must contain integer values."
            )

        return numeric.astype(
            np.int64,
            copy=True,
        )

    @staticmethod
    def _normalize_metadata(
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        copied = {
            str(
                key,
            ): item
            for key, item in value.items()
        }

        return MappingProxyType(
            {
                key: copied[key]
                for key in sorted(
                    copied,
                )
            }
        )
