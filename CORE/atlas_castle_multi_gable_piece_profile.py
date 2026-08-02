class AtlasCastleMultiGablePieceProfile:
    DEFAULT_MULTIPLIER = 1.0

    PROFILE_MULTIPLIERS = {
        143975871: {
            0: 1.18,
            1: 0.82,
            2: 1.0,
        },
    }

    @staticmethod
    def roof_height_multiplier(
        *,
        source_id,
        piece_index,
    ):
        try:
            normalized_source_id = int(source_id)
            normalized_piece_index = int(piece_index)
        except (TypeError, ValueError):
            return (
                AtlasCastleMultiGablePieceProfile
                .DEFAULT_MULTIPLIER
            )

        source_profile = (
            AtlasCastleMultiGablePieceProfile
            .PROFILE_MULTIPLIERS
            .get(
                normalized_source_id,
                {},
            )
        )

        return float(
            source_profile.get(
                normalized_piece_index,
                AtlasCastleMultiGablePieceProfile
                .DEFAULT_MULTIPLIER,
            )
        )
