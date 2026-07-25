from CORE.atlas_tower_builder import AtlasTowerBuilder


class DummyGeometry:
    exterior = (
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 10.0),
        (0.0, 10.0),
    )


class DummyWay:
    id = 1
    geometry = DummyGeometry()
    tags = {
        "man_made": "tower",
        "tower:type": "observation",
        "height": "125",
    }


def test_observation_tower_sets_profile():
    geometry = AtlasTowerBuilder.build(DummyWay())

    assert geometry.profile == "observation"
