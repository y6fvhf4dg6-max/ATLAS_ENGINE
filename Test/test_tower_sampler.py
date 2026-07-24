from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_tower_sampler import AtlasTowerSampler


class DummyWay:
    def __init__(self, way_id, geometry, tags):
        self.id = way_id
        self.geometry = geometry
        self.tags = tags


def test_sampler_collects_man_made_tower():
    way = DummyWay(
        way_id=1,
        geometry=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
        tags={"man_made": "tower"},
    )

    landmarks = AtlasTowerSampler.sample([way])

    assert len(landmarks) == 1

    landmark = landmarks[0]
    assert isinstance(landmark, AtlasLandmark)
    assert landmark.landmark_type == AtlasLandmarkType.TOWER
    assert landmark.geometry == way.geometry
    assert landmark.tags["man_made"] == "tower"
