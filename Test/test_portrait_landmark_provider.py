import pytest

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.providers.portrait.atlas_portrait_landmark_provider import (
    AtlasPortraitLandmarkProvider,
)


class FixturePortraitLandmarkProvider(
    AtlasPortraitLandmarkProvider,
):
    PROVIDER_ID = "fixture-provider"

    def detect(
        self,
        portrait_input,
    ) -> AtlasPortraitLandmarkResult:
        return AtlasPortraitLandmarkResult(
            image_width=1000,
            image_height=800,
            landmarks={
                "nose_tip": (
                    0.50,
                    0.55,
                ),
            },
            confidence=0.95,
            provider_id=self.provider_id,
            metadata={
                "portrait_input": portrait_input,
            },
        )


def test_provider_base_is_abstract():
    with pytest.raises(
        TypeError,
    ):
        AtlasPortraitLandmarkProvider()


def test_provider_exposes_normalized_provider_id():
    provider = FixturePortraitLandmarkProvider()

    assert provider.provider_id == "fixture-provider"


def test_provider_detect_returns_landmark_result():
    provider = FixturePortraitLandmarkProvider()

    result = provider.detect(
        portrait_input="fixture-image",
    )

    assert isinstance(
        result,
        AtlasPortraitLandmarkResult,
    )
    assert result.provider_id == "fixture-provider"
    assert result.metadata["portrait_input"] == ("fixture-image")


def test_provider_validates_its_result():
    provider = FixturePortraitLandmarkProvider()

    result = provider.detect(
        portrait_input="fixture-image",
    )

    assert provider.validate_result(result) is result


def test_provider_rejects_non_result_output():
    provider = FixturePortraitLandmarkProvider()

    with pytest.raises(
        TypeError,
        match=("AtlasPortraitLandmarkResult"),
    ):
        provider.validate_result(
            {
                "landmarks": {},
            }
        )


def test_provider_rejects_result_from_another_provider():
    provider = FixturePortraitLandmarkProvider()

    result = AtlasPortraitLandmarkResult(
        image_width=1000,
        image_height=800,
        landmarks={
            "nose_tip": (
                0.50,
                0.55,
            ),
        },
        confidence=0.95,
        provider_id="another-provider",
        metadata={},
    )

    with pytest.raises(
        ValueError,
        match="provider_id",
    ):
        provider.validate_result(result)


class MissingProviderId(
    AtlasPortraitLandmarkProvider,
):
    def detect(
        self,
        portrait_input,
    ) -> AtlasPortraitLandmarkResult:
        raise NotImplementedError


@pytest.mark.parametrize(
    "provider_id",
    [
        "",
        "   ",
        123,
        None,
    ],
)
def test_provider_rejects_invalid_provider_id(
    provider_id,
):
    class InvalidProvider(
        AtlasPortraitLandmarkProvider,
    ):
        PROVIDER_ID = provider_id

        def detect(
            self,
            portrait_input,
        ) -> AtlasPortraitLandmarkResult:
            raise NotImplementedError

    with pytest.raises(
        ValueError,
    ):
        InvalidProvider()


def test_provider_requires_explicit_provider_id():
    with pytest.raises(
        ValueError,
    ):
        MissingProviderId()


def test_provider_id_is_read_only():
    provider = FixturePortraitLandmarkProvider()

    with pytest.raises(
        AttributeError,
    ):
        provider.provider_id = "changed-provider"
