import numpy as np
import pytest

from CORE.atlas_portrait_identity_prior_provider import (
    AtlasPortraitIdentityPriorResult,
    require_commercially_cleared_prior,
)


def test_valid_identity_prior_result():
    result = AtlasPortraitIdentityPriorResult(
        identity_vector=np.array([0.1, -0.2, 0.3]),
        confidence=0.8,
        provider_name="atlas_native_test",
        provider_version="1",
        commercial_use_cleared=True,
    )

    np.testing.assert_array_equal(
        result.identity_vector,
        np.array([0.1, -0.2, 0.3]),
    )
    assert result.confidence == 0.8
    assert result.commercial_use_cleared is True


def test_identity_vector_is_read_only():
    result = AtlasPortraitIdentityPriorResult(
        identity_vector=np.array([1.0, 2.0]),
        confidence=1.0,
        provider_name="atlas_native_test",
        provider_version="1",
        commercial_use_cleared=True,
    )

    assert result.identity_vector.flags.writeable is False


@pytest.mark.parametrize(
    "vector",
    [
        np.array([]),
        np.array([[1.0, 2.0]]),
        np.array([np.nan]),
        np.array([np.inf]),
    ],
)
def test_invalid_identity_vectors_are_rejected(vector):
    with pytest.raises(ValueError):
        AtlasPortraitIdentityPriorResult(
            identity_vector=vector,
            confidence=0.5,
            provider_name="atlas_native_test",
            provider_version="1",
            commercial_use_cleared=True,
        )


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_invalid_confidence_is_rejected(confidence):
    with pytest.raises(ValueError, match="confidence"):
        AtlasPortraitIdentityPriorResult(
            identity_vector=np.array([1.0]),
            confidence=confidence,
            provider_name="atlas_native_test",
            provider_version="1",
            commercial_use_cleared=True,
        )


def test_empty_provider_name_is_rejected():
    with pytest.raises(ValueError, match="provider_name"):
        AtlasPortraitIdentityPriorResult(
            identity_vector=np.array([1.0]),
            confidence=0.5,
            provider_name=" ",
            provider_version="1",
            commercial_use_cleared=True,
        )


def test_empty_provider_version_is_rejected():
    with pytest.raises(ValueError, match="provider_version"):
        AtlasPortraitIdentityPriorResult(
            identity_vector=np.array([1.0]),
            confidence=0.5,
            provider_name="atlas_native_test",
            provider_version=" ",
            commercial_use_cleared=True,
        )


def test_commercially_cleared_prior_passes_gate():
    result = AtlasPortraitIdentityPriorResult(
        identity_vector=np.array([1.0]),
        confidence=0.9,
        provider_name="atlas_native_test",
        provider_version="1",
        commercial_use_cleared=True,
    )

    assert require_commercially_cleared_prior(result) is result


def test_noncommercial_prior_is_blocked():
    result = AtlasPortraitIdentityPriorResult(
        identity_vector=np.array([1.0]),
        confidence=0.9,
        provider_name="research_only_test",
        provider_version="1",
        commercial_use_cleared=False,
    )

    with pytest.raises(
        PermissionError,
        match="not cleared for commercial production use",
    ):
        require_commercially_cleared_prior(result)
