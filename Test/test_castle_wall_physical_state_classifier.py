from CORE.atlas_castle_wall_physical_state_classifier import (
    AtlasCastleWallPhysicalStateClassifier,
)


def test_barrier_city_wall_is_current_physical():
    result = AtlasCastleWallPhysicalStateClassifier.classify(
        {
            "barrier": "city_wall",
            "height": "13-15",
        }
    )

    assert result["state"] == "CURRENT_PHYSICAL"
    assert result["allow_full_wall"] is True
    assert result["allow_crenellations"] is True


def test_ruined_wall_is_classified_as_remains():
    result = AtlasCastleWallPhysicalStateClassifier.classify(
        {
            "historic": "castle_wall",
            "ruins": "yes",
        }
    )

    assert result["state"] == "RUIN_OR_REMAINS"
    assert result["allow_full_wall"] is False
    assert result["allow_low_remains"] is True
    assert result["allow_crenellations"] is False


def test_demolished_wall_is_historical_only():
    result = AtlasCastleWallPhysicalStateClassifier.classify(
        {
            "demolished:historic": "castle_wall",
        }
    )

    assert result["state"] == "HISTORICAL_ONLY"
    assert result["allow_full_wall"] is False
    assert result["allow_low_remains"] is False
    assert result["allow_crenellations"] is False


def test_historic_castle_wall_without_physical_evidence_is_uncertain():
    result = AtlasCastleWallPhysicalStateClassifier.classify(
        {
            "historic": "castle_wall",
        }
    )

    assert result["state"] == "UNCERTAIN"
    assert result["allow_full_wall"] is False
    assert result["allow_low_remains"] is True
    assert result["allow_crenellations"] is False


def test_castle_relation_boundary_without_wall_evidence_is_not_physical():
    result = AtlasCastleWallPhysicalStateClassifier.classify(
        {
            "historic": "castle",
            "building": "museum",
            "source": "castle_relation",
            "relation_role": "outer",
        }
    )

    assert result["state"] == "HISTORICAL_ONLY"
    assert result["allow_full_wall"] is False
    assert result["allow_low_remains"] is False
    assert result["allow_crenellations"] is False


def test_numeric_height_range_is_parsed():
    result = AtlasCastleWallPhysicalStateClassifier.classify(
        {
            "barrier": "city_wall",
            "height": "13-15",
        }
    )

    assert result["height_min_m"] == 13.0
    assert result["height_max_m"] == 15.0
    assert result["height_representative_m"] == 14.0


def test_single_numeric_height_is_parsed():
    result = AtlasCastleWallPhysicalStateClassifier.classify(
        {
            "barrier": "wall",
            "height": "8.5 m",
        }
    )

    assert result["height_min_m"] == 8.5
    assert result["height_max_m"] == 8.5
    assert result["height_representative_m"] == 8.5
