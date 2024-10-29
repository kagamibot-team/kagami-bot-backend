from abc import ABC, abstractmethod
from pathlib import Path

import PIL
import PIL.Image
from pydantic import BaseModel, computed_field

from .urls import resource_url_registerator


class IResource(ABC, BaseModel):
    @computed_field
    @property
    @abstractmethod
    def path(self) -> Path:
        """资源的路径"""

    @computed_field
    @property
    @abstractmethod
    def url(self) -> str:
        """资源暴露给渲染器的相对 URL"""

    def load_pil_image(self) -> PIL.Image.Image:
        return PIL.Image.open(self.path)


class LocalResource(IResource, BaseModel):
    local_path: Path

    @computed_field
    @property
    def path(self) -> Path:
        return self.local_path

    @computed_field
    @property
    def url(self) -> str:
        return resource_url_registerator.register(self.path)
