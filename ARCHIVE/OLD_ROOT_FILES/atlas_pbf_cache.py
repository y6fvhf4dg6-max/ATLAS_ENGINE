"""
ATLAS PBF CACHE

Local PBF dosyasını bir kez okur.
Buildings, roads ve water verisini RAM'de tutar.
"""

from atlas_local_osm import read_local_osm_bbox


class AtlasPBFCache:

    def __init__(self):
        self.loaded = False
        self.pbf_path = None
        self.bbox = None
        self.buildings = []
        self.roads = []
        self.water = []

    def load(self, pbf_path, bbox):
        if self.loaded and self.pbf_path == pbf_path and self.bbox == bbox:
            print("PBF cache kullanılıyor.")
            return

        self.buildings, self.roads, self.water = read_local_osm_bbox(
            bbox,
            pbf_path
        )

        self.pbf_path = pbf_path
        self.bbox = bbox
        self.loaded = True

        print("PBF cache yüklendi.")
        print("Cache bina sayısı:", len(self.buildings))
        print("Cache yol sayısı:", len(self.roads))
        print("Cache su sayısı:", len(self.water))