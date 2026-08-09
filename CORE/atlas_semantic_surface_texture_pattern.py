import math


class AtlasSemanticSurfaceTexturePattern:
    SUPPORTED_TEXTURE_LANGUAGES = {
        "paving",
        "lawn",
        "grass",
        "ordered_ground",
        "field",
    }

    def __init__(
        self,
        *,
        texture_language,
        relief_depth_mm,
        feature_pitch_mm,
    ):
        if (
            texture_language
            not in self.SUPPORTED_TEXTURE_LANGUAGES
        ):
            raise ValueError(
                "unsupported texture_language"
            )

        self.texture_language = texture_language
        self.relief_depth_mm = float(
            relief_depth_mm
        )
        self.feature_pitch_mm = float(
            feature_pitch_mm
        )

        if (
            not math.isfinite(self.relief_depth_mm)
            or self.relief_depth_mm <= 0.0
        ):
            raise ValueError(
                "relief_depth_mm must be positive"
            )

        if (
            not math.isfinite(self.feature_pitch_mm)
            or self.feature_pitch_mm <= 0.0
        ):
            raise ValueError(
                "feature_pitch_mm must be positive"
            )

    def offset_at(
        self,
        x,
        y,
    ):
        x = float(x)
        y = float(y)

        if self.texture_language == "paving":
            return self._paving_offset(
                x=x,
                y=y,
            )

        if self.texture_language == "lawn":
            return self._lawn_offset(
                x=x,
                y=y,
            )

        if self.texture_language == "grass":
            return self._grass_offset(
                x=x,
                y=y,
            )

        if self.texture_language == "ordered_ground":
            return self._ordered_ground_offset(
                x=x,
                y=y,
            )

        if self.texture_language == "field":
            return self._field_offset(
                x=x,
                y=y,
            )

        raise ValueError(
            "unsupported texture_language"
        )

    def _lawn_offset(
        self,
        *,
        x,
        y,
    ):
        phase = (
            2.0
            * math.pi
            * (
                x * 0.72
                + y * 0.28
            )
            / self.feature_pitch_mm
        )

        normalized = (
            math.sin(phase) + 1.0
        ) / 2.0

        return (
            self.relief_depth_mm
            * normalized
        )

    def _grass_offset(
        self,
        *,
        x,
        y,
    ):
        phase_x = (
            2.0
            * math.pi
            * x
            / self.feature_pitch_mm
        )

        phase_y = (
            2.0
            * math.pi
            * y
            / (
                self.feature_pitch_mm
                * 0.72
            )
        )

        combined = (
            0.60 * math.sin(phase_x)
            + 0.40 * math.sin(phase_y)
        )

        normalized = (
            combined + 1.0
        ) / 2.0

        return (
            self.relief_depth_mm
            * normalized
        )

    def _ordered_ground_offset(
        self,
        *,
        x,
        y,
    ):
        phase = (
            2.0
            * math.pi
            * x
            / self.feature_pitch_mm
        )

        secondary_phase = (
            2.0
            * math.pi
            * y
            / (
                self.feature_pitch_mm
                * 2.0
            )
        )

        combined = (
            0.80 * math.sin(phase)
            + 0.20 * math.sin(secondary_phase)
        )

        normalized = (
            combined + 1.0
        ) / 2.0

        return (
            self.relief_depth_mm
            * normalized
        )

    def _field_offset(
        self,
        *,
        x,
        y,
    ):
        phase = (
            2.0
            * math.pi
            * (
                x + 0.15 * y
            )
            / self.feature_pitch_mm
        )

        normalized = (
            math.sin(phase) + 1.0
        ) / 2.0

        return (
            self.relief_depth_mm
            * normalized
        )

    def _paving_offset(
        self,
        *,
        x,
        y,
    ):
        phase_x = (
            2.0
            * math.pi
            * x
            / self.feature_pitch_mm
        )

        phase_y = (
            2.0
            * math.pi
            * y
            / self.feature_pitch_mm
        )

        pattern = (
            math.sin(phase_x)
            * math.sin(phase_y)
        )

        normalized_pattern = (
            pattern + 1.0
        ) / 2.0

        return (
            self.relief_depth_mm
            * normalized_pattern
        )
