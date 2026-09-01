import numpy as np
import pytest

from CORE.atlas_portrait_identity_prior_provider import (
    require_commercially_cleared_prior,
)
from CORE.atlas_portrait_native_identity_prior_provider import (
    AtlasPortraitNativeIdentityPriorProvider,
)


def test_native_prior_is_zero_centered_and_commercially_cleared():
    provider = AtlasPortraitNativeIdentityPriorProvider(
        identity_dimension=5,
    )

    result = provider.estimate_identity_prior()

    np.testing.assert_array_equal(
        result.identity_vector,
        np.zeros(5),
    )
    assert result.confidence == 1.0
    assert (
        result.provider_name
        == "atlas_native_zero_centered_identity_prior"
    )
    assert result.provider_version == "1"
    assert result.commercial_use_cleared is True
    assert require_commercially_cleared_prior(result) is result


def test_native_prior_does_not_depend_on_observation_object():
    provider = AtlasPortraitNativeIdentityPriorProvider(
        identity_dimension=3,
    )

    a = provider.estimate_identity_prior(
        observations={"subject": "a"},
    )
    b = provider.estimate_identity_prior(
        observations={"subject": "b"},
    )

    np.testing.assert_array_equal(
        a.identity_vector,
        b.identity_vector,
    )


def test_residual_is_identity_minus_zero_prior():
    provider = AtlasPortraitNativeIdentityPriorProvider(
        identity_dimension=4,
    )

    residual = provider.residual(
        identity_vector=np.array(
            [1.0, -2.0, 0.5, 3.0]
        ),
    )

    np.testing.assert_array_equal(
        residual,
        np.array([1.0, -2.0, 0.5, 3.0]),
    )
    assert residual.flags.writeable is False


@pytest.mark.parametrize(
    "dimension",
    [0, -1],
)
def test_nonpositive_identity_dimension_is_rejected(dimension):
    with pytest.raises(
        ValueError,
        match="identity_dimension must be positive",
    ):
        AtlasPortraitNativeIdentityPriorProvider(
            identity_dimension=dimension,
        )


def test_noninteger_identity_dimension_is_rejected():
    with pytest.raises(
        TypeError,
        match="identity_dimension must be an integer",
    ):
        AtlasPortraitNativeIdentityPriorProvider(
            identity_dimension=3.0,
        )


@pytest.mark.parametrize(
    "confidence",
    [-0.01, 1.01],
)
def test_invalid_confidence_is_rejected(confidence):
    with pytest.raises(ValueError, match="confidence"):
        AtlasPortraitNativeIdentityPriorProvider(
            identity_dimension=3,
            confidence=confidence,
        )


def test_wrong_residual_dimension_is_rejected():
    provider = AtlasPortraitNativeIdentityPriorProvider(
        identity_dimension=3,
    )

    with pytest.raises(
        ValueError,
        match="dimension does not match",
    ):
        provider.residual(
            identity_vector=np.zeros(2),
        )


def test_nonfinite_residual_input_is_rejected():
    provider = AtlasPortraitNativeIdentityPriorProvider(
        identity_dimension=3,
    )

    with pytest.raises(
        ValueError,
        match="only finite",
    ):
        provider.residual(
            identity_vector=np.array(
                [0.0, np.nan, 0.0]
            ),
        )


def test_multidimensional_residual_input_is_rejected():
    provider = AtlasPortraitNativeIdentityPriorProvider(
        identity_dimension=3,
    )

    with pytest.raises(
        ValueError,
        match="one-dimensional",
    ):
        provider.residual(
            identity_vector=np.zeros((1, 3)),
        )
