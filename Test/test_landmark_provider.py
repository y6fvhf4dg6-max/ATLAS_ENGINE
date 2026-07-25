import pytest

from CORE.atlas_landmark_provider import AtlasLandmarkProvider


def test_provider_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AtlasLandmarkProvider()


def test_provider_requires_from_source():
    assert hasattr(AtlasLandmarkProvider, "from_source")
