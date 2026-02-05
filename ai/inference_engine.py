from ultralytics import YOLO

class InferenceEngine:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def run(self, image):
        results = self.model(image)
        detections = []

        for r in results:
            for box in r.boxes:
                detections.append({
                    "label": r.names[int(box.cls)],
                    "confidence": float(box.conf)
                })

        return detections
