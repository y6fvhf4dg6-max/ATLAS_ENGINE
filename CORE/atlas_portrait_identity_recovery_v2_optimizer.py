from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import numpy as np
from scipy.optimize import least_squares

from CORE.atlas_portrait_identity_recovery_v2_objective import (
    AtlasPortraitIdentityRecoveryV2Objective,
)
from CORE.atlas_portrait_identity_recovery_v2_spec import (
    AtlasPortraitIdentityRecoveryV2Spec,
)
from CORE.atlas_portrait_native_identity_prior_provider import (
    AtlasPortraitNativeIdentityPriorProvider,
)


@dataclass(frozen=True)
class AtlasPortraitIdentityRecoveryV2ViewState:
    """
    Per-view optimization state.

    Identity is deliberately absent: identity is shared globally.
    """

    pose_radians: np.ndarray
    translation_xyz: np.ndarray
    log_focal_scale_xy: np.ndarray

    def __post_init__(self) -> None:
        arrays = {
            "pose_radians": (self.pose_radians, 3),
            "translation_xyz": (self.translation_xyz, 3),
            "log_focal_scale_xy": (self.log_focal_scale_xy, 2),
        }

        for name, (value, size) in arrays.items():
            array = np.asarray(value, dtype=np.float64)

            if array.shape != (size,):
                raise ValueError(
                    f"{name} must have shape ({size},)."
                )

            if not np.all(np.isfinite(array)):
                raise ValueError(
                    f"{name} must contain only finite values."
                )

            array = array.copy()
            array.setflags(write=False)
            object.__setattr__(self, name, array)

    @property
    def focal_scale_xy(self) -> np.ndarray:
        scale = np.exp(self.log_focal_scale_xy)
        scale.setflags(write=False)
        return scale


@dataclass(frozen=True)
class AtlasPortraitIdentityRecoveryV2OptimizerResult:
    identity_vector: np.ndarray
    view_states: tuple[AtlasPortraitIdentityRecoveryV2ViewState, ...]
    success: bool
    cost: float
    optimality: float
    nfev: int
    message: str
    residual_vector: np.ndarray

    def __post_init__(self) -> None:
        identity = np.asarray(
            self.identity_vector,
            dtype=np.float64,
        ).copy()
        residual = np.asarray(
            self.residual_vector,
            dtype=np.float64,
        ).copy()

        identity.setflags(write=False)
        residual.setflags(write=False)

        object.__setattr__(self, "identity_vector", identity)
        object.__setattr__(self, "residual_vector", residual)


ResidualEvaluator = Callable[
    [
        np.ndarray,
        tuple[AtlasPortraitIdentityRecoveryV2ViewState, ...],
    ],
    Mapping[str, np.ndarray],
]


class AtlasPortraitIdentityRecoveryV2Optimizer:
    """
    Shared-identity / per-view-camera-pose least-squares optimizer.

    Parameter layout:
        [shared identity]
        then for each view:
            [rx, ry, rz]
            [tx, ty, tz]
            [log_fx_scale, log_fy_scale]

    Evidence geometry remains outside this class and is supplied by a
    residual evaluator. The native identity prior is injected here so
    callers cannot accidentally omit regularization when the prior
    channel is enabled.
    """

    VIEW_PARAMETER_COUNT = 8

    def __init__(
        self,
        *,
        spec: AtlasPortraitIdentityRecoveryV2Spec,
        identity_dimension: int,
        identity_bound: float = 3.0,
        pose_bound_degrees: float = 60.0,
        translation_bound: float = 1000.0,
        translation_z_min: float = 1.0e-3,
        focal_scale_min: float = 0.5,
        focal_scale_max: float = 2.0,
        max_nfev: int = 300,
    ) -> None:
        if identity_dimension <= 0:
            raise ValueError(
                "identity_dimension must be positive."
            )
        if identity_bound <= 0.0:
            raise ValueError(
                "identity_bound must be positive."
            )
        if not (0.0 < pose_bound_degrees <= 180.0):
            raise ValueError(
                "pose_bound_degrees must be within (0, 180]."
            )
        if translation_bound <= 0.0:
            raise ValueError(
                "translation_bound must be positive."
            )
        if translation_z_min <= 0.0:
            raise ValueError(
                "translation_z_min must be positive."
            )
        if translation_z_min >= translation_bound:
            raise ValueError(
                "translation_z_min must be smaller than "
                "translation_bound."
            )
        if focal_scale_min <= 0.0:
            raise ValueError(
                "focal_scale_min must be positive."
            )
        if focal_scale_max <= focal_scale_min:
            raise ValueError(
                "focal_scale_max must exceed focal_scale_min."
            )
        if max_nfev <= 0:
            raise ValueError(
                "max_nfev must be positive."
            )

        self.spec = spec
        self.identity_dimension = int(identity_dimension)
        self.identity_bound = float(identity_bound)
        self.pose_bound_radians = float(
            np.deg2rad(pose_bound_degrees)
        )
        self.translation_bound = float(translation_bound)
        self.translation_z_min = float(translation_z_min)
        self.log_focal_scale_min = float(
            np.log(focal_scale_min)
        )
        self.log_focal_scale_max = float(
            np.log(focal_scale_max)
        )
        self.max_nfev = int(max_nfev)

        self.identity_prior = (
            AtlasPortraitNativeIdentityPriorProvider(
                identity_dimension=self.identity_dimension,
            )
        )

    def pack(
        self,
        *,
        identity_vector: np.ndarray,
        view_states: Sequence[
            AtlasPortraitIdentityRecoveryV2ViewState
        ],
    ) -> np.ndarray:
        identity = np.asarray(
            identity_vector,
            dtype=np.float64,
        )

        if identity.shape != (self.identity_dimension,):
            raise ValueError(
                "identity_vector dimension mismatch."
            )

        if not np.all(np.isfinite(identity)):
            raise ValueError(
                "identity_vector must contain only finite values."
            )

        if not view_states:
            raise ValueError(
                "at least one view state is required."
            )

        blocks = [identity]

        for state in view_states:
            blocks.extend(
                [
                    state.pose_radians,
                    state.translation_xyz,
                    state.log_focal_scale_xy,
                ]
            )

        return np.concatenate(blocks)

    def unpack(
        self,
        parameters: np.ndarray,
        *,
        view_count: int,
    ) -> tuple[
        np.ndarray,
        tuple[AtlasPortraitIdentityRecoveryV2ViewState, ...],
    ]:
        parameters = np.asarray(
            parameters,
            dtype=np.float64,
        )

        expected = (
            self.identity_dimension
            + view_count * self.VIEW_PARAMETER_COUNT
        )

        if parameters.shape != (expected,):
            raise ValueError(
                f"parameter vector must have shape ({expected},)."
            )

        identity = parameters[
            : self.identity_dimension
        ].copy()

        states = []
        offset = self.identity_dimension

        for _ in range(view_count):
            pose = parameters[offset:offset + 3]
            offset += 3
            translation = parameters[offset:offset + 3]
            offset += 3
            log_focal = parameters[offset:offset + 2]
            offset += 2

            states.append(
                AtlasPortraitIdentityRecoveryV2ViewState(
                    pose_radians=pose,
                    translation_xyz=translation,
                    log_focal_scale_xy=log_focal,
                )
            )

        identity.setflags(write=False)
        return identity, tuple(states)

    def parameter_bounds(
        self,
        *,
        view_count: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        if view_count <= 0:
            raise ValueError(
                "view_count must be positive."
            )

        lower = np.full(
            self.identity_dimension,
            -self.identity_bound,
            dtype=np.float64,
        )
        upper = np.full(
            self.identity_dimension,
            self.identity_bound,
            dtype=np.float64,
        )

        view_lower = np.array(
            [
                -self.pose_bound_radians,
                -self.pose_bound_radians,
                -self.pose_bound_radians,
                -self.translation_bound,
                -self.translation_bound,
                self.translation_z_min,
                self.log_focal_scale_min,
                self.log_focal_scale_min,
            ],
            dtype=np.float64,
        )

        view_upper = np.array(
            [
                self.pose_bound_radians,
                self.pose_bound_radians,
                self.pose_bound_radians,
                self.translation_bound,
                self.translation_bound,
                self.translation_bound,
                self.log_focal_scale_max,
                self.log_focal_scale_max,
            ],
            dtype=np.float64,
        )

        lower = np.concatenate(
            [lower] + [view_lower] * view_count
        )
        upper = np.concatenate(
            [upper] + [view_upper] * view_count
        )

        return lower, upper

    def fit(
        self,
        *,
        initial_identity: np.ndarray,
        initial_view_states: Sequence[
            AtlasPortraitIdentityRecoveryV2ViewState
        ],
        residual_evaluator: ResidualEvaluator,
    ) -> AtlasPortraitIdentityRecoveryV2OptimizerResult:
        view_count = len(initial_view_states)

        x0 = self.pack(
            identity_vector=initial_identity,
            view_states=initial_view_states,
        )

        lower, upper = self.parameter_bounds(
            view_count=view_count,
        )

        if np.any(x0 < lower) or np.any(x0 > upper):
            raise ValueError(
                "initial parameters lie outside optimizer bounds."
            )

        def evaluate(parameters: np.ndarray) -> np.ndarray:
            identity, states = self.unpack(
                parameters,
                view_count=view_count,
            )

            residuals = dict(
                residual_evaluator(
                    identity,
                    states,
                )
            )

            if self.spec.use_identity_prior:
                if "identity_prior" in residuals:
                    raise ValueError(
                        "identity_prior residual is owned by the "
                        "optimizer and must not be supplied externally."
                    )

                residuals["identity_prior"] = (
                    self.identity_prior.residual(
                        identity_vector=identity,
                    )
                )

            result = (
                AtlasPortraitIdentityRecoveryV2Objective.compose(
                    spec=self.spec,
                    residuals_by_channel=residuals,
                )
            )

            return result.residual_vector

        solved = least_squares(
            evaluate,
            x0,
            bounds=(lower, upper),
            method="trf",
            ftol=1.0e-10,
            xtol=1.0e-10,
            gtol=1.0e-10,
            max_nfev=self.max_nfev,
        )

        identity, states = self.unpack(
            solved.x,
            view_count=view_count,
        )

        final_residual = evaluate(solved.x).copy()
        final_residual.setflags(write=False)

        return AtlasPortraitIdentityRecoveryV2OptimizerResult(
            identity_vector=identity,
            view_states=states,
            success=bool(solved.success),
            cost=float(solved.cost),
            optimality=float(solved.optimality),
            nfev=int(solved.nfev),
            message=str(solved.message),
            residual_vector=final_residual,
        )
