import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_ground_truth_observation import (
    AtlasCanonicalHeadMetricGroundTruthObservation,
)


def _observation(**overrides):
    values = {
        "observation_id": "metric-gt-01",
        "subject_id": "subject-01",
        "source_id": "benchmark-source-a",
        "units": "mm",
        "ground_truth_vertices": np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        "ground_truth_faces": (
            (0, 1, 2),
        ),
        "reconstruction_vertices": np.asarray(
            [
                [0.0, 0.0, 0.1],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        "reconstruction_faces": (
            (0, 1, 2),
        ),
        "source_provenance_state": "VERIFIED",
        "evaluation_license_state": "ACCEPTABLE",
        "evaluation_use_only": True,
    }
    values.update(overrides)
    return AtlasCanonicalHeadMetricGroundTruthObservation(**values)


def test_accepts_metric_ground_truth_observation():
    observation = _observation()

    assert observation.observation_id == "metric-gt-01"
    assert observation.subject_id == "subject-01"
    assert observation.source_id == "benchmark-source-a"
    assert observation.units == "mm"
    assert observation.source_provenance_state == "VERIFIED"
    assert observation.evaluation_license_state == "ACCEPTABLE"
    assert observation.evaluation_use_only is True


def test_requires_millimetre_units():
    with pytest.raises(ValueError, match="units"):
        _observation(units="px")


def test_rejects_nonfinite_ground_truth_vertices():
    vertices = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [np.nan, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    with pytest.raises(ValueError, match="ground_truth_vertices"):
        _observation(ground_truth_vertices=vertices)


def test_rejects_nonfinite_reconstruction_vertices():
    vertices = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, np.inf, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    with pytest.raises(ValueError, match="reconstruction_vertices"):
        _observation(reconstruction_vertices=vertices)


def test_requires_boolean_evaluation_use_only():
    with pytest.raises(TypeError, match="evaluation_use_only"):
        _observation(evaluation_use_only="yes")


def test_normalizes_metric_ground_truth_policy_states():
    observation = _observation(
        source_provenance_state=" verified ",
        evaluation_license_state=" acceptable ",
    )

    assert observation.source_provenance_state == "VERIFIED"
    assert observation.evaluation_license_state == "ACCEPTABLE"


def test_rejects_unknown_source_provenance_state():
    with pytest.raises(ValueError, match="source_provenance_state"):
        _observation(source_provenance_state="MAYBE")


def test_rejects_unknown_evaluation_license_state():
    with pytest.raises(ValueError, match="evaluation_license_state"):
        _observation(evaluation_license_state="MAYBE")
