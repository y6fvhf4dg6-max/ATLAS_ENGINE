from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


class AtlasPortraitFlameKinematicTransformEvaluator:
    """
    Evaluates rest-pose-corrected FLAME joint transforms.

    Each joint receives an axis-angle rotation. Local transforms
    are accumulated through the model kinematic tree and then
    corrected by the corresponding rest-pose joint position.

    The returned transforms are suitable for a subsequent linear
    blend skinning stage.

    This evaluator performs no skinning-weight application,
    vertex deformation, fitting, rendering, or STL generation.
    """

    _SMALL_ANGLE_THRESHOLD = 1.0e-12

    @classmethod
    def evaluate(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        joint_positions: Any,
        pose_parameters: Any,
    ) -> np.ndarray:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        joint_count = model.joint_count

        normalized_joint_positions = cls._normalize_joint_positions(
            joint_positions,
            expected_joint_count=joint_count,
        )
        normalized_pose_parameters = cls._normalize_pose_parameters(
            pose_parameters,
            expected_parameter_count=model.pose_parameter_count,
        )

        expected_kinematic_parameter_count = joint_count * 3

        if model.pose_parameter_count != expected_kinematic_parameter_count:
            raise ValueError(
                "model pose_parameter_count must equal "
                "joint_count * 3 for kinematic evaluation."
            )

        rotation_vectors = normalized_pose_parameters.reshape(
            joint_count,
            3,
        )
        rotation_matrices = np.stack(
            [
                cls._axis_angle_to_rotation_matrix(
                    rotation_vector,
                )
                for rotation_vector in rotation_vectors
            ],
            axis=0,
        )

        global_transforms = np.empty(
            (
                joint_count,
                4,
                4,
            ),
            dtype=np.float64,
        )

        for joint_index in range(
            joint_count,
        ):
            parent_index = int(
                model.kinematic_tree[
                    joint_index
                ]
            )

            if parent_index == -1:
                local_translation = normalized_joint_positions[
                    joint_index
                ]
            else:
                local_translation = (
                    normalized_joint_positions[
                        joint_index
                    ]
                    - normalized_joint_positions[
                        parent_index
                    ]
                )

            local_transform = np.eye(
                4,
                dtype=np.float64,
            )
            local_transform[
                :3,
                :3,
            ] = rotation_matrices[
                joint_index
            ]
            local_transform[
                :3,
                3,
            ] = local_translation

            if parent_index == -1:
                global_transforms[
                    joint_index
                ] = local_transform
            else:
                global_transforms[
                    joint_index
                ] = (
                    global_transforms[
                        parent_index
                    ]
                    @ local_transform
                )

        corrected_transforms = np.empty_like(
            global_transforms,
        )

        for joint_index in range(
            joint_count,
        ):
            rest_inverse = np.eye(
                4,
                dtype=np.float64,
            )
            rest_inverse[
                :3,
                3,
            ] = -normalized_joint_positions[
                joint_index
            ]

            corrected_transforms[
                joint_index
            ] = (
                global_transforms[
                    joint_index
                ]
                @ rest_inverse
            )

        result = np.asarray(
            corrected_transforms,
            dtype=np.float64,
        ).copy()

        result.setflags(
            write=False,
        )

        return result

    @staticmethod
    def _normalize_joint_positions(
        value: Any,
        *,
        expected_joint_count: int,
    ) -> np.ndarray:
        try:
            joint_positions = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "joint_positions must be numeric."
            ) from exc

        expected_shape = (
            expected_joint_count,
            3,
        )

        if joint_positions.shape != expected_shape:
            raise ValueError(
                "joint_positions must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            joint_positions,
        ).all():
            raise ValueError(
                "joint_positions contains non-finite values."
            )

        return joint_positions.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_pose_parameters(
        value: Any,
        *,
        expected_parameter_count: int,
    ) -> np.ndarray:
        try:
            pose_parameters = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "pose_parameters must be numeric."
            ) from exc

        expected_shape = (
            expected_parameter_count,
        )

        if pose_parameters.shape != expected_shape:
            raise ValueError(
                "pose_parameters must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            pose_parameters,
        ).all():
            raise ValueError(
                "pose_parameters contains non-finite values."
            )

        return pose_parameters.astype(
            np.float64,
            copy=True,
        )

    @classmethod
    def _axis_angle_to_rotation_matrix(
        cls,
        rotation_vector: np.ndarray,
    ) -> np.ndarray:
        angle = float(
            np.linalg.norm(
                rotation_vector,
            )
        )

        if angle <= cls._SMALL_ANGLE_THRESHOLD:
            return np.eye(
                3,
                dtype=np.float64,
            )

        axis = rotation_vector / angle

        skew_symmetric = np.array(
            [
                [
                    0.0,
                    -axis[2],
                    axis[1],
                ],
                [
                    axis[2],
                    0.0,
                    -axis[0],
                ],
                [
                    -axis[1],
                    axis[0],
                    0.0,
                ],
            ],
            dtype=np.float64,
        )

        identity = np.eye(
            3,
            dtype=np.float64,
        )

        return (
            identity
            + np.sin(angle) * skew_symmetric
            + (
                1.0
                - np.cos(angle)
            )
            * (
                skew_symmetric
                @ skew_symmetric
            )
        )
