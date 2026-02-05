import cv2
import os

def extract_frames(video_path, output_dir, interval=30):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    frame_id = 0
    saved = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % interval == 0:
            cv2.imwrite(f"{output_dir}/frame_{saved}.jpg", frame)
            saved += 1

        frame_id += 1

    cap.release()
