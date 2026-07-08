import time
import requests


def get_elevation(latitude, longitude):
    url = "https://api.opentopodata.org/v1/srtm90m"
    params = {"locations": f"{latitude},{longitude}"}

    response = requests.get(url, params=params)

    if response.status_code == 429:
        raise Exception("API sınırı: Çok fazla istek. Biraz beklemek gerekiyor.")

    response.raise_for_status()

    data = response.json()
    return data["results"][0]["elevation"]


def fetch_elevations_in_batches(locations, batch_size=50, max_retries=3, wait_seconds=10):
    url = "https://api.opentopodata.org/v1/srtm90m"
    elevations = []

    for start in range(0, len(locations), batch_size):
        batch = locations[start:start + batch_size]
        params = {"locations": "|".join(batch)}

        for attempt in range(1, max_retries + 1):
            response = requests.get(url, params=params)

            if response.status_code == 429:
                print(f"API sınırı geldi. {wait_seconds} saniye bekleniyor... Deneme {attempt}/{max_retries}")
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            data = response.json()

            for result in data["results"]:
                elevations.append(result["elevation"])

            break
        else:
            raise Exception("DEM verisi alınamadı. API sınırı devam ediyor.")

        time.sleep(1)

    return elevations


def get_dem_grid(center_latitude, center_longitude, grid_size=16, step=0.001):
    locations = []

    for row in range(grid_size):
        for col in range(grid_size):
            latitude = center_latitude + (row - grid_size / 2) * step
            longitude = center_longitude + (col - grid_size / 2) * step
            locations.append(f"{latitude},{longitude}")

    elevations = fetch_elevations_in_batches(locations, batch_size=50)

    dem_grid = []
    index = 0

    for row in range(grid_size):
        row_values = []

        for col in range(grid_size):
            row_values.append(elevations[index])
            index += 1

        dem_grid.append(row_values)

    return dem_grid


if __name__ == "__main__":
    test_latitude = 50.1104684
    test_longitude = 8.6816587

    grid = get_dem_grid(test_latitude, test_longitude, grid_size=16)

    print("DEM matrisi oluşturuldu.")
    print("Satır sayısı:", len(grid))
    print("Sütun sayısı:", len(grid[0]))
    print("İlk satır:", grid[0])