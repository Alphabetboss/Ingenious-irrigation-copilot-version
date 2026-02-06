"""
Inference engine for plant/zone visual analysis.

Responsibilities:
- Load YOLO (or any object detection model) once at startup
- Run inference on images (file path or bytes)
- Return structured detections for downstream logic
"""

from pathlib import Path
from typing import List, Optional, Union
import io

from pydantic import BaseModel

# If you’re using ultralytics YOLO, uncomment this and install `ultralytics`
# from ultralytics import YOLO


class Detection(BaseModel):
    label: str
    confidence: float
    x_min: int
    y_min: int
    x_max: int
    y_max: int


class InferenceResult(BaseModel):
    model_name: str
    detections: List[Detection]


class InferenceEngine:
    def __init__(
        self,
        model_path: Union[str, Path],
        confidence_threshold: float = 0.3,
        device: str = "cpu",
    ) -> None:
        self.model_path = str(model_path)
        self.confidence_threshold = confidence_threshold
        self.device = device

        # Lazy-loaded model
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return

        # Example with YOLO; adapt if you use another framework
        # self._model = YOLO(self.model_path)
        # self._model.to(self.device)

        # Placeholder so the rest of the app doesn’t break if model isn’t wired yet
        self._model = "DUMMY_MODEL"

    @property
    def model_name(self) -> str:
        return Path(self.model_path).name

    def _run_dummy_inference(self) -> List[Detection]:
        # Safe fallback for now; replace with real model logic
        return [
            Detection(
                label="plant",
                confidence=0.85,
                x_min=100,
                y_min=120,
                x_max=220,
                y_max=260,
            )
        ]

    def run_on_bytes(self, image_bytes: bytes) -> InferenceResult:
        """
        Run inference on raw image bytes.
        """
        self._load_model()

        # If using real YOLO:
        # img = io.BytesIO(image_bytes)
        # results = self._model(img)
        # detections = self._parse_yolo_results(results)

        detections = self._run_dummy_inference()

        return InferenceResult(
            model_name=self.model_name,
            detections=detections,
        )

    def run_on_path(self, image_path: Union[str, Path]) -> InferenceResult:
        """
        Run inference on an image file path.
        """
        self._load_model()

        # If using real YOLO:
        # results = self._model(str(image_path))
        # detections = self._parse_yolo_results(results)

        detections = self._run_dummy_inference()

        return InferenceResult(
            model_name=self.model_name,
            detections=detections,
        )

    # Example parser if you wire YOLO:
    # def _parse_yolo_results(self, results) -> List[Detection]:
    #     detections: List[Detection] = []
    #     for r in results:
    #         boxes = r.boxes
    #         for box in boxes:
    #             x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
    #             conf = float(box.conf[0])
    #             cls_id = int(box.cls[0])
    #             label = self._model.names[cls_id]
    #
    #             if conf < self.confidence_threshold:
    #                 continue
    #
    #             detections.append(
    #                 Detection(
    #                     label=label,
    #                     confidence=conf,
    #                     x_min=int(x_min),
    #                     y_min=int(y_min),
    #                     x_max=int(x_max),
    #                     y_max=int(y_max),
    #                 )
    #             )
    #     return detections


# Singleton-style accessor for FastAPI startup wiring
_inference_engine: Optional[InferenceEngine] = None


def get_inference_engine() -> InferenceEngine:
    global _inference_engine
    if _inference_engine is None:
        # Adjust model path to wherever you store weights
        _inference_engine = InferenceEngine(
            model_path="models/plant_yolo.pt",
            confidence_threshold=0.35,
            device="cpu",
        )
    return _inference_engine
