from __future__ import annotations

import numpy as np

from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


class AtlasParametricFaceDepthDeformer:
    """
    Applies anatomical depth deformation to a
    parametric face surface.

    Anatomical components modify Z only. X and Y
    coordinates are preserved exactly.

    The deformer never mutates the source surface.
    """

    NOSE_TIP_CENTER_X = 0.00
    NOSE_TIP_CENTER_Y = -0.12
    NOSE_TIP_RADIUS_X = 0.30
    NOSE_TIP_RADIUS_Y = 0.32

    NOSE_BRIDGE_CENTER_X = 0.00
    NOSE_BRIDGE_CENTER_Y = 0.08
    NOSE_BRIDGE_RADIUS_X = 0.22
    NOSE_BRIDGE_RADIUS_Y = 0.55

    EYE_SOCKET_CENTER_X = 0.36
    EYE_SOCKET_CENTER_Y = 0.22
    EYE_SOCKET_SCALE_X = 0.36
    EYE_SOCKET_SCALE_Y = 0.24

    @classmethod
    def deform(
        cls,
        surface: AtlasParametricFaceSurface,
        *,
        depth_profile: AtlasParametricFaceDepthProfile,
    ) -> AtlasParametricFaceSurface:
        if not isinstance(
            surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        if not isinstance(
            depth_profile,
            AtlasParametricFaceDepthProfile,
        ):
            raise TypeError(
                "depth_profile must be an "
                "AtlasParametricFaceDepthProfile instance."
            )

        source_x = np.asarray(
            surface.x_coordinates,
            dtype=np.float64,
        )
        source_y = np.asarray(
            surface.y_coordinates,
            dtype=np.float64,
        )
        source_z = np.asarray(
            surface.z_coordinates,
            dtype=np.float64,
        )

        nose_tip_delta = cls._build_compact_projection(
            x_coordinates=source_x,
            y_coordinates=source_y,
            center_x=cls.NOSE_TIP_CENTER_X,
            center_y=cls.NOSE_TIP_CENTER_Y,
            radius_x=cls.NOSE_TIP_RADIUS_X,
            radius_y=cls.NOSE_TIP_RADIUS_Y,
            projection=depth_profile.nose_tip_projection,
        )

        nose_bridge_delta = cls._build_compact_projection(
            x_coordinates=source_x,
            y_coordinates=source_y,
            center_x=cls.NOSE_BRIDGE_CENTER_X,
            center_y=cls.NOSE_BRIDGE_CENTER_Y,
            radius_x=cls.NOSE_BRIDGE_RADIUS_X,
            radius_y=cls.NOSE_BRIDGE_RADIUS_Y,
            projection=depth_profile.nose_bridge_projection,
        )

        eye_socket_delta = cls._build_eye_socket_delta(
            x_coordinates=source_x,
            y_coordinates=source_y,
            depth=depth_profile.eye_socket_depth,
        )

        deformed_z = (
            source_z
            + nose_tip_delta
            + nose_bridge_delta
            + eye_socket_delta
        )

        return AtlasParametricFaceSurface(
            x_coordinates=source_x.copy(),
            y_coordinates=source_y.copy(),
            z_coordinates=deformed_z,
        )

    @classmethod
    def _build_nose_tip_delta(
        cls,
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
        projection: float,
    ) -> np.ndarray:
        return cls._build_compact_projection(
            x_coordinates=x_coordinates,
            y_coordinates=y_coordinates,
            center_x=cls.NOSE_TIP_CENTER_X,
            center_y=cls.NOSE_TIP_CENTER_Y,
            radius_x=cls.NOSE_TIP_RADIUS_X,
            radius_y=cls.NOSE_TIP_RADIUS_Y,
            projection=projection,
        )

    @classmethod
    def _build_eye_socket_delta(
        cls,
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
        depth: float,
    ) -> np.ndarray:
        if depth == 0.0:
            return np.zeros_like(
                x_coordinates,
                dtype=np.float64,
            )

        left_radius = np.sqrt(
            (
                (
                    x_coordinates
                    + cls.EYE_SOCKET_CENTER_X
                )
                / cls.EYE_SOCKET_SCALE_X
            )
            ** 2
            + (
                (
                    y_coordinates
                    - cls.EYE_SOCKET_CENTER_Y
                )
                / cls.EYE_SOCKET_SCALE_Y
            )
            ** 2
        )

        right_radius = np.sqrt(
            (
                (
                    x_coordinates
                    - cls.EYE_SOCKET_CENTER_X
                )
                / cls.EYE_SOCKET_SCALE_X
            )
            ** 2
            + (
                (
                    y_coordinates
                    - cls.EYE_SOCKET_CENTER_Y
                )
                / cls.EYE_SOCKET_SCALE_Y
            )
            ** 2
        )

        nearest_radius = np.minimum(
            left_radius,
            right_radius,
        )

        gaussian_weight = np.exp(
            -nearest_radius
            * nearest_radius
        )

        outer_transition = np.clip(
            (
                nearest_radius
                - 1.00
            )
            / 0.65,
            0.0,
            1.0,
        )

        outer_transition_squared = (
            outer_transition
            * outer_transition
        )
        outer_transition_cubed = (
            outer_transition_squared
            * outer_transition
        )

        outer_smootherstep = (
            outer_transition_cubed
            * (
                10.0
                - 15.0
                * outer_transition
                + 6.0
                * outer_transition_squared
            )
        )

        outer_weight = (
            1.0
            - outer_smootherstep
        )

        absolute_x = np.abs(
            x_coordinates,
        )

        nasal_transition = np.clip(
            (
                absolute_x
                - 0.12
            )
            / 0.18,
            0.0,
            1.0,
        )

        nasal_transition_squared = (
            nasal_transition
            * nasal_transition
        )
        nasal_transition_cubed = (
            nasal_transition_squared
            * nasal_transition
        )

        nasal_weight = (
            nasal_transition_cubed
            * (
                10.0
                - 15.0
                * nasal_transition
                + 6.0
                * nasal_transition_squared
            )
        )

        combined_weight = (
            gaussian_weight
            * outer_weight
            * nasal_weight
        )

        return (
            -float(
                depth,
            )
            * combined_weight
        ).astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _build_gaussian_projection(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
        center_x: float,
        center_y: float,
        scale_x: float,
        scale_y: float,
        projection: float,
    ) -> np.ndarray:
        if projection == 0.0:
            return np.zeros_like(
                x_coordinates,
                dtype=np.float64,
            )

        normalized_radius_squared = (
            (
                (
                    x_coordinates
                    - center_x
                )
                / scale_x
            )
            ** 2
            + (
                (
                    y_coordinates
                    - center_y
                )
                / scale_y
            )
            ** 2
        )

        return (
            float(
                projection,
            )
            * np.exp(
                -normalized_radius_squared
            )
        ).astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _build_compact_projection(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
        center_x: float,
        center_y: float,
        radius_x: float,
        radius_y: float,
        projection: float,
    ) -> np.ndarray:
        if projection == 0.0:
            return np.zeros_like(
                x_coordinates,
                dtype=np.float64,
            )

        normalized_radius_squared = (
            (
                (
                    x_coordinates
                    - center_x
                )
                / radius_x
            )
            ** 2
            + (
                (
                    y_coordinates
                    - center_y
                )
                / radius_y
            )
            ** 2
        )

        compact_support = np.clip(
            1.0
            - normalized_radius_squared,
            0.0,
            1.0,
        )

        smooth_weight = (
            compact_support
            * compact_support
            * (
                3.0
                - 2.0
                * compact_support
            )
        )

        return (
            float(
                projection,
            )
            * smooth_weight
        ).astype(
            np.float64,
            copy=False,
        )
