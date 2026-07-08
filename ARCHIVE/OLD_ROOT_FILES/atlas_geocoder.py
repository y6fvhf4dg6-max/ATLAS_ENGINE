from geopy.geocoders import Nominatim


def geocode_address(address):
    geolocator = Nominatim(user_agent="atlas_engine")
    location = geolocator.geocode(address)

    if location is None:
        raise ValueError("Adres bulunamadı.")

    return location.latitude, location.longitude


if __name__ == "__main__":
    test_address = "Frankfurt Römer"
    latitude, longitude = geocode_address(test_address)

    print("Adres:", test_address)
    print("Enlem :", latitude)
    print("Boylam:", longitude)