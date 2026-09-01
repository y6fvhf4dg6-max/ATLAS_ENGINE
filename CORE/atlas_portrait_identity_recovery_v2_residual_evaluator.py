from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from CORE.atlas_portrait_dense_image_surface_evidence_producer import (
    AtlasPortraitDenseImageSurfaceEvidenceProducer,
)
from CORE.atlas_portrait_flame_identity_geometry_evaluator import (
    AtlasPortraitFlameIdentityGeometryEvaluator,
)
from CORE.atlas_portrait_flame_multiview_landmark_residual import (
    _axis_angle_rotation_matrix,
    _flame_to_camera_axes,
)
from CORE.atlas_portrait_identity_recovery_v2_optimizer import (
    AtlasPortraitIdentityRecoveryV2ViewState,
)
from CORE.atlas_portrait_perspective_camera import (
    AtlasPortraitPerspectiveCamera,
)


@dataclass(frozen=True)
class AtlasPortraitIdentityRecoveryV2ResidualEvaluator:
    """
    Production residual-integration owner for Identity Recovery V2.

    The optimizer owns parameter search and objective composition.
    This evaluator owns conversion of the current candidate identity
    and per-view states into evidence-channel residuals.

    Objective channel weighting is deliberately not applied here.
    """

    geometry_evaluator: AtlasPortraitFlameIdentityGeometryEvaluator
    base_fx_fy_by_view: tuple[np.ndarray, ...]
    principal_xy_by_view: tuple[np.ndarray, ...]
    source_rgb_by_view: tuple[np.ndarray, ...]
    photometric_pairs: tuple[tuple[int, int], ...]
    photometric_vertex_indices_by_pair: tuple[np.ndarray, ...]
    photometric_baseline_confidence_by_pair: tuple[np.ndarray, ...]
    image_support_masks_by_view: tuple[np.ndarray | None, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.geometry_evaluator,
            AtlasPortraitFlameIdentityGeometryEvaluator,
        ):
            raise TypeError(
                "geometry_evaluator must be an "
                "AtlasPortraitFlameIdentityGeometryEvaluator."
            )

        sources = tuple(
            np.asarray(value, dtype=np.float64)
            for value in self.source_rgb_by_view
        )
        base_focals = tuple(
            np.asarray(value, dtype=np.float64)
            for value in self.base_fx_fy_by_view
        )
        principals = tuple(
            np.asarray(value, dtype=np.float64)
            for value in self.principal_xy_by_view
        )
        masks = tuple(self.image_support_masks_by_view)

        view_count = len(sources)

        if view_count == 0:
            raise ValueError(
                "at least one source view is required."
            )

        if not (
            len(base_focals)
            == len(principals)
            == len(masks)
            == view_count
        ):
            raise ValueError(
                "all per-view inputs must have the same view count."
            )

        normalized_sources = []
        normalized_focals = []
        normalized_principals = []
        normalized_masks = []

        for index in range(view_count):
            source = sources[index]

            if (
                source.ndim != 3
                or source.shape[2] != 3
                or source.shape[0] <= 0
                or source.shape[1] <= 0
                or not np.all(np.isfinite(source))
                or np.any(source < 0.0)
                or np.any(source > 1.0)
            ):
                raise ValueError(
                    "each source_rgb view must have shape "
                    "(H, W, 3) with finite rgb inside 0.0..1.0."
                )

            focal = base_focals[index]

            if (
                focal.shape != (2,)
                or not np.all(np.isfinite(focal))
                or np.any(focal <= 0.0)
            ):
                raise ValueError(
                    "each base_fx_fy entry must contain two "
                    "finite positive values."
                )

            principal = principals[index]

            if (
                principal.shape != (2,)
                or not np.all(np.isfinite(principal))
            ):
                raise ValueError(
                    "each principal_xy entry must contain two "
                    "finite values."
                )

            mask = masks[index]

            if mask is not None:
                mask = np.asarray(
                    mask,
                    dtype=np.bool_,
                )

                if mask.shape != source.shape[:2]:
                    raise ValueError(
                        "each image support mask must match its "
                        "source image dimensions."
                    )

                mask = mask.copy()
                mask.setflags(write=False)

            source = source.copy()
            focal = focal.copy()
            principal = principal.copy()

            source.setflags(write=False)
            focal.setflags(write=False)
            principal.setflags(write=False)

            normalized_sources.append(source)
            normalized_focals.append(focal)
            normalized_principals.append(principal)
            normalized_masks.append(mask)

        pairs = tuple(
            tuple(int(value) for value in pair)
            for pair in self.photometric_pairs
        )

        vertices_by_pair = tuple(
            np.asarray(value, dtype=np.int64)
            for value in self.photometric_vertex_indices_by_pair
        )

        confidence_by_pair = tuple(
            np.asarray(value, dtype=np.float64)
            for value in self.photometric_baseline_confidence_by_pair
        )

        if not pairs:
            raise ValueError(
                "at least one photometric pair is required."
            )

        if not (
            len(pairs)
            == len(vertices_by_pair)
            == len(confidence_by_pair)
        ):
            raise ValueError(
                "photometric pair inputs must have the same count."
            )

        normalized_vertices = []
        normalized_confidence = []

        for pair, vertex_indices, confidence in zip(
            pairs,
            vertices_by_pair,
            confidence_by_pair,
            strict=True,
        ):
            if len(pair) != 2:
                raise ValueError(
                    "each photometric pair must contain two view indices."
                )

            if (
                pair[0] < 0
                or pair[1] < 0
                or pair[0] >= view_count
                or pair[1] >= view_count
                or pair[0] == pair[1]
            ):
                raise ValueError(
                    "photometric pair contains invalid view indices."
                )

            if (
                vertex_indices.ndim != 1
                or vertex_indices.size == 0
                or np.any(vertex_indices < 0)
                or np.any(
                    vertex_indices
                    >= self.geometry_evaluator.vertex_count
                )
                or np.unique(vertex_indices).size
                != vertex_indices.size
            ):
                raise ValueError(
                    "photometric vertex indices must be unique "
                    "valid canonical vertex indices."
                )

            if (
                confidence.shape != vertex_indices.shape
                or not np.all(np.isfinite(confidence))
                or np.any(confidence < 0.0)
                or np.any(confidence > 1.0)
            ):
                raise ValueError(
                    "photometric baseline confidence must match "
                    "the frozen pair support and lie inside 0.0..1.0."
                )

            vertex_indices = vertex_indices.copy()
            confidence = confidence.copy()
            vertex_indices.setflags(write=False)
            confidence.setflags(write=False)

            normalized_vertices.append(vertex_indices)
            normalized_confidence.append(confidence)

        object.__setattr__(
            self,
            "source_rgb_by_view",
            tuple(normalized_sources),
        )
        object.__setattr__(
            self,
            "base_fx_fy_by_view",
            tuple(normalized_focals),
        )
        object.__setattr__(
            self,
            "principal_xy_by_view",
            tuple(normalized_principals),
        )
        object.__setattr__(
            self,
            "image_support_masks_by_view",
            tuple(normalized_masks),
        )
        object.__setattr__(
            self,
            "photometric_pairs",
            pairs,
        )
        object.__setattr__(
            self,
            "photometric_vertex_indices_by_pair",
            tuple(normalized_vertices),
        )
        object.__setattr__(
            self,
            "photometric_baseline_confidence_by_pair",
            tuple(normalized_confidence),
        )

    @property
    def applies_objective_channel_weighting(self) -> bool:
        return False

    def __call__(
        self,
        identity_vector: np.ndarray,
        view_states: Sequence[
            AtlasPortraitIdentityRecoveryV2ViewState
        ],
    ) -> dict[str, np.ndarray]:
        states = tuple(view_states)

        if len(states) != len(self.source_rgb_by_view):
            raise ValueError(
                "view state count must match configured source views."
            )

        if not all(
            isinstance(
                state,
                AtlasPortraitIdentityRecoveryV2ViewState,
            )
            for state in states
        ):
            raise TypeError(
                "all view states must be "
                "AtlasPortraitIdentityRecoveryV2ViewState instances."
            )

        geometry = self.geometry_evaluator.evaluate(
            identity_vector=identity_vector,
        )

        projected_by_view = []
        camera_z_by_view = []

        for index, state in enumerate(states):
            rotation = _axis_angle_rotation_matrix(
                state.pose_radians
            )

            rotated_vertices = (
                geometry.vertices @ rotation.T
            )

            camera_vertices = (
                _flame_to_camera_axes(
                    rotated_vertices
                )
                + state.translation_xyz[None, :]
            )

            focal_scale = state.focal_scale_xy
            base_focal = self.base_fx_fy_by_view[index]
            principal = self.principal_xy_by_view[index]

            camera = AtlasPortraitPerspectiveCamera(
                fx=float(
                    base_focal[0] * focal_scale[0]
                ),
                fy=float(
                    base_focal[1] * focal_scale[1]
                ),
                cx=float(principal[0]),
                cy=float(principal[1]),
            )

            projected_by_view.append(
                camera.project(camera_vertices)
            )
            camera_z_by_view.append(
                np.asarray(
                    camera_vertices[:, 2],
                    dtype=np.float64,
                )
            )

        photometric_blocks = []

        for pair_index, (view_a, view_b) in enumerate(
            self.photometric_pairs
        ):
            photometric_blocks.append(
                AtlasPortraitDenseImageSurfaceEvidenceProducer
                .candidate_sensitive_pairwise_photometric_residual(
                    source_rgb_a=self.source_rgb_by_view[view_a],
                    source_rgb_b=self.source_rgb_by_view[view_b],
                    canonical_vertex_indices=(
                        self.photometric_vertex_indices_by_pair[
                            pair_index
                        ]
                    ),
                    baseline_confidence=(
                        self.photometric_baseline_confidence_by_pair[
                            pair_index
                        ]
                    ),
                    candidate_projected_xy_a=(
                        projected_by_view[view_a]
                    ),
                    candidate_camera_z_a=(
                        camera_z_by_view[view_a]
                    ),
                    candidate_projected_xy_b=(
                        projected_by_view[view_b]
                    ),
                    candidate_camera_z_b=(
                        camera_z_by_view[view_b]
                    ),
                    faces=geometry.faces,
                    image_support_mask_a=(
                        self.image_support_masks_by_view[view_a]
                    ),
                    image_support_mask_b=(
                        self.image_support_masks_by_view[view_b]
                    ),
                )
            )

        photometric = np.concatenate(
            photometric_blocks
        ).astype(
            np.float64,
            copy=False,
        )
        photometric.setflags(write=False)

        return {
            "photometric": photometric,
        }
