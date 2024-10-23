from abc import ABC, abstractmethod
from pathlib import Path

import PIL
import PIL.Image

from .urls import resource_url_registerator


class IResource(ABC):
    @property
    @abstractmethod
    def path(self) -> Path:
        """资源的路径"""

    @property
    @abstractmethod
    def url(self) -> str:
        """资源暴露给渲染器的相对 URL"""

    def load_pil_image(self) -> PIL.Image.Image:
        return PIL.Image.open(self.path)


class LocalResource(IResource):
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    @property
    def url(self) -> str:
        return resource_url_registerator.register(self.path)
