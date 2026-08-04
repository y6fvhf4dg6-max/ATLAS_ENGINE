from __future__ import annotations

import math


class AtlasWaterSurfaceTexture:
    """Su üst yüzeyi için düşük genlikli, kenarda sönen dalga profili."""

    def __init__(
        self,
        *,
        amplitude_mm=None,
        wavelength_x_mm=7.0,
        wavelength_y_mm=11.0,
        edge_fade_mm=1.5,
    ):
        self.amplitude_mm = self._resolve_amplitude(
            amplitude_mm
        )
        self.wavelength_x_mm = self._positive_float(
            wavelength_x_mm,
            "wavelength_x_mm",
        )
        self.wavelength_y_mm = self._positive_float(
            wavelength_y_mm,
            "wavelength_y_mm",
        )
        self.edge_fade_mm = self._non_negative_float(
            edge_fade_mm,
            "edge_fade_mm",
        )

    @property
    def enabled(self):
        return (
            self.amplitude_mm is not None
            and self.amplitude_mm > 0.0
        )

    @staticmethod
    def _resolve_amplitude(value):
        if value is None:
            return None

        try:
            resolved = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "amplitude_mm must be a non-negative number or None"
            ) from error

        if not math.isfinite(resolved) or resolved < 0.0:
            raise ValueError(
                "amplitude_mm must be a non-negative number or None"
            )

        return resolved

    @staticmethod
    def _positive_float(value, field_name):
        try:
            resolved = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{field_name} must be positive"
            ) from error

        if not math.isfinite(resolved) or resolved <= 0.0:
            raise ValueError(
                f"{field_name} must be positive"
            )

        return resolved

    @staticmethod
    def _non_negative_float(value, field_name):
        try:
            resolved = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{field_name} must not be negative"
            ) from error

        if not math.isfinite(resolved) or resolved < 0.0:
            raise ValueError(
                f"{field_name} must not be negative"
            )

        return resolved

    def _edge_factor(self, edge_distance_mm):
        try:
            distance = float(edge_distance_mm)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "edge_distance_mm must not be negative"
            ) from error

        if not math.isfinite(distance) or distance < 0.0:
            raise ValueError(
                "edge_distance_mm must not be negative"
            )

        if self.edge_fade_mm <= 0.0:
            return 1.0

        progress = min(
            1.0,
            distance / self.edge_fade_mm,
        )

        # Smoothstep: sınırda sıfır eğimle başlar ve
        # iç bölgede tam dalga genliğine ulaşır.
        return (
            progress
            * progress
            * (3.0 - 2.0 * progress)
        )

    def offset_at(
        self,
        *,
        x_mm,
        y_mm,
        edge_distance_mm,
    ):
        if not self.enabled:
            return 0.0

        x_mm = float(x_mm)
        y_mm = float(y_mm)

        wave_x = math.sin(
            2.0
            * math.pi
            * x_mm
            / self.wavelength_x_mm
        )
        wave_y = math.sin(
            2.0
            * math.pi
            * y_mm
            / self.wavelength_y_mm
        )

        normalized_wave = (
            wave_x + wave_y
        ) * 0.5

        raised_wave = (
            normalized_wave + 1.0
        ) * 0.5

        return (
            self.amplitude_mm
            * raised_wave
            * self._edge_factor(
                edge_distance_mm
            )
        )
