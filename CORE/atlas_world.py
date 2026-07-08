import json


WORLD_FILE = "atlas_world.json"


def load_world():

    with open(WORLD_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
def get_country(country):

    world = load_world()

    for continent in world.values():

        if country in continent:
            return continent[country]

    return None

def main():

    turkey = get_country("Turkey")

    print(turkey)

    print(get_city_pbf_path(
        "Europe",
        "Turkey",
        "Istanbul"
    ))


def get_city_path(continent, country, city):
    return f"DATA/{continent}/{country}/Cities/{city}"

def get_city_pbf_path(continent, country, city):
    return f"{get_city_path(continent, country, city)}/PBF/{city.lower()}.osm.pbf"

def main():
    turkey = get_country("Turkey")

    print(turkey)

    print(get_city_pbf_path(
        "Europe",
        "Turkey",
        "Istanbul"
    ))


if __name__ == "__main__":
    main()