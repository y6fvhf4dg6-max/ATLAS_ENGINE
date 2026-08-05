import pytest
from dataclasses import FrozenInstanceError

from CORE.atlas_master_landmark_catalog import (
    AtlasMasterLandmarkCatalog,
    AtlasMasterLandmarkCatalogEntry,
)


def test_catalog_entry_is_immutable():
    entry = AtlasMasterLandmarkCatalogEntry(
        key="test-landmark",
        landmark_family="tower",
        wikidata_id="Q123",
        osm_ids=(456,),
        grammar_name=None,
        profile_name="test-profile",
        component_flags=("test-component",),
        geometry_overrides=(),
    )

    with pytest.raises(FrozenInstanceError):
        entry.profile_name = "changed"


@pytest.mark.parametrize(
    ("wikidata_id", "expected_key"),
    (
        ("Q686664", "bonn-muenster"),
        ("Q1788329", "kreuzkirche-bonn"),
        ("Q91274", "galata-tower"),
        ("Q81523", "galata-bridge"),
    ),
)
def test_catalog_resolves_known_landmarks_by_wikidata(
    wikidata_id,
    expected_key,
):
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id=wikidata_id,
    )

    assert entry is not None
    assert entry.key == expected_key
    assert entry.wikidata_id == wikidata_id


def test_catalog_resolves_bonn_muenster_by_osm_id():
    entry = AtlasMasterLandmarkCatalog.resolve(
        osm_id=112526702,
    )

    assert entry is not None
    assert entry.key == "bonn-muenster"
    assert entry.wikidata_id == "Q686664"
    assert 112526702 in entry.osm_ids


def test_catalog_returns_none_for_unknown_identity():
    assert (
        AtlasMasterLandmarkCatalog.resolve(
            wikidata_id="Q999999999",
        )
        is None
    )

    assert (
        AtlasMasterLandmarkCatalog.resolve(
            osm_id=999999999,
        )
        is None
    )


@pytest.mark.parametrize(
    ("wikidata_id", "osm_id"),
    (
        (None, None),
        ("", None),
        ("   ", None),
        (None, ""),
        (None, "not-an-osm-id"),
    ),
)
def test_catalog_handles_missing_or_invalid_identity_safely(
    wikidata_id,
    osm_id,
):
    assert (
        AtlasMasterLandmarkCatalog.resolve(
            wikidata_id=wikidata_id,
            osm_id=osm_id,
        )
        is None
    )


def test_catalog_prefers_matching_wikidata_when_both_ids_are_supplied():
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id="Q686664",
        osm_id=112526702,
    )

    assert entry is not None
    assert entry.key == "bonn-muenster"


def test_catalog_entries_have_unique_wikidata_ids():
    entries = AtlasMasterLandmarkCatalog.entries()

    wikidata_ids = tuple(
        entry.wikidata_id
        for entry in entries
        if entry.wikidata_id is not None
    )

    assert len(wikidata_ids) == len(set(wikidata_ids))


def test_catalog_entries_have_unique_osm_ids():
    entries = AtlasMasterLandmarkCatalog.entries()

    osm_ids = tuple(
        osm_id
        for entry in entries
        for osm_id in entry.osm_ids
    )

    assert len(osm_ids) == len(set(osm_ids))


def test_bonn_muenster_catalog_contract():
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id="Q686664",
    )

    assert entry.landmark_family == "church"
    assert entry.grammar_name == "bonn_muenster_catalog"
    assert entry.profile_name == "romanesque_cathedral"
    assert "disable_synthetic_apse" in entry.geometry_overrides


def test_kreuzkirche_catalog_contract():
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id="Q1788329",
    )

    assert entry.landmark_family == "church"
    assert entry.grammar_name == "single_west_tower"
    assert entry.profile_name is None


def test_galata_tower_catalog_contract():
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id="Q91274",
    )

    assert entry.landmark_family == "tower"
    assert entry.grammar_name is None
    assert entry.profile_name == "galata"


def test_galata_bridge_catalog_contract():
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id="Q81523",
    )

    assert entry.landmark_family == "bridge"
    assert entry.profile_name == "galata"
    assert "supports" in entry.component_flags
    assert "parapets" in entry.component_flags


def test_cenabi_ahmet_pasha_mosque_catalog_contract():
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id="Q96278624",
        osm_id=322722702,
    )

    assert entry is not None
    assert entry.key == "cenabi-ahmet-pasha-mosque"
    assert entry.landmark_family == "mosque"
    assert entry.wikidata_id == "Q96278624"
    assert entry.osm_ids == (322722702,)
    assert entry.grammar_name == (
        "single_dome_single_minaret"
    )

def test_kilic_ali_pasha_mosque_catalog_contract():
    entry = AtlasMasterLandmarkCatalog.resolve(
        wikidata_id="Q862848",
        osm_id=165574748,
    )

    assert entry is not None
    assert entry.key == "kilic-ali-pasha-mosque"
    assert entry.landmark_family == "mosque"
    assert entry.wikidata_id == "Q862848"
    assert entry.osm_ids == (165574748,)
    assert entry.grammar_name == (
        "single_dome_single_minaret"
    )

