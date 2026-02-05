"""
Model loading, image/video inference, hydration scoring, and API helpers.
"""
import io, json, time, datetime as dt
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
from PIL import Image
import cv2

from config import YOLO_WEIGHTS, IMG_SIZE, INFERENCE_CONF, INFERENCE_IOU, HYDRATION_SCORES_CSV, CLASS_NAMES
from schedule_manager import start_watering, stop_watering, get_status

_YOLO = None
_YOLO_ERROR = None

def _load_yolo():
    global _YOLO, _YOLO_ERROR
    if _YOLO is not None or _YOLO_ERROR:
        return _YOLO
    try:
        from ultralytics import YOLO
        _YOLO = YOLO(YOLO_WEIGHTS)
        print("[hydration] YOLO loaded:", YOLO_WEIGHTS)
    except Exception as e:
        _YOLO_ERROR = e
        print("[hydration] YOLO load failed -> HSV fallback:", repr(e))
    return _YOLO

def _infer_with_hsv(img_bgr: np.ndarray) -> Dict[str, Any]:
    """Simple green-coverage fallback when YOLO isn't available."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    # Broad green range; tune as needed
    lower = np.array([25, 40, 40]); upper = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    pct_green = float(mask.mean()) / 255.0  # 0..1
    # Fake detections in the same shape Ultralytics would give
    return {"detections": [{"cls": "grass", "conf": pct_green, "xyxy": [0,0,0,0]}]}

def _parse_yolo_results(results) -> List[Dict[str, Any]]:
    parsed = []
    for r in results:
        if not hasattr(r, "boxes") or r.boxes is None:
            continue
        names = r.names
        for b in r.boxes:
            cls_id = int(b.cls.cpu().item())
            conf = float(b.conf.cpu().item())
            xyxy = b.xyxy[0].cpu().tolist()
            parsed.append({"cls": names.get(cls_id, str(cls_id)), "conf": conf, "xyxy": xyxy})
    return parsed

def run_inference_on_image(img_bgr: np.ndarray) -> Dict[str, Any]:
    mdl = _load_yolo()
    if mdl is None:
        det = _infer_with_hsv(img_bgr)
    else:
        r = mdl.predict(img_bgr[..., ::-1], imgsz=IMG_SIZE, conf=INFERENCE_CONF, iou=INFERENCE_IOU, verbose=False)
        det = {"detections": _parse_yolo_results(r)}
    return _score_hydration(det)

def _score_hydration(det: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert detections into your 0–10 inverted 'hydration need' score.
    0 = very dry (needs more time), 5 = optimal, 10 = oversaturated (skip).
    Simple heuristic you can tune with real data.
    """
    counts = {k: 0 for k in CLASS_NAMES}
    for d in det["detections"]:
        k = d["cls"]
        if k in counts:
            counts[k] += 1

    # Heuristic
    grass = counts["grass"]
    dead = counts["dead_grass"]
    water = counts["water"] + counts.get("standing_water", 0) + counts.get("mushy_grass", 0) + counts.get("mud", 0)

    score = 5.0
    score -= min(dead * 0.5, 5.0)      # more dead grass → needs water (lower score)
    score += min(water * 0.7, 5.0)     # more water/mud → oversaturated (higher score)
    score = float(np.clip(score, 0, 10))

    out = {"counts": counts, "score": score, "timestamp": dt.datetime.now().isoformat(timespec="seconds")}
    _append_hydration_score(out)
    return out

def _append_hydration_score(row: Dict[str, Any]):
    header = ["timestamp", "score"] + CLASS_NAMES
    path = Path(HYDRATION_SCORES_CSV)
    exists = path.exists()
    with path.open("a", encoding="utf-8") as f:
        if not exists:
            f.write(",".join(header) + "\n")
        vals = [row["timestamp"], f'{row["score"]:.3f}'] + [str(row["counts"].get(c, 0)) for c in CLASS_NAMES]
        f.write(",".join(vals) + "\n")

def infer_file(file_bytes: bytes) -> Dict[str, Any]:
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return run_inference_on_image(img_bgr)
