from __future__ import annotations

import numpy as np

from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)
from CORE.atlas_portrait_flame_model_parameter_specification import (
    AtlasPortraitFlameModelParameterSpecification,
)


class AtlasPortraitFlameFittingParameterInitializer:
    """
    Creates deterministic neutral FLAME fitting parameters.

    Parameter-vector dimensions are taken from an immutable
    FLAME model parameter specification. Identity,
    expression, and pose vectors are initialized to zero.

    It performs no FLAME model loading, camera solving,
    landmark fitting, optimization, blendshape evaluation,
    mesh deformation, projection, rendering, relief
    compression, or STL generation.
    """

    @classmethod
    def initialize(
        cls,
        specification: (
            AtlasPortraitFlameModelParameterSpecification
        ),
    ) -> AtlasPortraitFlameFittingParameters:
        if not isinstance(
            specification,
            AtlasPortraitFlameModelParameterSpecification,
        ):
            raise TypeError(
                "specification must be an "
                "AtlasPortraitFlameModelParameterSpecification "
                "instance."
            )

        return AtlasPortraitFlameFittingParameters(
            identity_parameters=np.zeros(
                specification.identity_parameter_count,
                dtype=np.float64,
            ),
            expression_parameters=np.zeros(
                specification.expression_parameter_count,
                dtype=np.float64,
            ),
            pose_parameters=np.zeros(
                specification.pose_parameter_count,
                dtype=np.float64,
            ),
            metadata=cls._build_metadata(
                specification,
            ),
        )

    @staticmethod
    def _build_metadata(
        specification: (
            AtlasPortraitFlameModelParameterSpecification
        ),
    ) -> dict[str, object]:
        return {
            "fitting_stage": "neutral_initialization",
            "initialization_method": "zero_parameters",
            "model_family": specification.model_family,
            "model_version": specification.model_version,
            "synthetic": specification.metadata.get(
                "synthetic",
            ),
        }
