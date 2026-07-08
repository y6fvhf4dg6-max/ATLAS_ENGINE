"""
ATLAS Projection Engine v0.2

Gerçek dünya koordinatlarını
model koordinatına çevirir.

Kural:
Hiçbir X/Y değeri model sınırlarının dışına çıkamaz.
"""


def project_to_model(lat, lon, bounds, model_size):
    lat_range = bounds["north"] - bounds["south"]
    lon_range = bounds["east"] - bounds["west"]

    x = ((lon - bounds["west"]) / lon_range) * model_size

    y = ((bounds["north"] - lat) / lat_range) * model_size

    # Clamping: koordinatlar model dışına taşamaz
    x = max(0, min(model_size, x))
    y = max(0, min(model_size, y))

    return x, y


if __name__ == "__main__":
    bounds = {
        "north": 50.11271417793748,
        "south": 50.10822262206253,
        "east": 8.685160563140817,
        "west": 8.678156836859182,
    }

    x, y = project_to_model(
        50.1107812,
        8.6852076,
        bounds,
        200
    )

    print("X =", round(x, 2), "mm")
    print("Y =", round(y, 2), "mm")