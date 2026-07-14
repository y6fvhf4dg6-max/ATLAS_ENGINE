import pytest

from CORE.atlas_castle_wall_builder import (
    AtlasCastleWallBuilder,
)


class FakeCoordinateEngine:
    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m) * 1000.0 / 5500.0


def test_height_range_uses_representative_real_height():
    policy = AtlasCastleWallBuilder._resolve_physical_policy(
        tags={
            "barrier": "city_wall",
            "height": "13-15",
        },
        coordinate_engine=FakeCoordinateEngine(),
    )

    assert policy["state"] == "CURRENT_PHYSICAL"
    assert policy["height_m"] == 14.0
    assert policy["height_mm"] == pytest.approx(
        14.0 * 1000.0 / 5500.0
    )
    assert policy["allow_wall"] is True
    assert policy["allow_crenellations"] is True


def test_current_wall_without_height_uses_default_without_six_mm_clamp():
    policy = AtlasCastleWallBuilder._resolve_physical_policy(
        tags={
            "barrier": "city_wall",
        },
        coordinate_engine=FakeCoordinateEngine(),
    )

    expected_mm = (
        AtlasCastleWallBuilder.DEFAULT_WALL_HEIGHT_M
        * 1000.0
        / 5500.0
    )

    assert policy["height_mm"] == pytest.approx(expected_mm)
    assert policy["height_mm"] < 6.0
    assert policy["allow_wall"] is True


def test_ruin_uses_low_remains_profile_without_crenellations():
    policy = AtlasCastleWallBuilder._resolve_physical_policy(
        tags={
            "historic": "castle_wall",
            "ruins": "yes",
        },
        coordinate_engine=FakeCoordinateEngine(),
    )

    assert policy["state"] == "RUIN_OR_REMAINS"
    assert policy["allow_wall"] is True
    assert policy["allow_crenellations"] is False
    assert policy["height_m"] == (
        AtlasCastleWallBuilder.DEFAULT_REMAINS_HEIGHT_M
    )


def test_uncertain_historic_wall_uses_low_profile():
    policy = AtlasCastleWallBuilder._resolve_physical_policy(
        tags={
            "historic": "castle_wall",
        },
        coordinate_engine=FakeCoordinateEngine(),
    )

    assert policy["state"] == "UNCERTAIN"
    assert policy["allow_wall"] is True
    assert policy["allow_crenellations"] is False
    assert policy["height_m"] == (
        AtlasCastleWallBuilder.DEFAULT_UNCERTAIN_HEIGHT_M
    )


def test_demolished_wall_is_not_allowed():
    policy = AtlasCastleWallBuilder._resolve_physical_policy(
        tags={
            "demolished:historic": "castle_wall",
        },
        coordinate_engine=FakeCoordinateEngine(),
    )

    assert policy["state"] == "HISTORICAL_ONLY"
    assert policy["allow_wall"] is False
    assert policy["allow_crenellations"] is False


def test_relation_boundary_without_physical_evidence_is_not_allowed():
    policy = AtlasCastleWallBuilder._resolve_physical_policy(
        tags={
            "historic": "castle",
            "building": "museum",
            "source": "castle_relation",
            "relation_role": "outer",
        },
        coordinate_engine=FakeCoordinateEngine(),
    )

    assert policy["state"] == "HISTORICAL_ONLY"
    assert policy["allow_wall"] is False
