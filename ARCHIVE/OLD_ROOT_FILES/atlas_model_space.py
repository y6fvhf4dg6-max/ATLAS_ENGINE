"""
ATLAS Engine

Module : Model Space Engine
Version: 0.1
Status : Development

Purpose:
Converts real geographic coordinates into printable model-space points.
"""

from atlas_projection import project_to_model


def coordinates_to_model_points(coordinates, bounds, model_size):
    model_points = []

    for lat, lon in coordinates:
        x, y = project_to_model(
            lat,
            lon,
            bounds,
            model_size
        )

        model_points.append((x, y))

    return model_points


if __name__ == "__main__":
    sample_coordinates = [
        (50.1107812, 8.6852076),
        (50.1107000, 8.6849000),
        (50.1105000, 8.6847000),
        (50.1107812, 8.6852076),
    ]

    sample_bounds = {
        "north": 50.11271417793748,
        "south": 50.10822262206253,
        "east": 8.685160563140817,
        "west": 8.678156836859182,
    }

    points = coordinates_to_model_points(
        sample_coordinates,
        sample_bounds,
        200
    )

    print("Model nokta sayısı:", len(points))
    print("İlk model noktası:", points[0])
    print("Tüm noktalar:", points)