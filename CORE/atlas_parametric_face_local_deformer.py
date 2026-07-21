from __future__ import annotations

import numpy as np

from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


class AtlasParametricFaceLocalDeformer:
    """
    Applies local anatomical coordinate deformation.

    Current scope:
    - eye spacing
    - eye height
    - nose width
    - nose length
    - mouth width
    - jaw width
    - chin width
    - chin length
    - forehead height

    Deformation uses smooth regional influence masks so
    distant facial regions remain unchanged.

    It performs no global scaling, rotation, translation,
    projection, rendering, triangulation, or mesh
    generation.
    """

    EYE_CENTER_Y = 0.22
    NOSE_CENTER_Y = 0.05
    MOUTH_CENTER_Y = -0.38
    CHIN_LENGTH_ANCHOR_Y = -0.50
    FOREHEAD_HEIGHT_ANCHOR_Y = 0.20

    @classmethod
    def deform(
        cls,
        surface: AtlasParametricFaceSurface,
        *,
        parameters: AtlasParametricFaceParameters,
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
            parameters,
            AtlasParametricFaceParameters,
        ):
            raise TypeError(
                "parameters must be an "
                "AtlasParametricFaceParameters instance."
            )

        source_x = surface.x_coordinates
        source_y = surface.y_coordinates
        source_z = surface.z_coordinates

        nose_width_mask = cls._nose_width_mask(
            x_coordinates=source_x,
            y_coordinates=source_y,
        )
        nose_length_mask = cls._nose_length_mask(
            x_coordinates=source_x,
            y_coordinates=source_y,
        )
        eye_mask = cls._eye_mask(
            x_coordinates=source_x,
            y_coordinates=source_y,
        )
        chin_width_mask = cls._chin_width_mask(
            x_coordinates=source_x,
            y_coordinates=source_y,
        )
        chin_length_mask = cls._chin_length_mask(
            x_coordinates=source_x,
            y_coordinates=source_y,
        )
        forehead_height_mask = cls._forehead_height_mask(
            x_coordinates=source_x,
            y_coordinates=source_y,
        )

        nose_width_factor = (
            1.0
            + (
                parameters.nose_width
                - 1.0
            )
            * nose_width_mask
        )

        nose_length_factor = (
            1.0
            + (
                parameters.nose_length
                - 1.0
            )
            * nose_length_mask
        )

        eye_height_factor = (
            1.0
            + (
                parameters.eye_height
                - 1.0
            )
            * eye_mask
        )

        chin_width_factor = (
            1.0
            + (
                parameters.chin_width
                - 1.0
            )
            * chin_width_mask
        )

        chin_length_factor = (
            1.0
            + (
                parameters.chin_length
                - 1.0
            )
            * chin_length_mask
        )

        forehead_height_factor = (
            1.0
            + (
                parameters.forehead_height
                - 1.0
            )
            * forehead_height_mask
        )

        nose_deformed_x = (
            source_x
            * nose_width_factor
        )

        nose_deformed_y = (
            cls.NOSE_CENTER_Y
            + (
                source_y
                - cls.NOSE_CENTER_Y
            )
            * nose_length_factor
        )

        pre_mouth_deformed_x = (
            nose_deformed_x
            * chin_width_factor
        )

        mouth_deformed_x = cls._deform_mouth_width(
            x_coordinates=pre_mouth_deformed_x,
            source_x_coordinates=source_x,
            source_y_coordinates=source_y,
            mouth_width=parameters.mouth_width,
        )

        eye_deformed_x = cls._deform_eye_spacing(
            x_coordinates=mouth_deformed_x,
            source_x_coordinates=source_x,
            source_y_coordinates=source_y,
            eye_spacing=parameters.eye_spacing,
        )

        deformed_x = cls._deform_jaw_width(
            x_coordinates=eye_deformed_x,
            source_x_coordinates=source_x,
            source_y_coordinates=source_y,
            jaw_width=parameters.jaw_width,
        )

        eye_y_offset = (
            source_y
            - cls.EYE_CENTER_Y
        )

        eye_deformed_y = (
            nose_deformed_y
            + eye_y_offset
            * (
                eye_height_factor
                - 1.0
            )
        )

        chin_y_offset = (
            source_y
            - cls.CHIN_LENGTH_ANCHOR_Y
        )

        chin_deformed_y = (
            eye_deformed_y
            + chin_y_offset
            * (
                chin_length_factor
                - 1.0
            )
        )

        forehead_y_offset = (
            source_y
            - cls.FOREHEAD_HEIGHT_ANCHOR_Y
        )

        deformed_y = (
            chin_deformed_y
            + forehead_y_offset
            * (
                forehead_height_factor
                - 1.0
            )
        )

        return AtlasParametricFaceSurface(
            x_coordinates=np.asarray(
                deformed_x,
                dtype=np.float64,
            ),
            y_coordinates=np.asarray(
                deformed_y,
                dtype=np.float64,
            ),
            z_coordinates=np.asarray(
                source_z,
                dtype=np.float64,
            ),
        )

    @staticmethod
    def _deform_eye_spacing(
        *,
        x_coordinates: np.ndarray,
        source_x_coordinates: np.ndarray,
        source_y_coordinates: np.ndarray,
        eye_spacing: float,
    ) -> np.ndarray:
        eye_anchor_x = 0.36
        protected_boundary_x = 0.75

        vertical_weight = np.exp(
            -(
                (
                    (
                        source_y_coordinates
                        - AtlasParametricFaceLocalDeformer.EYE_CENTER_Y
                    )
                    / 0.20
                )
                ** 2
            )
        )

        lower_transition = np.clip(
            (
                source_y_coordinates
                - (-0.20)
            )
            / 0.20,
            0.0,
            1.0,
        )

        lower_transition = (
            lower_transition
            * lower_transition
            * (
                3.0
                - 2.0
                * lower_transition
            )
        )

        vertical_weight = (
            vertical_weight
            * lower_transition
        )

        protected_region = (
            (source_y_coordinates <= -0.20)
            | (
                np.abs(
                    source_x_coordinates,
                )
                >= protected_boundary_x
            )
        )

        vertical_weight = np.where(
            protected_region,
            0.0,
            vertical_weight,
        )

        effective_factor = (
            1.0
            + (
                eye_spacing
                - 1.0
            )
            * vertical_weight
        )

        expanded_anchor = (
            protected_boundary_x
            - (
                protected_boundary_x
                - eye_anchor_x
            )
            / effective_factor
        )

        compressed_anchor = (
            eye_anchor_x
            * effective_factor
        )

        target_anchor = np.where(
            effective_factor >= 1.0,
            expanded_anchor,
            compressed_anchor,
        )

        current_absolute_x = np.abs(
            x_coordinates,
        )

        inner_scale = (
            target_anchor
            / eye_anchor_x
        )

        outer_scale = (
            (
                protected_boundary_x
                - target_anchor
            )
            / (
                protected_boundary_x
                - eye_anchor_x
            )
        )

        mapped_inner_x = (
            current_absolute_x
            * inner_scale
        )

        mapped_outer_x = (
            target_anchor
            + (
                current_absolute_x
                - eye_anchor_x
            )
            * outer_scale
        )

        transition_half_width = 0.12
        transition_start = (
            eye_anchor_x
            - transition_half_width
        )
        transition_end = (
            eye_anchor_x
            + transition_half_width
        )
        transition_width = (
            transition_end
            - transition_start
        )

        transition_t = np.clip(
            (
                current_absolute_x
                - transition_start
            )
            / transition_width,
            0.0,
            1.0,
        )

        transition_start_value = (
            transition_start
            * inner_scale
        )

        transition_end_value = (
            target_anchor
            + (
                transition_end
                - eye_anchor_x
            )
            * outer_scale
        )

        hermite_h00 = (
            2.0
            * transition_t
            * transition_t
            * transition_t
            - 3.0
            * transition_t
            * transition_t
            + 1.0
        )

        hermite_h10 = (
            transition_t
            * transition_t
            * transition_t
            - 2.0
            * transition_t
            * transition_t
            + transition_t
        )

        hermite_h01 = (
            -2.0
            * transition_t
            * transition_t
            * transition_t
            + 3.0
            * transition_t
            * transition_t
        )

        hermite_h11 = (
            transition_t
            * transition_t
            * transition_t
            - transition_t
            * transition_t
        )

        mapped_transition_x = (
            hermite_h00
            * transition_start_value
            + hermite_h10
            * transition_width
            * inner_scale
            + hermite_h01
            * transition_end_value
            + hermite_h11
            * transition_width
            * outer_scale
        )

        mapped_absolute_x = np.where(
            current_absolute_x
            <= transition_start,
            mapped_inner_x,
            np.where(
                current_absolute_x
                >= transition_end,
                mapped_outer_x,
                mapped_transition_x,
            ),
        )

        outer_transition_width = 0.24
        outer_transition_start = (
            protected_boundary_x
            - outer_transition_width
        )

        outer_transition_t = np.clip(
            (
                current_absolute_x
                - outer_transition_start
            )
            / outer_transition_width,
            0.0,
            1.0,
        )

        outer_start_value = (
            target_anchor
            + (
                outer_transition_start
                - eye_anchor_x
            )
            * outer_scale
        )

        outer_h00 = (
            2.0
            * outer_transition_t
            * outer_transition_t
            * outer_transition_t
            - 3.0
            * outer_transition_t
            * outer_transition_t
            + 1.0
        )

        outer_h10 = (
            outer_transition_t
            * outer_transition_t
            * outer_transition_t
            - 2.0
            * outer_transition_t
            * outer_transition_t
            + outer_transition_t
        )

        outer_h01 = (
            -2.0
            * outer_transition_t
            * outer_transition_t
            * outer_transition_t
            + 3.0
            * outer_transition_t
            * outer_transition_t
        )

        outer_h11 = (
            outer_transition_t
            * outer_transition_t
            * outer_transition_t
            - outer_transition_t
            * outer_transition_t
        )

        mapped_outer_transition_x = (
            outer_h00
            * outer_start_value
            + outer_h10
            * outer_transition_width
            * outer_scale
            + outer_h01
            * protected_boundary_x
            + outer_h11
            * outer_transition_width
        )

        mapped_absolute_x = np.where(
            (
                current_absolute_x
                > outer_transition_start
            )
            & (
                current_absolute_x
                < protected_boundary_x
            ),
            mapped_outer_transition_x,
            mapped_absolute_x,
        )

        mapped_absolute_x = np.where(
            current_absolute_x
            >= protected_boundary_x,
            current_absolute_x,
            mapped_absolute_x,
        )

        mapped_current_x = np.copysign(
            mapped_absolute_x,
            x_coordinates,
        )

        result = np.where(
            protected_region,
            x_coordinates,
            mapped_current_x,
        )

        return result.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _eye_mask(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
    ) -> np.ndarray:
        horizontal_distance = (
            np.abs(
                x_coordinates,
            )
            - 0.36
        )

        mask = np.exp(
            -(
                (
                    horizontal_distance
                    / 0.22
                )
                ** 2
                + (
                    (
                        y_coordinates
                        - 0.22
                    )
                    / 0.20
                )
                ** 2
            )
        )

        protected_region = (
            (y_coordinates <= -0.20)
            | (
                np.abs(
                    x_coordinates,
                )
                >= 0.75
            )
        )

        mask = np.where(
            protected_region,
            0.0,
            mask,
        )

        return mask.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _deform_mouth_width(
        *,
        x_coordinates: np.ndarray,
        source_x_coordinates: np.ndarray,
        source_y_coordinates: np.ndarray,
        mouth_width: float,
    ) -> np.ndarray:
        mouth_anchor_x = 0.38
        protected_boundary_x = 0.75

        vertical_weight = np.exp(
            -(
                (
                    (
                        source_y_coordinates
                        - AtlasParametricFaceLocalDeformer.MOUTH_CENTER_Y
                    )
                    / 0.18
                )
                ** 2
            )
        )

        lower_transition = np.clip(
            (
                source_y_coordinates
                - (-0.72)
            )
            / 0.30,
            0.0,
            1.0,
        )

        lower_transition_squared = (
            lower_transition
            * lower_transition
        )
        lower_transition_cubed = (
            lower_transition_squared
            * lower_transition
        )

        lower_transition = (
            lower_transition_cubed
            * (
                10.0
                - 15.0
                * lower_transition
                + 6.0
                * lower_transition_squared
            )
        )

        upper_transition = np.clip(
            (
                0.0
                - source_y_coordinates
            )
            / 0.22,
            0.0,
            1.0,
        )

        upper_transition_squared = (
            upper_transition
            * upper_transition
        )
        upper_transition_cubed = (
            upper_transition_squared
            * upper_transition
        )

        upper_transition = (
            upper_transition_cubed
            * (
                10.0
                - 15.0
                * upper_transition
                + 6.0
                * upper_transition_squared
            )
        )

        vertical_weight = (
            vertical_weight
            * lower_transition
            * upper_transition
        )

        protected_region = (
            (source_y_coordinates >= 0.0)
            | (source_y_coordinates <= -0.72)
            | (
                np.abs(
                    source_x_coordinates,
                )
                >= protected_boundary_x
            )
        )

        vertical_weight = np.where(
            protected_region,
            0.0,
            vertical_weight,
        )

        effective_factor = (
            1.0
            + (
                mouth_width
                - 1.0
            )
            * vertical_weight
        )

        expanded_anchor = (
            protected_boundary_x
            - (
                protected_boundary_x
                - mouth_anchor_x
            )
            / effective_factor
        )

        compressed_anchor = (
            mouth_anchor_x
            * effective_factor
        )

        target_anchor = np.where(
            effective_factor >= 1.0,
            expanded_anchor,
            compressed_anchor,
        )

        source_absolute_x = np.abs(
            source_x_coordinates,
        )

        anchor_displacement = (
            target_anchor
            - mouth_anchor_x
        )

        inner_t = np.clip(
            source_absolute_x
            / mouth_anchor_x,
            0.0,
            1.0,
        )

        inner_t_squared = (
            inner_t
            * inner_t
        )
        inner_t_cubed = (
            inner_t_squared
            * inner_t
        )

        inner_basis = (
            inner_t_cubed
            * (
                10.0
                - 15.0
                * inner_t
                + 6.0
                * inner_t_squared
            )
        )

        outer_t = np.clip(
            (
                source_absolute_x
                - mouth_anchor_x
            )
            / (
                protected_boundary_x
                - mouth_anchor_x
            ),
            0.0,
            1.0,
        )

        outer_t_squared = (
            outer_t
            * outer_t
        )
        outer_t_cubed = (
            outer_t_squared
            * outer_t
        )

        outer_smootherstep = (
            outer_t_cubed
            * (
                10.0
                - 15.0
                * outer_t
                + 6.0
                * outer_t_squared
            )
        )

        outer_basis = (
            1.0
            - outer_smootherstep
        )

        horizontal_basis = np.where(
            source_absolute_x
            <= mouth_anchor_x,
            inner_basis,
            outer_basis,
        )

        mapped_absolute_x = (
            source_absolute_x
            + anchor_displacement
            * horizontal_basis
        )

        mapped_absolute_x = np.where(
            source_absolute_x
            >= protected_boundary_x,
            source_absolute_x,
            mapped_absolute_x,
        )

        mapped_source_x = np.copysign(
            mapped_absolute_x,
            source_x_coordinates,
        )

        mouth_displacement = (
            mapped_source_x
            - source_x_coordinates
        )

        result = (
            x_coordinates
            + mouth_displacement
        )

        result = np.where(
            protected_region,
            x_coordinates,
            result,
        )

        return result.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _deform_jaw_width(
        *,
        x_coordinates: np.ndarray,
        source_x_coordinates: np.ndarray,
        source_y_coordinates: np.ndarray,
        jaw_width: float,
    ) -> np.ndarray:
        jaw_anchor_x = 0.50
        protected_boundary_x = 0.78

        vertical_weight = np.exp(
            -(
                (
                    (
                        source_y_coordinates
                        + 0.52
                    )
                    / 0.25
                )
                ** 2
            )
        )

        upper_transition = np.clip(
            (
                -0.10
                - source_y_coordinates
            )
            / 0.30,
            0.0,
            1.0,
        )

        upper_transition_squared = (
            upper_transition
            * upper_transition
        )
        upper_transition_cubed = (
            upper_transition_squared
            * upper_transition
        )

        upper_transition = (
            upper_transition_cubed
            * (
                10.0
                - 15.0
                * upper_transition
                + 6.0
                * upper_transition_squared
            )
        )

        vertical_weight = (
            vertical_weight
            * upper_transition
        )

        protected_region = (
            (source_y_coordinates >= -0.10)
            | (
                np.abs(
                    source_x_coordinates,
                )
                >= protected_boundary_x
            )
        )

        vertical_weight = np.where(
            protected_region,
            0.0,
            vertical_weight,
        )

        effective_factor = (
            1.0
            + (
                jaw_width
                - 1.0
            )
            * vertical_weight
        )

        expanded_anchor = (
            protected_boundary_x
            - (
                protected_boundary_x
                - jaw_anchor_x
            )
            / effective_factor
        )

        compressed_anchor = (
            jaw_anchor_x
            * effective_factor
        )

        target_anchor = np.where(
            effective_factor >= 1.0,
            expanded_anchor,
            compressed_anchor,
        )

        current_absolute_x = np.abs(
            x_coordinates,
        )

        anchor_displacement = (
            target_anchor
            - jaw_anchor_x
        )

        inner_t = np.clip(
            current_absolute_x
            / jaw_anchor_x,
            0.0,
            1.0,
        )

        inner_t_squared = (
            inner_t
            * inner_t
        )
        inner_t_cubed = (
            inner_t_squared
            * inner_t
        )

        inner_basis = (
            inner_t_cubed
            * (
                10.0
                - 15.0
                * inner_t
                + 6.0
                * inner_t_squared
            )
        )

        outer_t = np.clip(
            (
                current_absolute_x
                - jaw_anchor_x
            )
            / (
                protected_boundary_x
                - jaw_anchor_x
            ),
            0.0,
            1.0,
        )

        outer_t_squared = (
            outer_t
            * outer_t
        )
        outer_t_cubed = (
            outer_t_squared
            * outer_t
        )

        outer_smootherstep = (
            outer_t_cubed
            * (
                10.0
                - 15.0
                * outer_t
                + 6.0
                * outer_t_squared
            )
        )

        outer_basis = (
            1.0
            - outer_smootherstep
        )

        horizontal_basis = np.where(
            current_absolute_x
            <= jaw_anchor_x,
            inner_basis,
            outer_basis,
        )

        mapped_absolute_x = (
            current_absolute_x
            + anchor_displacement
            * horizontal_basis
        )

        mapped_absolute_x = np.where(
            current_absolute_x
            >= protected_boundary_x,
            current_absolute_x,
            mapped_absolute_x,
        )

        mapped_current_x = np.copysign(
            mapped_absolute_x,
            x_coordinates,
        )

        result = np.where(
            protected_region,
            x_coordinates,
            mapped_current_x,
        )

        return result.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _chin_width_mask(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
    ) -> np.ndarray:
        mask = np.exp(
            -(
                (
                    x_coordinates
                    / 0.32
                )
                ** 2
                + (
                    (
                        y_coordinates
                        + 0.72
                    )
                    / 0.22
                )
                ** 2
            )
        )

        protected_region = (
            (y_coordinates >= -0.10)
            | (
                np.abs(
                    x_coordinates,
                )
                >= 0.78
            )
        )

        mask = np.where(
            protected_region,
            0.0,
            mask,
        )

        return mask.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _chin_length_mask(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
    ) -> np.ndarray:
        mask = np.exp(
            -(
                (
                    x_coordinates
                    / 0.30
                )
                ** 2
                + (
                    (
                        y_coordinates
                        + 0.74
                    )
                    / 0.24
                )
                ** 2
            )
        )

        protected_region = (
            (y_coordinates >= -0.10)
            | (
                np.abs(
                    x_coordinates,
                )
                >= 0.78
            )
        )

        mask = np.where(
            protected_region,
            0.0,
            mask,
        )

        return mask.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _forehead_height_mask(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
    ) -> np.ndarray:
        mask = np.exp(
            -(
                (
                    x_coordinates
                    / 0.52
                )
                ** 2
                + (
                    (
                        y_coordinates
                        - 0.70
                    )
                    / 0.30
                )
                ** 2
            )
        )

        protected_region = (
            (y_coordinates <= 0.20)
            | (
                np.abs(
                    x_coordinates,
                )
                >= 0.78
            )
        )

        mask = np.where(
            protected_region,
            0.0,
            mask,
        )

        return mask.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _nose_width_mask(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
    ) -> np.ndarray:
        mask = np.exp(
            -(
                (
                    x_coordinates
                    / 0.30
                )
                ** 2
                + (
                    (
                        y_coordinates
                        - 0.02
                    )
                    / 0.42
                )
                ** 2
            )
        )

        absolute_x = np.abs(
            x_coordinates,
        )

        outer_transition_start = 0.45
        protected_boundary_x = 0.70
        outer_transition_width = (
            protected_boundary_x
            - outer_transition_start
        )

        outer_transition = np.clip(
            (
                absolute_x
                - outer_transition_start
            )
            / outer_transition_width,
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

        mask = (
            mask
            * outer_weight
        )

        mask = np.where(
            absolute_x
            >= protected_boundary_x,
            0.0,
            mask,
        )

        return mask.astype(
            np.float64,
            copy=False,
        )


    @staticmethod
    def _nose_length_mask(
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
    ) -> np.ndarray:
        mask = np.exp(
            -(
                (
                    x_coordinates
                    / 0.24
                )
                ** 2
                + (
                    (
                        y_coordinates
                        - 0.05
                    )
                    / 0.46
                )
                ** 2
            )
        )

        mask = np.where(
            np.abs(
                x_coordinates,
            )
            >= 0.70,
            0.0,
            mask,
        )

        return mask.astype(
            np.float64,
            copy=False,
        )
