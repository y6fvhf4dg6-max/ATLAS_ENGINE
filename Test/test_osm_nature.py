from DATA_CONNECTORS.OSM.osm_nature_downloader import OSMNatureDownloader


def main():
    bbox = (39.9350, 32.8450, 39.9400, 32.8550)

    downloader = OSMNatureDownloader()
    data = downloader.download_trees(bbox)

    print()
    print("=" * 60)
    print("NATURE DOWNLOAD SUCCESS")
    print("=" * 60)
    print("Elements:", len(data.get("elements", [])))

    for element in data.get("elements", [])[:5]:
        print(
            "ID:",
            element.get("id"),
            "| Lat:",
            element.get("lat"),
            "| Lon:",
            element.get("lon"),
            "| Tags:",
            element.get("tags", {}),
        )


if __name__ == "__main__":
    main()
