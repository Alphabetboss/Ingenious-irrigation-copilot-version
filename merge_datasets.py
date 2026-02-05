"""
Merge multiple YOLO-format datasets into one unified dataset.
Assumes the standard:
  images/{train,val,test} and labels/{train,val,test}
"""
import shutil, os
from pathlib import Path

INPUTS = [
    Path("datasets/Grass_Detection"),
    Path("datasets/Water_Body_Detection"),
    Path("datasets/Water_Leakage_Detection"),
]
OUTPUT = Path("datasets/yolo_merged")

def copy_tree(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        for f in files:
            sp = Path(root) / f
            rel = sp.relative_to(src)
            dp = dst / rel
            dp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sp, dp)

def main():
    if OUTPUT.exists():
        print("Clearing", OUTPUT)
        shutil.rmtree(OUTPUT)
    for d in INPUTS:
        if d.exists():
            print("Merging:", d)
            copy_tree(d, OUTPUT)
    print("Merged into:", OUTPUT)

if __name__ == "__main__":
    main()
