from CORE.atlas_place_of_worship_profile_resolver import (
    AtlasPlaceOfWorshipProfileResolver,
)


def test_resolves_explicit_church():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "church",
                "religion": "christian",
            }
        )
        == "church"
    )


def test_resolves_explicit_cathedral():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "cathedral",
                "religion": "christian",
            }
        )
        == "cathedral"
    )


def test_resolves_explicit_mosque():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "mosque",
                "amenity": "place_of_worship",
                "religion": "muslim",
            }
        )
        == "mosque"
    )


def test_resolves_explicit_synagogue():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "synagogue",
                "amenity": "place_of_worship",
                "religion": "jewish",
            }
        )
        == "synagogue"
    )


def test_resolves_generic_building_from_supported_religion():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "jewish",
            }
        )
        == "synagogue"
    )


def test_returns_none_for_normal_building():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "apartments",
            }
        )
        is None
    )


def test_conflicting_explicit_building_and_religion_falls_back_to_generic():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "mosque",
                "amenity": "place_of_worship",
                "religion": "christian",
            }
        )
        == "generic_place_of_worship"
    )


def test_generic_building_with_christian_religion_derives_church():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "christian",
            }
        )
        == "church"
    )


def test_generic_building_with_muslim_religion_derives_mosque():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "muslim",
            }
        )
        == "mosque"
    )


def test_generic_building_with_jewish_religion_derives_synagogue():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "jewish",
            }
        )
        == "synagogue"
    )


def test_place_of_worship_without_supported_religion_stays_generic():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "buddhist",
            }
        )
        == "generic_place_of_worship"
    )


def test_religion_without_place_of_worship_does_not_invent_profile():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "religion": "jewish",
            }
        )
        is None
    )


def test_generic_building_with_christian_religion_derives_church():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "christian",
            }
        )
        == "church"
    )


def test_generic_building_with_muslim_religion_derives_mosque():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "muslim",
            }
        )
        == "mosque"
    )


def test_generic_building_with_jewish_religion_derives_synagogue():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "jewish",
            }
        )
        == "synagogue"
    )


def test_place_of_worship_without_supported_religion_stays_generic():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "amenity": "place_of_worship",
                "religion": "buddhist",
            }
        )
        == "generic_place_of_worship"
    )


def test_religion_without_place_of_worship_does_not_invent_profile():
    assert (
        AtlasPlaceOfWorshipProfileResolver.resolve(
            {
                "building": "yes",
                "religion": "jewish",
            }
        )
        is None
    )
