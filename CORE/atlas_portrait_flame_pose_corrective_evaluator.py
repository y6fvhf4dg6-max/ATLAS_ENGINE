from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


class AtlasPortraitFlamePoseCorrectiveEvaluator:
    """
    Evaluates FLAME pose corrective vertex offsets.

    The evaluator contracts the canonical model's pose
    direction tensor with a validated pose-feature vector.

    It returns only the corrective displacement array.
    It performs no blendshape evaluation, joint regression,
    kinematic transformation, linear blend skinning,
    fitting, rendering, or STL generation.
    """

    @classmethod
    def evaluate(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        pose_features: Any,
    ) -> np.ndarray:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        normalized_features = cls._normalize_pose_features(
            pose_features,
            expected_count=model.pose_feature_count,
        )

        result = np.tensordot(
            model.pose_directions,
            normalized_features,
            axes=(
                2,
                0,
            ),
        )

        result = np.asarray(
            result,
            dtype=np.float64,
        ).copy()

        result.setflags(
            write=False,
        )

        return result

    @staticmethod
    def _normalize_pose_features(
        value: Any,
        *,
        expected_count: int,
    ) -> np.ndarray:
        try:
            pose_features = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "pose_features must be numeric."
            ) from exc

        if pose_features.ndim != 1:
            raise ValueError(
                "pose_features must be one-dimensional."
            )

        if pose_features.shape[0] != expected_count:
            raise ValueError(
                "pose_features length must match the "
                "canonical model pose feature count."
            )

        if not np.isfinite(
            pose_features,
        ).all():
            raise ValueError(
                "pose_features contains non-finite values."
            )

        return pose_features.astype(
            np.float64,
            copy=True,
        )
