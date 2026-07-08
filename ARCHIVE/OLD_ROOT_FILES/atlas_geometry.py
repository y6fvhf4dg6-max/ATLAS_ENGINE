"""
ATLAS Geometry Engine v0.3

Görev:
- OSM polygonlarını okumak
- Polygon geçerliliğini kontrol etmek
- Node ID listesini gerçek koordinatlara çevirmek
"""


def is_valid_polygon(nodes):
    if len(nodes) < 4:
        return False

    if nodes[0] != nodes[-1]:
        return False

    return True


def polygon_info(nodes):
    print("Polygon oluşturuluyor...")
    print("Toplam node:", len(nodes))

    if is_valid_polygon(nodes):
        print("Polygon durumu: GEÇERLİ ve KAPALI")
        return True

    print("Polygon durumu: GEÇERSİZ")
    return False


def build_node_lookup(osm_data):
    node_lookup = {}

    for element in osm_data["elements"]:
        if element["type"] == "node":
            node_lookup[element["id"]] = {
                "lat": element["lat"],
                "lon": element["lon"],
            }

    return node_lookup


def resolve_node_coordinates(node_ids, node_lookup):
    coordinates = []

    for node_id in node_ids:
        if node_id in node_lookup:
            node = node_lookup[node_id]
            coordinates.append((node["lat"], node["lon"]))

    return coordinates


if __name__ == "__main__":
    sample_osm_data = {
        "elements": [
            {"type": "node", "id": 1, "lat": 50.1, "lon": 8.6},
            {"type": "node", "id": 2, "lat": 50.2, "lon": 8.7},
            {"type": "node", "id": 3, "lat": 50.3, "lon": 8.8},
        ]
    }

    sample_node_ids = [1, 2, 3, 1]

    lookup = build_node_lookup(sample_osm_data)
    coords = resolve_node_coordinates(sample_node_ids, lookup)

    print("Node lookup sayısı:", len(lookup))
    print("Koordinatlar:", coords)