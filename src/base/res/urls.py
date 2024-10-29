from hashlib import sha256
from pathlib import Path


class ResourceURLRegisterator:
    def __init__(self) -> None:
        self.registered: dict[Path, str] = {}
        self.registered_reverse: dict[str, Path] = {}

    def register(self, path: Path) -> str:
        if path in self.registered:
            return self.registered[path]

        hashed = sha256(path.read_bytes()).hexdigest()
        url = f"/kagami/file/registered/{hashed}"
        self.registered[path] = url
        self.registered_reverse[hashed] = path

        return url

    def unregister(self, path: Path) -> None:
        if path in self.registered:
            url = self.registered[path]
            del self.registered[path]
            del self.registered_reverse[url]


resource_url_registerator = ResourceURLRegisterator()
