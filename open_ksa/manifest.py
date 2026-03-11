import json
import os
from typing import Any

from .models import to_plain_data


def write_manifest(manifest: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(to_plain_data(manifest), fh, ensure_ascii=False, indent=2)
