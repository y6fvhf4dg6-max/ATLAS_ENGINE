from CORE.atlas_castle_multi_gable_piece_profile import (
    AtlasCastleMultiGablePieceProfile,
)


def test_liedberg_wings_receive_distinct_roof_height_multipliers():
    assert AtlasCastleMultiGablePieceProfile.roof_height_multiplier(
        source_id=143975871,
        piece_index=0,
    ) == 1.18

    assert AtlasCastleMultiGablePieceProfile.roof_height_multiplier(
        source_id=143975871,
        piece_index=1,
    ) == 0.82

    assert AtlasCastleMultiGablePieceProfile.roof_height_multiplier(
        source_id=143975871,
        piece_index=2,
    ) == 1.0


def test_unrelated_castles_keep_default_roof_height():
    assert AtlasCastleMultiGablePieceProfile.roof_height_multiplier(
        source_id=999,
        piece_index=0,
    ) == 1.0
