import os
from typing import Any, Dict, List, Optional

import numpy as np

from core.app_context import AppContext


class InferenceEngine:
    """
    Vision inference engine for Ingenious Irrigation.

    - Wraps YOLO (Ultralytics) or future ONNX models
    - Accepts BGR numpy frames
    - Returns normalized, structured detections
    """

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.logger = getattr(self.ctx, "logger", None)

        self.runtime: str = ctx.get("ai", "runtime", default="yolo")
        self.models_cfg: Dict[str, Any] = ctx.get("ai", "models", default={})
        self.vision_model_path: Optional[str] = self.models_cfg.get("vision_health_model")

        self.model = None
        self.class_map: Dict[int, str] = self.models_cfg.get(
            "class_map",
            {
                0: "grass_green",
                1: "grass_dry",
                2: "grass_dead",
                3: "water_pooling",
                4: "mud",
            },
        )

        self._load_model()

    def _log(self, level: str, msg: str, *args):
        if self.logger:
            getattr(self.logger, level)(msg, *args)

    def _load_model(self):
        if not self.vision_model_path or not os.path.exists(self.vision_model_path):
            self._log(
                "warning",
                "Vision model path not found (%s). Running in stub mode.",
                self.vision_model_path,
            )
            self.model = None
            return

        if self.runtime == "yolo":
            try:
                from ultralytics import YOLO  # type: ignore[import]

                self.model = YOLO(self.vision_model_path)
                self._log("info", "Loaded YOLO model from %s", self.vision_model_path)
            except Exception as e:
                self._log(
                    "exception",
                    "Failed to load YOLO model; falling back to stub mode: %s",
                    e,
                )
                self.model = None
        else:
            # Placeholder for ONNX or other runtimes
            self._log(
                "warning",
                "Runtime '%s' not implemented yet. Using stub mode.",
                self.runtime,
            )
            self.model = None

    def is_stub(self) -> bool:
        return self.model is None

    def run_on_frame(self, frame_bgr: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run inference on a BGR frame.

        Returns:
            List of detections:
            [
                {
                    "class_id": int,
                    "class_name": str,
                    "confidence": float,
                    "box": [x1, y1, x2, y2],
                },
                ...
            ]
        """
        if self.model is None:
            return self._stub_detections()

        try:
            results = self.model(frame_bgr, imgsz=640)
            detections: List[Dict[str, Any]] = []

            for r in results:
                boxes = getattr(r, "boxes", None)
                if boxes is None:
                    continue

                for b in boxes:
                    cls_id = int(b.cls[0])
                    conf = float(b.conf[0])
                    xyxy = b.xyxy[0].tolist()
                    class_name = self.class_map.get(cls_id, f"class_{cls_id}")

                    detections.append(
                        {
                            "class_id": cls_id,
                            "class_name": class_name,
                            "confidence": conf,
                            "box": xyxy,
                        }
                    )

            self._log(
                "info",
                "Inference produced %s detections (stub=%s)",
                len(detections),
                self.is_stub(),
            )
            return detections

        except Exception as e:
            self._log("exception", "Vision inference failed: %s", e)
            return []

    def _stub_detections(self) -> List[Dict[str, Any]]:
        """
        Fallback heuristic when no model is available.
        Pretends we see mostly healthy grass with a hint of dryness.
        """
        self._log("info", "Using stub detections (no vision model loaded).")
        return [
            {
                "class_id": 0,
                "class_name": "grass_green",
                "confidence": 0.9,
                "box": [0, 0, 100, 100],
            },
            {
                "class_id": 1,
                "class_name": "grass_dry",
                "confidence": 0.25,
                "box": [120, 80, 220, 180],
            },
        ]
