"""
ATLAS Terrain Surface Texture v0.1

Düz ürün yüzeyine çok düşük genlikli, geniş dalga boylu
mikro-topografya ofseti sağlar.

Bu modül mesh üretmez ve terrain geometrisini doğrudan değiştirmez.
Yalnız belirli bir XY noktası için kontrollü Z ofseti hesaplar.
"""

import math


class AtlasTerrainSurfaceTexture:
    MIN_POSITIVE_VALUE = 1e-9

    def __init__(
        self,
        *,
        size_x_mm,
        size_y_mm,
        amplitude_mm=0.16,
        wavelength_x_mm=28.0,
        wavelength_y_mm=37.0,
        edge_fade_mm=8.0,
        phase_y_radians=0.8,
    ):
        self.size_x_mm = self._positive_float(
            size_x_mm,
            "size_x_mm",
        )
        self.size_y_mm = self._positive_float(
            size_y_mm,
            "size_y_mm",
        )
        self.amplitude_mm = self._non_negative_float(
            amplitude_mm,
            "amplitude_mm",
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
        self.phase_y_radians = float(
            phase_y_radians
        )

    def offset_at(self, x, y):
        x = float(x)
        y = float(y)

        if self.amplitude_mm <= 0.0:
            return 0.0

        fade = self._edge_fade_factor(
            x=x,
            y=y,
        )

        if fade <= 0.0:
            return 0.0

        wave_x = math.sin(
            2.0
            * math.pi
            * x
            / self.wavelength_x_mm
        )
        wave_y = math.sin(
            (
                2.0
                * math.pi
                * y
                / self.wavelength_y_mm
            )
            + self.phase_y_radians
        )

        # İki dalganın ortalaması kullanılır.
        # Böylece birleşik değer her zaman [-1, +1]
        # aralığında kalır ve amplitude_mm aşılmaz.
        normalized_wave = (
            wave_x + wave_y
        ) / 2.0

        return (
            self.amplitude_mm
            * normalized_wave
            * fade
        )

    def _edge_fade_factor(self, *, x, y):
        if (
            x <= 0.0
            or x >= self.size_x_mm
            or y <= 0.0
            or y >= self.size_y_mm
        ):
            return 0.0

        if self.edge_fade_mm <= 0.0:
            return 1.0

        edge_distance = min(
            x,
            self.size_x_mm - x,
            y,
            self.size_y_mm - y,
        )

        if edge_distance <= 0.0:
            return 0.0

        linear_factor = min(
            edge_distance / self.edge_fade_mm,
            1.0,
        )

        # Smoothstep:
        # Kenarda türev sıfıra yaklaşır; ani kırık oluşmaz.
        return (
            linear_factor
            * linear_factor
            * (3.0 - 2.0 * linear_factor)
        )

    @staticmethod
    def _positive_float(value, name):
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be a positive number"
            ) from exc

        if (
            not math.isfinite(parsed)
            or parsed
            <= AtlasTerrainSurfaceTexture
            .MIN_POSITIVE_VALUE
        ):
            raise ValueError(
                f"{name} must be a positive number"
            )

        return parsed

    @staticmethod
    def _non_negative_float(value, name):
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be a non-negative number"
            ) from exc

        if (
            not math.isfinite(parsed)
            or parsed < 0.0
        ):
            raise ValueError(
                f"{name} must be a non-negative number"
            )

        return parsed
