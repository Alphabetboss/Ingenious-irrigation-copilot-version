from pathlib import Path

def list_images(path="dataset"):
    return [str(p) for p in Path(path).rglob("*.jpg")]
