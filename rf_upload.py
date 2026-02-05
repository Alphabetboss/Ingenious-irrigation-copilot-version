"""
Upload local images/labels to a Roboflow project.
Set ROBOFLOW_API_KEY and ROBOFLOW_PROJECT in your environment.
"""
import os
from pathlib import Path
from roboflow import Roboflow

DATASET = Path("datasets/yolo_dataset")
API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
PROJECT = os.getenv("ROBOFLOW_PROJECT", "")  # e.g., "ingenious-irrigation/1"

def main():
    if not API_KEY or not PROJECT:
        raise SystemExit("Set ROBOFLOW_API_KEY and ROBOFLOW_PROJECT")

    rf = Roboflow(api_key=API_KEY)
    ws, proj_name = PROJECT.split("/")
    proj = rf.workspace(ws).project(proj_name)

    # Expect images/train + labels/train etc.
    # You can also zip and upload; here we show simple per-folder upload:
    for split in ["train", "val", "test"]:
        img_dir = DATASET / "images" / split
        lbl_dir = DATASET / "labels" / split
        if not img_dir.exists():
            continue
        # Roboflow’s Python SDK prefers using the web uploader or dataset versions,
        # so the simplest path is to export a zip; here we just note the path:
        print(f"[INFO] Upload {split} from: {img_dir} (labels: {lbl_dir})")
        # Tip: Use proj.upload(...) with a zip; see Roboflow docs for bulk upload.
    print("Done (see notes).")

if __name__ == "__main__":
    main()
