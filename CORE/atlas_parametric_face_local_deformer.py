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
    - nose width
    - nose length

    Deformation uses smooth Gaussian influence masks so
    distant facial regions remain unchanged.

    It performs no global scaling, rotation, translation,
    projection, rendering, triangulation, or mesh
    generation.
    """

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

        width_factor = (
            1.0
            + (
                parameters.nose_width
                - 1.0
            )
            * nose_width_mask
        )

        nose_center_y = 0.05

        length_factor = (
            1.0
            + (
                parameters.nose_length
                - 1.0
            )
            * nose_length_mask
        )

        deformed_x = (
            source_x
            * width_factor
        )

        deformed_y = (
            nose_center_y
            + (
                source_y
                - nose_center_y
            )
            * length_factor
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
