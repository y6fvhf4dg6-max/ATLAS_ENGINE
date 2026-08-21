from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_focal_identifiability_observation import (
    AtlasCanonicalHeadFocalIdentifiabilityObservation,
)


def _observation(**overrides):
    values = {
        "observation_id": "subject-01-perspective-focal",
        "focal_upper_bounds_px": (
            5000.0,
            10000.0,
            20000.0,
        ),
        "fitted_focal_lengths_px": (
            (5000.0, 5000.0, 5000.0),
            (10000.0, 10000.0, 10000.0),
            (20000.0, 20000.0, 20000.0),
        ),
    }
    values.update(overrides)

    return AtlasCanonicalHeadFocalIdentifiabilityObservation(
        **values
    )


def test_detects_focal_solution_that_tracks_every_upper_bound():
    observation = _observation()

    assert observation.trial_count == 3
    assert observation.view_count == 3
    assert observation.upper_bound_hit_by_trial == (
        True,
        True,
        True,
    )
    assert observation.is_bound_dependent is True
    assert observation.focal_identifiable is False


def test_interior_focal_solution_is_not_classified_as_bound_dependent():
    observation = _observation(
        fitted_focal_lengths_px=(
            (1800.0, 1820.0, 1790.0),
            (1810.0, 1805.0, 1815.0),
            (1808.0, 1812.0, 1804.0),
        ),
    )

    assert observation.upper_bound_hit_by_trial == (
        False,
        False,
        False,
    )
    assert observation.is_bound_dependent is False


def test_non_bound_dependence_alone_does_not_claim_identifiability():
    observation = _observation(
        fitted_focal_lengths_px=(
            (1800.0, 1800.0, 1800.0),
            (3500.0, 3500.0, 3500.0),
            (7000.0, 7000.0, 7000.0),
        ),
    )

    assert observation.is_bound_dependent is False
    assert observation.focal_identifiable is False


def test_stable_interior_solution_can_be_identifiable():
    observation = _observation(
        fitted_focal_lengths_px=(
            (1800.0, 1820.0, 1790.0),
            (1810.0, 1805.0, 1815.0),
            (1808.0, 1812.0, 1804.0),
        ),
    )

    assert observation.focal_identifiable is True


def test_requires_multiple_upper_bound_trials():
    with pytest.raises(
        ValueError,
        match="at least two",
    ):
        _observation(
            focal_upper_bounds_px=(5000.0,),
            fitted_focal_lengths_px=(
                (5000.0, 5000.0, 5000.0),
            ),
        )


def test_requires_matching_trial_counts():
    with pytest.raises(
        ValueError,
        match="trial count",
    ):
        _observation(
            fitted_focal_lengths_px=(
                (5000.0, 5000.0, 5000.0),
                (10000.0, 10000.0, 10000.0),
            ),
        )


def test_requires_same_view_count_for_every_trial():
    with pytest.raises(
        ValueError,
        match="view count",
    ):
        _observation(
            fitted_focal_lengths_px=(
                (5000.0, 5000.0, 5000.0),
                (10000.0, 10000.0),
                (20000.0, 20000.0, 20000.0),
            ),
        )


@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
    ),
)
def test_upper_bounds_must_be_positive_and_finite(value):
    with pytest.raises(ValueError):
        _observation(
            focal_upper_bounds_px=(
                5000.0,
                10000.0,
                value,
            ),
        )


def test_rejects_fitted_focal_above_its_trial_upper_bound():
    with pytest.raises(
        ValueError,
        match="upper bound",
    ):
        _observation(
            fitted_focal_lengths_px=(
                (5000.0, 5000.0, 5000.0),
                (10000.0, 10000.0, 10000.0),
                (20001.0, 20000.0, 20000.0),
            ),
        )


def test_observation_is_immutable():
    observation = _observation()

    with pytest.raises(FrozenInstanceError):
        observation.focal_upper_bounds_px = (1.0, 2.0)


def test_contract_does_not_claim_camera_or_identity_quality():
    observation = _observation()

    assert not hasattr(observation, "camera_observation")
    assert not hasattr(observation, "identity_preservation_support")
    assert not hasattr(observation, "multi_view_consistency")
    assert not hasattr(observation, "decision")
    assert not hasattr(observation, "phase_9_authorized")
