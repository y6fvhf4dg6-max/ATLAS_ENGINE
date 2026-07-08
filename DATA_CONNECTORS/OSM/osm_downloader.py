"""
ATLAS Engine

OSM Downloader v1.0
"""

import requests


class OSMDownloader:

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def download_buildings(self, bbox):

        south, west, north, east = bbox

        query = f"""
        [out:json][timeout:120];

        (
          way["building"]({south},{west},{north},{east});
          relation["building"]({south},{west},{north},{east});
        );

        out body;
        >;
        out skel qt;
        """

        print("Downloading OSM buildings...")
        print()

        response = requests.post(
            self.OVERPASS_URL,
            data={"data": query},
            headers={"User-Agent": "ATLAS-Engine/1.0"},
            timeout=180,
        )

        response.raise_for_status()

        data = response.json()

        print(f"Downloaded {len(data['elements'])} OSM elements.")

        return data
