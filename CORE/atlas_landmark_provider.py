from abc import ABC, abstractmethod


class AtlasLandmarkProvider(ABC):
    @classmethod
    @abstractmethod
    def from_source(cls, source):
        raise NotImplementedError
