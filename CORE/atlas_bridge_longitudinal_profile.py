from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class AtlasBridgeLongitudinalProfile:
    shore_top_m: float
    center_top_m: float
    approach_ratio: float
    deck_thickness_m: float = 1.0
    full_span_convex: bool = False

    def __post_init__(self):
        shore_top_m = float(self.shore_top_m)
        center_top_m = float(self.center_top_m)
        approach_ratio = float(self.approach_ratio)
        deck_thickness_m = float(self.deck_thickness_m)

        if not 0.0 < approach_ratio < 0.5:
            raise ValueError(
                "approach_ratio must be greater than 0 and less than 0.5"
            )

        if deck_thickness_m <= 0.0:
            raise ValueError(
                "deck_thickness_m must be greater than 0"
            )

        if center_top_m < shore_top_m:
            raise ValueError(
                "center_top_m must be greater than or equal to shore_top_m"
            )

        object.__setattr__(self, "shore_top_m", shore_top_m)
        object.__setattr__(self, "center_top_m", center_top_m)
        object.__setattr__(self, "approach_ratio", approach_ratio)
        object.__setattr__(self, "deck_thickness_m", deck_thickness_m)

    def top_z_at(self, position):
        position = float(position)

        if not 0.0 <= position <= 1.0:
            raise ValueError(
                "position must be inside the unit interval"
            )

        if self.full_span_convex:
            convex_progress = math.sin(
                math.pi * position
            )

            return (
                self.shore_top_m
                + (
                    self.center_top_m
                    - self.shore_top_m
                )
                * convex_progress
            )

        distance_from_end = min(
            position,
            1.0 - position,
        )

        if distance_from_end >= self.approach_ratio:
            return self.center_top_m

        progress = distance_from_end / self.approach_ratio

        smooth_progress = (
            0.5
            - 0.5 * math.cos(math.pi * progress)
        )

        return (
            self.shore_top_m
            + (
                self.center_top_m
                - self.shore_top_m
            )
            * smooth_progress
        )

    def bottom_z_at(self, position):
        return (
            self.top_z_at(position)
            - self.deck_thickness_m
        )
