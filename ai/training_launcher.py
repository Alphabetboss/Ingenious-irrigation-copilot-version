import os

def train(model="yolov8n.pt", data="data.yaml"):
    os.system(f"yolo train model={model} data={data} epochs=100 imgsz=640")
