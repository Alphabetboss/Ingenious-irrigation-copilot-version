"""
Quick local test: run inference on images or a folder and print hydration scores.
Usage:
  python inference_test.py path\to\image.jpg
  python inference_test.py path\to\folder
"""
import sys, os, glob, json
from irrigation_api import infer_file

def _infer_one(p: str):
    with open(p, "rb") as f:
        res = infer_file(f.read())
    print(os.path.basename(p), json.dumps(res, indent=2))

def main():
    if len(sys.argv) < 2:
        print("Provide an image file or folder.")
        sys.exit(1)
    src = sys.argv[1]
    if os.path.isdir(src):
        for img in glob.glob(os.path.join(src, "*.*")):
            if img.lower().endswith((".jpg",".jpeg",".png")):
                _infer_one(img)
    else:
        _infer_one(src)

if __name__ == "__main__":
    main()
