from __future__ import annotations

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)


class AtlasPortraitFlameBlendshapeEvaluator:
    """
    Evaluates FLAME identity and expression blendshapes.

    The evaluator applies identity and expression basis
    vectors to the canonical template vertices.

    Pose parameters are dimension-validated but are not
    applied at this stage. Pose corrective deformation,
    joint transformation, linear blend skinning, fitting,
    projection, rendering, relief compression, and STL
    generation are outside this class.
    """

    @classmethod
    def evaluate(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        parameters: AtlasPortraitFlameFittingParameters,
    ) -> np.ndarray:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        if not isinstance(
            parameters,
            AtlasPortraitFlameFittingParameters,
        ):
            raise TypeError(
                "parameters must be an "
                "AtlasPortraitFlameFittingParameters "
                "instance."
            )

        cls._validate_parameter_counts(
            model=model,
            parameters=parameters,
        )

        identity_offset = np.tensordot(
            model.identity_shape_directions,
            parameters.identity_parameters,
            axes=(
                2,
                0,
            ),
        )

        expression_offset = np.tensordot(
            model.expression_shape_directions,
            parameters.expression_parameters,
            axes=(
                2,
                0,
            ),
        )

        result = np.asarray(
            model.template_vertices
            + identity_offset
            + expression_offset,
            dtype=np.float64,
        ).copy()

        result.setflags(
            write=False,
        )

        return result

    @staticmethod
    def _validate_parameter_counts(
        *,
        model: AtlasPortraitFlameCanonicalModel,
        parameters: AtlasPortraitFlameFittingParameters,
    ) -> None:
        if (
            parameters.identity_parameter_count
            != model.identity_parameter_count
        ):
            raise ValueError(
                "identity parameter count does not match "
                "the canonical model."
            )

        if (
            parameters.expression_parameter_count
            != model.expression_parameter_count
        ):
            raise ValueError(
                "expression parameter count does not match "
                "the canonical model."
            )

        if (
            parameters.pose_parameter_count
            != model.pose_parameter_count
        ):
            raise ValueError(
                "pose parameter count does not match the "
                "canonical model."
            )
