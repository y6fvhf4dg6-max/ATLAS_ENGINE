from __future__ import annotations

import numpy as np

from CORE.atlas_portrait_flame_blendshape_evaluator import (
    AtlasPortraitFlameBlendshapeEvaluator,
)
from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
    AtlasPortraitFlameDeformedMeshEvaluator,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)
from CORE.atlas_portrait_flame_image_coordinate_normalizer import (
    AtlasPortraitFlameImageCoordinateNormalizer,
)
from CORE.atlas_portrait_flame_joint_regressor_evaluator import (
    AtlasPortraitFlameJointRegressorEvaluator,
)
from CORE.atlas_portrait_flame_kinematic_transform_evaluator import (
    AtlasPortraitFlameKinematicTransformEvaluator,
)
from CORE.atlas_portrait_flame_linear_blend_skinning_evaluator import (
    AtlasPortraitFlameLinearBlendSkinningEvaluator,
)
from CORE.atlas_portrait_flame_pose_corrective_evaluator import (
    AtlasPortraitFlamePoseCorrectiveEvaluator,
)
from CORE.atlas_portrait_flame_pose_feature_evaluator import (
    AtlasPortraitFlamePoseFeatureEvaluator,
)
from CORE.atlas_portrait_flame_posed_vertex_composer import (
    AtlasPortraitFlamePosedVertexComposer,
)


class AtlasPortraitFlameFittedMeshBuilder:
    """
    Builds an image-coordinate FLAME mesh from a completed
    dense-identity fitting pipeline result.

    Processing sequence:

        fitted identity parameters
        + fitted root pose
        + neutral expression
        + neutral non-root pose
        -> blendshape evaluation
        -> joint regression
        -> pose corrective evaluation
        -> posed vertex composition
        -> kinematic transforms
        -> linear blend skinning
        -> image-coordinate normalization
        -> immutable deformed mesh

    The builder performs no fitting, camera solving,
    projection, rendering, relief conversion, persistence,
    or STL generation.
    """

    @classmethod
    def build(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        pipeline_result: (
            AtlasPortraitFlameDenseIdentityPipelineResult
        ),
    ) -> AtlasPortraitFlameDeformedMesh:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        if not isinstance(
            pipeline_result,
            AtlasPortraitFlameDenseIdentityPipelineResult,
        ):
            raise TypeError(
                "pipeline_result must be an "
                "AtlasPortraitFlameDenseIdentityPipelineResult "
                "instance."
            )

        identity_parameters = (
            pipeline_result.final_identity_parameters
        )

        if (
            identity_parameters.shape[0]
            != model.identity_parameter_count
        ):
            raise ValueError(
                "identity parameter count does not match "
                "the canonical model."
            )

        if (
            model.pose_parameter_count < 6
            or model.pose_parameter_count % 3 != 0
        ):
            raise ValueError(
                "model must contain at least two "
                "three-component axis-angle pose joints."
            )

        expression_parameters = np.zeros(
            model.expression_parameter_count,
            dtype=np.float64,
        )

        pose_parameters = np.zeros(
            model.pose_parameter_count,
            dtype=np.float64,
        )
        pose_parameters[
            :3
        ] = pipeline_result.final_root_pose_parameters

        parameters = AtlasPortraitFlameFittingParameters(
            identity_parameters=identity_parameters,
            expression_parameters=expression_parameters,
            pose_parameters=pose_parameters,
            metadata={
                "fitting_stage": "fitted_mesh",
                "model_family": "flame",
                "model_version": model.metadata.get(
                    "model_version"
                ),
                "synthetic": model.metadata.get(
                    "synthetic"
                ),
            },
        )

        shaped_vertices = (
            AtlasPortraitFlameBlendshapeEvaluator.evaluate(
                model,
                parameters=parameters,
            )
        )

        joint_positions = (
            AtlasPortraitFlameJointRegressorEvaluator.evaluate(
                model,
                shaped_vertices=shaped_vertices,
            )
        )

        pose_features = (
            AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
                parameters
            )
        )

        pose_corrective_offsets = (
            AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
                model,
                pose_features=pose_features,
            )
        )

        posed_vertices = (
            AtlasPortraitFlamePosedVertexComposer.compose(
                model,
                shaped_vertices=shaped_vertices,
                pose_corrective_offsets=(
                    pose_corrective_offsets
                ),
            )
        )

        joint_transforms = (
            AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
                model,
                joint_positions=joint_positions,
                pose_parameters=pose_parameters,
            )
        )

        skinned_vertices = (
            AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
                model,
                posed_vertices=posed_vertices,
                joint_transforms=joint_transforms,
            )
        )

        (
            image_vertices,
            image_triangle_faces,
        ) = (
            AtlasPortraitFlameImageCoordinateNormalizer
            .normalize_mesh(
                vertices=skinned_vertices,
                triangle_faces=model.triangle_faces,
            )
        )

        return AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
            AtlasPortraitFlameCanonicalModel(
                template_vertices=model.template_vertices,
                triangle_faces=image_triangle_faces,
                identity_shape_directions=(
                    model.identity_shape_directions
                ),
                expression_shape_directions=(
                    model.expression_shape_directions
                ),
                pose_directions=model.pose_directions,
                pose_parameter_count=model.pose_parameter_count,
                joint_regressor=model.joint_regressor,
                skinning_weights=model.skinning_weights,
                kinematic_tree=model.kinematic_tree,
                metadata=model.metadata,
            ),
            skinned_vertices=image_vertices,
        )
