from __future__ import annotations

import numpy as np

from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)


class AtlasPortraitFlamePoseFeatureEvaluator:
    """
    Converts FLAME axis-angle pose parameters into pose features.

    Processing:
    - split the pose vector into three-component axis-angle
      rotations
    - convert each rotation to a 3x3 matrix with Rodrigues'
      formula
    - exclude the root joint rotation
    - subtract the identity matrix from each non-root
      rotation
    - flatten the residual matrices in joint order

    It performs no pose corrective vertex deformation,
    joint regression, kinematic transformation, linear
    blend skinning, fitting, rendering, or STL generation.
    """

    MINIMUM_JOINT_COUNT = 2
    AXIS_ANGLE_COMPONENT_COUNT = 3
    SMALL_ANGLE_THRESHOLD = 1.0e-8

    @classmethod
    def evaluate(
        cls,
        parameters: AtlasPortraitFlameFittingParameters,
    ) -> np.ndarray:
        if not isinstance(
            parameters,
            AtlasPortraitFlameFittingParameters,
        ):
            raise TypeError(
                "parameters must be an "
                "AtlasPortraitFlameFittingParameters "
                "instance."
            )

        cls._validate_pose_parameter_layout(
            parameters.pose_parameter_count,
        )

        axis_angles = parameters.pose_parameters.reshape(
            -1,
            cls.AXIS_ANGLE_COMPONENT_COUNT,
        )

        rotation_matrices = np.stack(
            [
                cls._axis_angle_to_rotation_matrix(
                    axis_angle,
                )
                for axis_angle in axis_angles
            ],
            axis=0,
        )

        identity = np.eye(
            3,
            dtype=np.float64,
        )

        pose_features = np.asarray(
            rotation_matrices[
                1:
            ]
            - identity,
            dtype=np.float64,
        ).reshape(
            -1,
        ).copy()

        pose_features.setflags(
            write=False,
        )

        return pose_features

    @classmethod
    def _validate_pose_parameter_layout(
        cls,
        pose_parameter_count: int,
    ) -> None:
        minimum_parameter_count = (
            cls.MINIMUM_JOINT_COUNT
            * cls.AXIS_ANGLE_COMPONENT_COUNT
        )

        if (
            pose_parameter_count < minimum_parameter_count
            or (
                pose_parameter_count
                % cls.AXIS_ANGLE_COMPONENT_COUNT
            )
            != 0
        ):
            raise ValueError(
                "pose parameter count must represent at "
                "least two three-component axis-angle "
                "joint rotations."
            )

    @classmethod
    def _axis_angle_to_rotation_matrix(
        cls,
        axis_angle: np.ndarray,
    ) -> np.ndarray:
        vector = np.asarray(
            axis_angle,
            dtype=np.float64,
        )

        angle_squared = float(
            np.dot(
                vector,
                vector,
            )
        )

        skew = np.array(
            [
                [
                    0.0,
                    -vector[2],
                    vector[1],
                ],
                [
                    vector[2],
                    0.0,
                    -vector[0],
                ],
                [
                    -vector[1],
                    vector[0],
                    0.0,
                ],
            ],
            dtype=np.float64,
        )

        if (
            angle_squared
            < cls.SMALL_ANGLE_THRESHOLD
            * cls.SMALL_ANGLE_THRESHOLD
        ):
            sine_over_angle = (
                1.0
                - angle_squared / 6.0
                + angle_squared
                * angle_squared
                / 120.0
            )

            one_minus_cosine_over_angle_squared = (
                0.5
                - angle_squared / 24.0
                + angle_squared
                * angle_squared
                / 720.0
            )
        else:
            angle = float(
                np.sqrt(
                    angle_squared,
                )
            )

            sine_over_angle = (
                np.sin(
                    angle,
                )
                / angle
            )

            one_minus_cosine_over_angle_squared = (
                (
                    1.0
                    - np.cos(
                        angle,
                    )
                )
                / angle_squared
            )

        return (
            np.eye(
                3,
                dtype=np.float64,
            )
            + sine_over_angle
            * skew
            + one_minus_cosine_over_angle_squared
            * (
                skew
                @ skew
            )
        )
