from types import SimpleNamespace

from CORE.atlas_rock_cut_tomb_builder import (
    AtlasRockCutTombBuilder,
    AtlasRockCutTombGeometry,
)


def test_rock_cut_tomb_builder_preserves_printable_footprint():
    landmark = SimpleNamespace(
        geometry=(
            (-4.0, -1.0),
            (4.0, -1.0),
            (4.0, 1.0),
            (-4.0, 1.0),
        ),
        tags={
            "historic": "tomb",
            "tomb": "rock-cut",
        },
    )

    geometry = AtlasRockCutTombBuilder.build(landmark)

    assert geometry == AtlasRockCutTombGeometry(
        footprint=landmark.geometry,
        height_m=3.0,
    )
