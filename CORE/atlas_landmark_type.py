from enum import Enum, auto


class AtlasLandmarkType(Enum):
    UNKNOWN = auto()

    MEMORIAL = auto()
    STATUE = auto()
    OBELISK = auto()
    ROCK_CUT_TOMB = auto()

    CLOCK_TOWER = auto()
    TOWER = auto()
    LIGHTHOUSE = auto()
    WATER_TOWER = auto()
    WINDMILL = auto()
    CHIMNEY = auto()

    ARCH = auto()
    BRIDGE = auto()

    CASTLE = auto()
    FORTRESS = auto()

    MOSQUE = auto()
    CHURCH = auto()
    CATHEDRAL = auto()
    SYNAGOGUE = auto()

    STADIUM = auto()
