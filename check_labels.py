"""
Scan a dataset directory and report images missing YOLO labels.
"""
from pathlib import Path

DATASET_DIR = Path("datasets")
IMG_EXT = {".jpg", ".jpeg", ".png"}

def main():
    images = []
    for p in DATASET_DIR.rglob("*"):
        if p.suffix.lower() in IMG_EXT and "images" in p.parts:
            images.append(p)

    missing = []
    for img in images:
        lbl = img.parent.parent / "labels" / img.name.replace(img.suffix, ".txt")
        if not lbl.exists():
            missing.append(str(img))

    print("Total images:", len(images))
    print("Images missing labels:", len(missing))
    for m in missing[:100]:
        print("MISSING:", m)
    if len(missing) > 100:
        print(f"...and {len(missing)-100} more")

if __name__ == "__main__":
    main()
