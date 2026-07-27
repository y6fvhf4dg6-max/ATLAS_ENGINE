from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasBridgeRoadApproachProfile:
    bridge_top_z: float
    road_top_z: float
    length_mm: float
    deck_thickness_mm: float = 0.80

    def __post_init__(self):
        bridge_top_z = float(self.bridge_top_z)
        road_top_z = float(self.road_top_z)
        length_mm = float(self.length_mm)
        deck_thickness_mm = float(
            self.deck_thickness_mm
        )

        if length_mm <= 0.0:
            raise ValueError(
                "Approach length must be greater than 0"
            )

        if deck_thickness_mm <= 0.0:
            raise ValueError(
                "Deck thickness must be greater than 0"
            )

        object.__setattr__(
            self,
            "bridge_top_z",
            bridge_top_z,
        )
        object.__setattr__(
            self,
            "road_top_z",
            road_top_z,
        )
        object.__setattr__(
            self,
            "length_mm",
            length_mm,
        )
        object.__setattr__(
            self,
            "deck_thickness_mm",
            deck_thickness_mm,
        )

    @staticmethod
    def _clamp_position(position):
        return max(
            0.0,
            min(
                1.0,
                float(position),
            ),
        )

    def top_z_at(self, normalized_position):
        position = self._clamp_position(
            normalized_position
        )

        return (
            self.bridge_top_z
            + (
                self.road_top_z
                - self.bridge_top_z
            )
            * position
        )

    def bottom_z_at(self, normalized_position):
        return (
            self.top_z_at(normalized_position)
            - self.deck_thickness_mm
        )
