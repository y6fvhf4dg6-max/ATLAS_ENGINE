from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadFocalIdentifiabilityObservation:
    observation_id: str
    focal_upper_bounds_px: tuple[float, ...]
    fitted_focal_lengths_px: tuple[tuple[float, ...], ...]

    BOUND_HIT_RELATIVE_TOLERANCE = 1.0e-6
    STABILITY_RELATIVE_TOLERANCE = 0.02

    def __post_init__(self) -> None:
        observation_id = str(
            self.observation_id
        ).strip()

        if not observation_id:
            raise ValueError(
                "observation_id must be non-blank."
            )

        upper_bounds = tuple(
            self._normalize_positive_finite(
                value,
                name="focal upper bound",
            )
            for value in self.focal_upper_bounds_px
        )

        if len(upper_bounds) < 2:
            raise ValueError(
                "at least two focal upper-bound trials are required."
            )

        try:
            raw_trials = tuple(
                self.fitted_focal_lengths_px
            )
        except TypeError as exc:
            raise TypeError(
                "fitted_focal_lengths_px must be an iterable of trials."
            ) from exc

        if len(raw_trials) != len(
            upper_bounds
        ):
            raise ValueError(
                "fitted focal trial count must match upper-bound trial count."
            )

        normalized_trials = []

        expected_view_count = None

        for trial_index, (
            upper_bound,
            raw_trial,
        ) in enumerate(
            zip(
                upper_bounds,
                raw_trials,
            )
        ):
            try:
                trial = tuple(
                    self._normalize_positive_finite(
                        value,
                        name="fitted focal length",
                    )
                    for value in raw_trial
                )
            except TypeError as exc:
                raise TypeError(
                    "each fitted focal trial must be an iterable."
                ) from exc

            if not trial:
                raise ValueError(
                    "each fitted focal trial must contain at least one view."
                )

            if expected_view_count is None:
                expected_view_count = len(
                    trial
                )
            elif len(
                trial
            ) != expected_view_count:
                raise ValueError(
                    "every fitted focal trial must have the same view count."
                )

            for fitted_focal in trial:
                if fitted_focal > upper_bound:
                    raise ValueError(
                        "fitted focal length must not exceed its trial upper bound."
                    )

            normalized_trials.append(
                trial
            )

        object.__setattr__(
            self,
            "observation_id",
            observation_id,
        )
        object.__setattr__(
            self,
            "focal_upper_bounds_px",
            upper_bounds,
        )
        object.__setattr__(
            self,
            "fitted_focal_lengths_px",
            tuple(
                normalized_trials
            ),
        )

    @property
    def trial_count(
        self,
    ) -> int:
        return len(
            self.focal_upper_bounds_px
        )

    @property
    def view_count(
        self,
    ) -> int:
        return len(
            self.fitted_focal_lengths_px[
                0
            ]
        )

    @property
    def upper_bound_hit_by_trial(
        self,
    ) -> tuple[bool, ...]:
        results = []

        for upper_bound, trial in zip(
            self.focal_upper_bounds_px,
            self.fitted_focal_lengths_px,
        ):
            hit = all(
                math.isclose(
                    fitted_focal,
                    upper_bound,
                    rel_tol=(
                        self.BOUND_HIT_RELATIVE_TOLERANCE
                    ),
                    abs_tol=1.0e-9,
                )
                for fitted_focal in trial
            )

            results.append(
                hit
            )

        return tuple(
            results
        )

    @property
    def is_bound_dependent(
        self,
    ) -> bool:
        return all(
            self.upper_bound_hit_by_trial
        )

    @property
    def focal_identifiable(
        self,
    ) -> bool:
        if self.is_bound_dependent:
            return False

        trial_means = tuple(
            sum(trial) / len(trial)
            for trial in self.fitted_focal_lengths_px
        )

        minimum = min(
            trial_means
        )
        maximum = max(
            trial_means
        )

        reference = max(
            abs(
                sum(trial_means)
                / len(trial_means)
            ),
            1.0e-12,
        )

        relative_range = (
            maximum - minimum
        ) / reference

        return (
            relative_range
            <= self.STABILITY_RELATIVE_TOLERANCE
        )

    @staticmethod
    def _normalize_positive_finite(
        value: object,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if (
            not math.isfinite(
                numeric
            )
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be positive and finite."
            )

        return numeric
